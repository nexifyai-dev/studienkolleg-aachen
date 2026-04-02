# Auth and RBAC

## Zweck

Diese Seite beschreibt das technische Authentifizierungs- und Berechtigungsmodell der Plattform auf Backend- und Frontend-Ebene.

## Authentifizierungsmodell

Die Plattform verwendet ein cookie-basiertes JWT-Modell.

### Kernprinzipien

- Access Token werden primär aus Cookies gelesen.
- Optional kann ein Bearer-Token aus dem `Authorization`-Header verwendet werden.
- Das Backend validiert JWT-Typ, Signatur und Ablaufzeit.
- Nach Token-Validierung wird der Benutzer aus der Datenbank geladen.
- Deaktivierte Benutzer werden trotz gültigem Token abgewiesen.

## Backend-Enforcement

### `get_current_user`
Die zentrale Dependency für authentifizierte Endpunkte.

Verantwortung:
- Access Token aus Cookie oder Header lesen
- JWT dekodieren
- Token-Typ prüfen
- Benutzerdatensatz laden
- `password_hash` aus Response-Kontext entfernen
- deaktiverte Konten blockieren

### `require_roles(*roles)`
Factory für rollenbasierte Zugriffskontrolle.

Verwendung:
- Endpunkte werden explizit auf bestimmte Rollen eingeschränkt.
- Bei fehlender Berechtigung wird mit `403` abgewiesen.

### `require_self_or_roles(user_id_param, *admin_roles)`
Sonderfall für Ressourcen, bei denen entweder Eigentümerschaft oder privilegierte Rollen Zugriff erhalten.

## Rollegruppen im Backend

Aktuell definierte Gruppen:

- `ADMIN_ROLES = {superadmin, admin}`
- `STAFF_ROLES = {superadmin, admin, staff, accounting_staff}`
- `TEACHING_ROLES = {superadmin, admin, staff, accounting_staff, teacher}`
- `TEACHER_ROLES = {teacher}`
- `PARTNER_ROLES = {agency_admin, agency_agent, affiliate}`
- `ALL_PORTAL_ROLES = {applicant, agency_admin, agency_agent, affiliate}`

## Wichtige Beobachtung

Das Backend-Rollenmodell ist derzeit breiter als das explizite Frontend-Routing. Insbesondere `agency_admin` und `agency_agent` sind serverseitig bereits berücksichtigt. Diese Differenz muss künftig bewusst gepflegt werden, damit UI und API nicht auseinanderlaufen.

## Frontend-Session-Modell

### `AuthContext`
Das Frontend hält den Nutzerzustand zentral in `AuthContext`.

Zuständigkeiten:
- Initialer Auth-Check via `/api/auth/me`
- Login-Flow
- Logout
- User-Refresh
- Synchronisation von `language_pref` mit i18n

### `apiClient`
Der zentrale Axios-Client behandelt Auth-Fehler systemweit.

Verhalten:
- sendet immer Cookies mit `withCredentials: true`
- versucht bei `401` einmalig einen Refresh über `/api/auth/refresh`
- queued parallele Requests während laufendem Refresh
- leitet bei finalem Fehler auf `/auth/login` weiter

### Sicherheitsvorteil
Tokens werden nicht im Browser-Storage persistiert. Das verringert das Risiko klassischer `localStorage`-Tokenprobleme, erhöht aber die Abhängigkeit von korrekt konfigurierten Cookies und HTTPS.

## Routing-Kopplung im Frontend

Die Rollen wirken sich direkt auf die Flächenzuordnung aus:

- interne Rollen → `/staff` oder `/admin`
- `affiliate` → `/partner`
- `applicant` → `/portal`
- `teacher` → `/staff` mit eigenem Dashboard

## Typische RBAC-Muster im Backend

### Ownership-basierter Zugriff
Beispiel: Applicants dürfen nur eigene Applications und Documents sehen.

### Rollenbasierter Zugriff
Beispiel: Updates an Applications oder Document Reviews sind Staff-Rollen vorbehalten.

### Organisationsbasierter Zugriff
Beispiel: Partnerrollen werden auf `organization_id` gescopet.

## Risiken und Drift-Punkte

Diese Seite ist besonders wichtig, weil Auth/RBAC schnell über mehrere Ebenen driftet:

- Rolle im Backend ergänzt, aber Frontend kennt sie nicht
- Frontend leitet Rolle korrekt, Backend erlaubt Endpunkt nicht
- Endpunkt erlaubt Rolle, aber Oberfläche blendet Funktion nicht ein
- Cookie-/Refresh-Verhalten stimmt nicht mit Deploy-Umgebung überein
- SameSite-/Secure-Einstellungen verhindern produktive Sessions

## Prüfregeln bei Änderungen

Bei jeder Änderung an Rollen oder Auth bitte prüfen:

1. Muss `deps.py` angepasst werden?
2. Muss `App.js` bzw. Routing angepasst werden?
3. Muss `AuthContext` oder der Refresh-Flow angepasst werden?
4. Müssen Seed-Accounts oder Testrollen geändert werden?
5. Müssen betroffene Docs-Seiten aktualisiert werden?

## Nächste sinnvolle Vertiefungen

- rollenweise Matrix „wer darf was?“
- Auth-Endpunktdokumentation
- Cookie-/SameSite-/HTTPS-Matrix für lokale, Staging- und Prod-Umgebungen
- Partnerrollen-Differenzierung (`affiliate` vs. `agency_*`)
