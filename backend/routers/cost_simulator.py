"""
Interner Staff-Kosten-Simulator
Feature-Flag: COST_SIMULATOR_ENABLED=true (Standard: false)

WICHTIG:
- Nicht öffentlich zugänglich – nur Staff/Admin
- Keine echten Preise (Preislogik ist [OFFEN])
- Nur zur internen Kalkulation / Planung / Angebotsvorbereitung
- Alle Preisangaben sind PLATZHALTER und nicht freigegeben
- Preise/Kosten sind EINZELFALLABHÄNGIG (Kurswahl, Zeitpunkt, Zusatzleistungen, Partner-/Sub-Agentur-Kontext)
- Keine Veröffentlichung oder Weitergabe als Standardpreise erlaubt
- Sub-Agenturen/Partner: Konditionen ebenfalls individuell
"""
from fastapi import APIRouter, HTTPException, Depends
from deps import require_roles, STAFF_ROLES
from config import COST_SIMULATOR_ENABLED

router = APIRouter(prefix="/api/internal", tags=["internal_staff"])


@router.get("/cost-simulator/config")
async def cost_simulator_config(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """
    Gibt den aktuellen Zustand des Kosten-Simulators zurück.
    Feature-flagged: nur aktiv wenn COST_SIMULATOR_ENABLED=true.
    """
    if not COST_SIMULATOR_ENABLED:
        return {
            "enabled": False,
            "message": "[OFFEN] Kosten-Simulator ist deaktiviert. Preislogik noch nicht final freigegeben. Alle Kosten und Konditionen sind einzelfallabhängig.",
        }
    return {
        "enabled": True,
        "disclaimer": "[OFFEN] Alle Preisangaben sind vorläufige Platzhalter und nicht rechtlich freigegeben. Tatsächliche Kosten sind einzelfallabhängig (Kurswahl, Zeitpunkt, Zusatzleistungen, individuelle Vereinbarung). Für Partner/Sub-Agenturen gelten gesonderte, individuell vereinbarte Konditionen.",
        "courses": [
            {
                "course": "T-Course (Technik)",
                "duration_months": 10,
                "fee_placeholder": "[OFFEN]",
                "language_levels": ["B1", "B2", "C1"],
            },
            {
                "course": "M-Course (Medizin)",
                "duration_months": 10,
                "fee_placeholder": "[OFFEN]",
                "language_levels": ["B1", "B2", "C1"],
            },
            {
                "course": "W-Course (Wirtschaft)",
                "duration_months": 10,
                "fee_placeholder": "[OFFEN]",
                "language_levels": ["B1", "B2", "C1"],
            },
            {
                "course": "Language Course (A1–C1)",
                "duration_months": "1–12 (je Niveau)",
                "fee_per_level_placeholder": "[OFFEN]",
                "language_levels": ["A1", "A2", "B1", "B2", "C1"],
            },
        ],
        "services": [
            {"service": "Visaunterstützung", "fee_placeholder": "[OFFEN]"},
            {"service": "Unterkunftsvermittlung", "fee_placeholder": "[OFFEN]"},
            {"service": "Krankenversicherung", "fee_placeholder": "[OFFEN]"},
            {"service": "Uni-Bewerbungscoaching", "fee_placeholder": "[OFFEN]"},
        ],
        "cancellation_rules": {
            "over_8_weeks": "20% der Kursgebühr, mind. 500 EUR",
            "6_to_8_weeks": "60% der Kursgebühr",
            "under_6_weeks": "100% der Kursgebühr",
            "after_start": "100% der Kursgebühr",
        },
        "visa_refund_admin_fees": {
            "schwerpunktkurse": "500 EUR Verwaltungspauschale",
            "sprachkurs_per_level": "100 EUR je Sprachniveaustufe",
        },
    }
