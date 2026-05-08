"""
Rate Limiter – Zentrales Modul fuer slowapi Rate-Limiting.
Wird von server.py und allen Routern importiert.

Granulare Limits:
  - Standard: 120/min (allgemeine API-Nutzung)
  - Auth: 10/min (Brute-Force-Schutz)
  - File-Upload: 20/min
  - KI-Screening: 10/min (Kostenreduktion)
  - Support-Chat: 30/min
  - Leads-Ingest: 15/min (Spam-Schutz)
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

# Vordefinierte Limit-Strings fuer Router
RATE_AUTH = "10/minute"
RATE_UPLOAD = "20/minute"
RATE_AI = "10/minute"
RATE_CHAT = "30/minute"
RATE_INGEST = "15/minute"
RATE_EXPORT = "5/minute"
