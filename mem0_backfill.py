#!/usr/bin/env python3
"""
Mem0 Backfill Script für studienkolleg-aachen Projekt.
Liest alle relevanten Projektdateien ein und speichert sie als Memories in Mem0.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Konfiguration
MEM0_API_KEY = "m0-WtAI9fmup6f3C6IdFWzZF4QHNXV2xbNKCjNftBB3"
MEM0_API_URL = "https://api.mem0.ai/v1/memories/"
USER_ID = "CLINEE"
VERSION = "v2"

# Dateien und Verzeichnisse für Backfill
BACKFILL_SOURCES = [
    # Memory-Dokumente
    ("memory/PRD.md", "project_documentation"),
    ("memory/FEHLERREGISTER.md", "error_log"),
    ("memory/GO_LIVE_BLOCKERS.md", "blockers"),
    ("memory/ROLES_MATRIX.md", "roles"),
    ("memory/COMMUNICATION_ARCHITECTURE.md", "communication"),
    
    # Design & Guidelines
    ("design_guidelines.json", "design"),
    
    # Projektplanung
    ("03_projektprofil_und_scope.md", "planning"),
    ("04_projektklassifikation.md", "planning"),
    ("05_zielgruppen_und_funnel.md", "planning"),
    ("06_informationsarchitektur.md", "planning"),
    ("07_ux_workflows.md", "planning"),
    ("08_content_system.md", "planning"),
    ("09_copy_blueprints.md", "planning"),
    ("10_funktions_und_modulmatrix.md", "planning"),
    ("11_rollen_und_rechte_matrix.md", "planning"),
    ("12_datenmodell_und_source_of_truth.md", "planning"),
    ("13_tech_stack_und_systemarchitektur.md", "tech_stack"),
    ("14_tracking_kpis_und_automationen.md", "planning"),
    ("15_security_privacy_compliance.md", "security"),
    ("16_designsystem_ableitung.md", "design"),
    ("17_qa_release_und_abnahme.md", "qa"),
    ("18_umsetzungsroadmap.md", "planning"),
    ("19_backlog_priorisiert.md", "backlog"),
    ("20_ai_agent_handover_master.md", "handover"),
    
    # Wichtige Code-Dateien
    ("backend/config.py", "code_config"),
    ("backend/server.py", "code_main"),
    ("backend/models/schemas.py", "code_schemas"),
    ("frontend/src/App.js", "code_frontend_main"),
    ("frontend/src/contexts/AuthContext.js", "code_auth"),
]

def read_file_content(filepath: str) -> str:
    """Liest den Inhalt einer Datei."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Fehler beim Lesen der Datei {filepath}: {str(e)}"

def create_memory_payload(content: str, category: str, source: str) -> Dict[str, Any]:
    """Erstellt das Payload für die Mem0 API."""
    timestamp = datetime.utcnow().isoformat()
    
    # Kürze den Content, falls zu lang (Mem0 hat Limits)
    if len(content) > 15000:
        content = content[:14000] + "\n\n[Content truncated due to length limits]"
    
    return {
        "messages": [
            {
                "role": "user",
                "content": f"Projektinformation aus {source} (Kategorie: {category}):"
            },
            {
                "role": "assistant",
                "content": content
            }
        ],
        "user_id": USER_ID,
        "version": VERSION,
        "metadata": {
            "category": category,
            "source": source,
            "timestamp": timestamp,
            "project": "studienkolleg-aachen",
            "project_phase": "Phase 3.7"
        }
    }

def send_to_mem0(payload: Dict[str, Any]) -> bool:
    """Sendet einen Memory an die Mem0 API."""
    headers = {
        "Authorization": f"Token {MEM0_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(MEM0_API_URL, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            print(f"✓ Memory gespeichert: {payload['metadata']['source']}")
            return True
        else:
            print(f"✗ Fehler bei {payload['metadata']['source']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Netzwerkfehler bei {payload['metadata']['source']}: {str(e)}")
        return False

def main():
    """Hauptfunktion für den Backfill."""
    print("=" * 60)
    print("Mem0 Backfill für studienkolleg-aachen")
    print("=" * 60)
    
    total_files = len(BACKFILL_SOURCES)
    successful = 0
    failed = 0
    
    for filepath, category in BACKFILL_SOURCES:
        if not os.path.exists(filepath):
            print(f"⚠ Datei nicht gefunden: {filepath}")
            failed += 1
            continue
        
        print(f"\nVerarbeite: {filepath}...")
        content = read_file_content(filepath)
        
        if content.startswith("Fehler beim Lesen"):
            print(f"  ⚠ {content}")
            failed += 1
            continue
        
        payload = create_memory_payload(content, category, filepath)
        if send_to_mem0(payload):
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print("Backfill abgeschlossen!")
    print(f"Erfolgreich: {successful}/{total_files}")
    print(f"Fehlgeschlagen: {failed}/{total_files}")
    
    # Erstelle einen Zusammenfassungs-Memory
    summary_content = f"""
Backfill für studienkolleg-aachen Projekt abgeschlossen.
Gesamt: {total_files} Dateien
Erfolgreich: {successful}
Fehlgeschlagen: {failed}
Datum: {datetime.utcnow().isoformat()}
    
Backfill umfasst:
- Projektplanung & Dokumentation
- Design Guidelines
- Tech Stack & Architektur
- Code-Konfiguration
- Memory-Dokumente
- Backlog & Roadmap
"""
    summary_payload = create_memory_payload(
        summary_content,
        "system",
        "mem0_backfill.py"
    )
    send_to_mem0(summary_payload)
    
    print("\nZusammenfassungs-Memory erstellt.")

if __name__ == "__main__":
    main()