# QA & Release Gates

> Übersicht: [README](../../README.md) · Artefakt: [release/golive_checklist.yaml](../../release/golive_checklist.yaml)

## Gate-Set (verbindlich)

1. **Build Gate**
   - Backend startet ohne Import-/Syntaxfehler
   - Frontend Build erfolgreich
2. **Regression Gate**
   - Kritische Rollen-/Portalflüsse grün
   - Auth/Routing/i18n nicht regressiv
3. **AI Gate**
   - Entscheidungsgrenzen eingehalten
   - Keine Auto-Entscheidung aus bloßem Upload
4. **Security/Compliance Gate**
   - Keine Secrets im Code
   - Logging/Audit vollständig
5. **Go-Live Gate**
   - Checkliste vollständig
   - Rollback-Plan freigegeben

## Verknüpfungen

- [Teststrategie](test-strategy.md)
- [Rollback](rollback.md)
- [Governance PR-Policy](../governance/pr-policy.md)
- [Changelog](../../CHANGELOG.md)

## Dokumentverantwortung

- **Owner:** QA Lead
- **Update-Prozess:** Bei jeder PR mit neuen Features, kritischen Bugfixes, Pipeline- oder Testscope-Änderungen.
