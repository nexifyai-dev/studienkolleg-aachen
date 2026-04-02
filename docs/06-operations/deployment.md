# Deployment

## Zweck

Diese Seite dokumentiert den aktuellen Deploy-Gedanken der Plattform auf Systemebene. Sie beschreibt, was das Repo heute über Deployment erkennen lässt und welche produktionsrelevanten Voraussetzungen bestehen.

## Aktueller Zustand

Im Repository ist derzeit keine ausdefinierte Infrastruktur- oder Deploy-Pipeline dokumentiert, die als alleinige Source of Truth dienen könnte. Es gibt insbesondere keine klar sichtbaren Docker-, Compose- oder Kubernetes-Manifestdateien im Repo-Root.

Das bedeutet:
- das System ist deploybar, aber die Deploy-Dokumentation ist aktuell eher implizit
- produktionsrelevante Annahmen müssen aus App-Konfiguration, Go-live-Blockern und Laufzeitverhalten abgeleitet werden

## Was das System für Deployment voraussetzt

### Backend
Das Backend ist eine FastAPI-Anwendung mit:
- Startup-/Shutdown-Hooks
- MongoDB-Verbindungsaufbau beim Start
- Index-Erstellung beim Start
- Seed-Schritten beim Start

### Frontend
Das Frontend ist eine React-Anwendung mit separatem Build-/Start-Pfad.

### Datenbank
MongoDB ist Pflichtbestandteil des produktiven Betriebs.

## Betriebsrelevante Deploy-Annahmen

### HTTPS ist nicht optional
Produktive Nutzung setzt HTTPS/TLS voraus, weil Cookie-Sicherheit und Session-Verhalten davon abhängen.

### Cookies hängen am Deploy-Setup
`COOKIE_SECURE`, `COOKIE_SAMESITE`, Origin-Situation und Frontend-/Backend-URLs müssen zum tatsächlichen Hosting-Modell passen.

### Seeds laufen beim Start
Das Backend seedet Workspaces und Admin beim Startup. Daraus folgt:
- Seed-Env muss korrekt gesetzt sein
- Produktions-Passwörter und Seed-Verhalten müssen bewusst gesteuert werden
- Wiederholte Starts dürfen keine unerwarteten Drift-Effekte erzeugen

### Storage ist deploymentkritisch
Für produktionsfähige Dokumentenprozesse muss die Storage-Strategie bewusst gesetzt sein:
- lokal nur bedingt geeignet
- S3/MinIO deutlich näher an Produktionsbetrieb

### E-Mail ist konfigurationsgebunden
E-Mail-Funktionalität ist erst aktiv, wenn die zugehörigen Keys und Absenderkontexte korrekt gesetzt sind.

## Minimale Produktionsvoraussetzungen

Vor echtem Produktionsbetrieb sollten mindestens erfüllt sein:

- MongoDB verfügbar
- `JWT_SECRET` produktionsreif gesetzt
- `ADMIN_PASSWORD` sicher gesetzt und später rotiert
- `FRONTEND_URL` und `APP_URL` korrekt konfiguriert
- HTTPS aktiv
- `COOKIE_SECURE=true`
- Storage-Strategie festgelegt
- Backup-/Restore-Prozess definiert
- E-Mail-Setup geprüft, falls produktiv benötigt

## Laufzeitmodell

Das System deutet auf ein getrenntes Laufzeitmodell hin:

- Frontend als eigene ausgelieferte React-Anwendung
- Backend als eigene API-Laufzeit
- gemeinsame Session- und Origin-Logik über Konfiguration

## Risiken ohne sauber dokumentiertes Deployment

Wenn Deployment nicht explizit dokumentiert ist, entstehen typischerweise Probleme bei:

- Cookies / Session-Stabilität
- Origin-/CORS-Mismatches
- E-Mail-Aktivierung
- Dokumenten-Uploads
- Seed-Verhalten in Produktion
- Wiederanlauf und Wiederherstellung

## Empfohlene nächste Ausbaustufe

Diese Seite sollte später konkretisiert werden um:

- Zielumgebungen (local / staging / production)
- tatsächliche Hosting-Plattform
- Build- und Release-Ablauf
- Secret-Management
- Rollback-/Recovery-Grundregeln
- Monitoring / Logging / Healthchecks

## Dokumentationsregel

Diese Seite sollte aktualisiert werden, wenn:

- eine echte Deploy-Pipeline eingeführt wird
- Hosting-Strategie dokumentiert wird
- Infra-Dateien ins Repo kommen
- Cookie-/Origin-Modell sich ändert
- Startup-/Seed-Verhalten produktiv angepasst wird
