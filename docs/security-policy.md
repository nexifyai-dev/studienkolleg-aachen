# Security Policy (Credentials & Secrets)

## No credentials in Git

- **Never commit real or production-like credentials** (passwords, API keys, tokens, SMTP creds, DB URLs) to this repository.
- Test and seed credentials must be provided via environment variables.
- Historical reports and memory notes must only reference placeholders (e.g. `${TEST_ADMIN_PASSWORD}`).

## Required local setup (unversioned)

Create a local, untracked `.env.local` file and set values there. Example keys (without real values):

```bash
TEST_ADMIN_PASSWORD=
TEST_DEFAULT_PASSWORD=
TEST_INVALID_PASSWORD=
TEST_REGISTER_PASSWORD=
TEST_LEAD_CLAIM_PASSWORD=
TEST_PORTAL_PASSWORD=
```

> `.env.local` must stay local and unversioned.

## CI enforcement

Secret scanning runs in CI using **gitleaks** on every push and pull request to prevent secret re-introduction.
