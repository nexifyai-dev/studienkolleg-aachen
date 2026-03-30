# ADR-0007: Migration auf DeepSeek als produktiven KI-Provider

- **Datum:** 2026-03-30
- **Status:** accepted

## Kontext
Historische Providerbasis war nscale/NSCall.

## Problem
Providerkonsistenz und Wartbarkeit waren uneinheitlich.

## Entscheidung
Produktive KI-Aufrufe ausschließlich über `services/deepseek_provider.py`; nscale bleibt nur Kompatibilitäts-Shim.

## Begründung
Einheitliche Provider-Schicht, klarere Auditierbarkeit, geringere Integrationsstreuung.

## Alternativen
Parallelbetrieb mehrerer produktiver Provider (abgelehnt in aktuellem Scope).

## Auswirkungen
Umgebungsvariable `DEEPSEEK_API_KEY` wird zentral relevant.

## Betroffene Dateien/Bereiche
`backend/services/deepseek_provider.py`, `backend/services/nscale_provider.py`, AI-Doku.

## Risiken / Folgeaufgaben
Provider-SLA und Kostenentwicklung beobachten.
