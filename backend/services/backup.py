"""
MongoDB Backup Routine – Automatisiertes Backup ueber mongodump.

Laeuft als Background-Task ueber den Worker-Scheduler.
Backup-Pfad: /app/backups/ (persistent volume)
Retention: 7 Tage
"""
import logging
import os
import subprocess
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

BACKUP_DIR = "/app/backups"
RETENTION_DAYS = 7


async def run_backup():
    """Fuehrt ein vollstaendiges MongoDB-Backup durch."""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")

        mongo_url = os.environ.get("MONGO_URL", "")
        db_name = os.environ.get("DB_NAME", "w2g_platform")

        cmd = ["mongodump", f"--uri={mongo_url}", f"--db={db_name}", f"--out={backup_path}"]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logger.info(f"[BACKUP] Erfolgreich: {backup_path}")
            await _cleanup_old_backups()
            return {"status": "ok", "path": backup_path, "timestamp": timestamp}
        else:
            logger.error(f"[BACKUP] Fehlgeschlagen: {result.stderr[:200]}")
            return {"status": "error", "message": result.stderr[:200]}
    except FileNotFoundError:
        logger.warning("[BACKUP] mongodump nicht installiert – Backup uebersprungen")
        return {"status": "skipped", "message": "mongodump nicht verfuegbar"}
    except Exception as e:
        logger.error(f"[BACKUP] Fehler: {e}")
        return {"status": "error", "message": str(e)}


async def _cleanup_old_backups():
    """Loescht Backups aelter als RETENTION_DAYS."""
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
        for entry in os.listdir(BACKUP_DIR):
            path = os.path.join(BACKUP_DIR, entry)
            if os.path.isdir(path):
                try:
                    ts_str = entry.replace("backup_", "")
                    ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
                    if ts < cutoff:
                        import shutil
                        shutil.rmtree(path)
                        logger.info(f"[BACKUP] Altes Backup geloescht: {entry}")
                except (ValueError, OSError):
                    pass
    except Exception as e:
        logger.warning(f"[BACKUP] Cleanup-Fehler: {e}")
