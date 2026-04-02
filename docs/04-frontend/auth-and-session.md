# Frontend Auth and Session

## Zweck

Diese Seite beschreibt die Frontend-seitige Authentifizierungs- und Sitzungslogik der Plattform. Sie ergänzt die backendnahe RBAC-Doku um das tatsächliche Verhalten im Browser.

## Kernkomponenten

Die Frontend-Session wird vor allem durch zwei Bausteine getragen:

- `AuthContext`
- `apiClient`

## `AuthContext`

`AuthContext` ist die zentrale Quelle für den aktuellen Benutzerzustand im Frontend.

Verantwortlichkeiten:
- initialen Auth-Check ausführen
- aktuellen Nutzer im React-State halten
- Login durchführen
- Logout durchführen
- User-Refresh anbieten
- Sprache mit `language_pref` synchronisieren

## Initialer Auth-Check

Beim Start ruft das Frontend `/api/auth/me` auf.

Mögliche Folgen:
- Benutzer vorhanden → Session gilt als aktiv
- Fehler → Benutzer wird auf `null` gesetzt
- Ladezustand steuert geschützte Routen und Redirects

## Login-Verhalten

Der Login selbst läuft über einen expliziten POST auf `/api/auth/login`.

Wichtig:
- Cookies werden mitgesendet
- erfolgreicher Login setzt den User-State
- Sprache wird aus dem Userprofil synchronisiert

## Logout-Verhalten

Beim Logout versucht das Frontend einen Logout-Endpunkt aufzurufen und leert danach den lokalen User-State.

## `apiClient`

Der zentrale Axios-Client ist für API-Kommunikation mit Session-Handling zuständig.

Eigenschaften:
- `withCredentials: true`
- globale 401-Behandlung
- einmaliger Refresh-Versuch pro Request
- Request-Queue während laufendem Refresh
- Redirect auf `/auth/login`, wenn Refresh fehlschlägt

## Refresh-Flow

Wenn ein API-Request mit `401` antwortet:

1. wird geprüft, ob es sich nicht bereits um einen Auth-Endpunkt handelt
2. wird – einmalig – `/api/auth/refresh` versucht
3. parallele Requests werden währenddessen gequeued
4. bei Erfolg wird der ursprüngliche Request erneut gesendet
5. bei Fehler wird ausgeloggt bzw. auf Login umgeleitet

## Sicherheitsprinzip

Das Frontend speichert keine Tokens in `localStorage`.

Vorteile:
- geringere Angriffsfläche für klassische Token-Leaks im Browser-Storage
- ein konsistenterer Session-Pfad über httpOnly Cookies

Abhängigkeiten:
- korrektes Cookie-Setup im Backend
- funktionierende SameSite-/Secure-Konfiguration
- stimmige URL- und CORS-Situation zwischen Frontend und Backend

## Sprachsynchronisation

Ein bemerkenswerter Teil des Auth-Flows ist die direkte Kopplung der Session an `language_pref`.

Das bedeutet:
- Benutzerzustand beeinflusst direkt das i18n-Verhalten
- Auth-Probleme können indirekt auch die Sprachwahrnehmung beeinflussen

## Typische Fehlerbilder

### Session wird lokal nicht gehalten
Mögliche Ursachen:
- falsche Backend-URL
- unpassende Cookie-Flags
- SameSite-/Secure-Mismatch
- HTTPS-/Origin-Unterschiede

### Redirect-Schleifen
Mögliche Ursachen:
- `/api/auth/me` liefert unerwartet 401
- Refresh-Flow schlägt systematisch fehl
- Benutzerstatus bleibt im Frontend inkonsistent

### Sprache springt unerwartet
Mögliche Ursache:
- `language_pref` wird beim Refresh/User-Reload neu angewendet

## Gekoppelte Systeme

Die Frontend-Session hängt eng an:

- Backend-Auth-Endpunkten
- Cookie-Konfiguration
- Routing / Protected Routes
- i18n
- Browser-Origin-/Deploy-Situation

## Dokumentationsregel

Diese Seite sollte aktualisiert werden, wenn:

- Login-/Logout-/Refresh-Verhalten geändert wird
- `AuthContext` erweitert oder umgebaut wird
- Token-/Cookie-Strategie geändert wird
- Sprache oder Benutzerzustand anders synchronisiert wird
- Redirect- oder Fehlerbehandlung im `apiClient` geändert wird
