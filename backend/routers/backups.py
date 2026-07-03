"""
Backup Verwaltung – Admin API.

Endpoints:
  GET    /api/backups                → Liste aller Backups
  POST   /api/backups/run            → Manuelles Backup jetzt starten
  DELETE /api/backups/{name}         → Backup löschen
  POST   /api/backups/{name}/restore → Backup wiederherstellen (mongorestore --drop)
  GET    /api/backups/status         → Backend-Status (Retention, letzter Lauf, Pfad)
"""
import logging
import os
import shutil
import subprocess
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from deps import require_roles, ADMIN_ROLES
from services.backup import BACKUP_DIR, RETENTION_DAYS, run_backup

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/backups", tags=["backups"])


def _list_backups() -> list:
    if not os.path.isdir(BACKUP_DIR):
        return []
    items = []
    for entry in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, entry)
        if not os.path.isdir(path) or not entry.startswith("backup_"):
            continue
        try:
            ts_str = entry.replace("backup_", "")
            ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
            size = 0
            for root, _, files in os.walk(path):
                for f in files:
                    try:
                        size += os.path.getsize(os.path.join(root, f))
                    except OSError:
                        pass
            items.append({
                "name": entry,
                "timestamp": ts.isoformat(),
                "size_bytes": size,
                "size_mb": round(size / (1024 * 1024), 2),
                "path": path,
            })
        except ValueError:
            pass
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return items


@router.get("/status")
async def status(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    backups = _list_backups()
    mongodump_available = shutil.which("mongodump") is not None
    mongorestore_available = shutil.which("mongorestore") is not None
    return {
        "backup_dir": BACKUP_DIR,
        "retention_days": RETENTION_DAYS,
        "count": len(backups),
        "latest": backups[0] if backups else None,
        "mongodump_available": mongodump_available,
        "mongorestore_available": mongorestore_available,
    }


@router.get("")
async def list_backups(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    return {"backups": _list_backups()}


@router.post("/run")
async def create_backup(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    result = await run_backup()
    return result


@router.delete("/{name}")
async def delete_backup(name: str, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    if not name.startswith("backup_"):
        raise HTTPException(status_code=400, detail="Ungültiger Backup-Name")
    path = os.path.join(BACKUP_DIR, name)
    if not os.path.isdir(path):
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    shutil.rmtree(path)
    logger.info(f"[BACKUP] Manuell gelöscht: {name} durch {user.get('email')}")
    return {"status": "deleted", "name": name}


@router.post("/{name}/restore")
async def restore_backup(name: str, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Stellt ein Backup mit --drop wieder her (überschreibt aktuelle DB)."""
    if not name.startswith("backup_"):
        raise HTTPException(status_code=400, detail="Ungültiger Backup-Name")
    path = os.path.join(BACKUP_DIR, name)
    if not os.path.isdir(path):
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    if shutil.which("mongorestore") is None:
        raise HTTPException(status_code=503, detail="mongorestore nicht verfügbar auf diesem System")
    mongo_url = os.environ.get("MONGO_URL", "")
    db_name = os.environ.get("DB_NAME", "w2g_platform")
    db_dump_path = os.path.join(path, db_name)
    if not os.path.isdir(db_dump_path):
        raise HTTPException(status_code=400, detail=f"Backup enthält keine DB '{db_name}'")
    cmd = [
        "mongorestore",
        f"--uri={mongo_url}",
        f"--nsInclude={db_name}.*",
        "--drop",
        db_dump_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            logger.error(f"[BACKUP] Restore fehlgeschlagen: {result.stderr[:400]}")
            raise HTTPException(status_code=500, detail=f"Restore fehlgeschlagen: {result.stderr[:200]}")
        logger.info(f"[BACKUP] Restore erfolgreich: {name} durch {user.get('email')}")
        return {"status": "restored", "name": name, "log_tail": result.stdout[-500:]}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Restore-Timeout nach 600s")
