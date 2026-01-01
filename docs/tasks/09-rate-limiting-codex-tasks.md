# CODEX Tasks - Stage 09: Rate limiting + payload limity

## Status
- [x] T1: Zmapovat routy a request modely
- [x] T2: Implementovat rate limiter + klíče
- [x] T3: Napojit limiter na POST routy + logovat blokace
- [x] T4: Implementovat payload limit middleware
- [x] T5: Implementovat max délku textu zprávy + log blokace
- [x] T6: Testy (rate limit, payload size, text length)
- [x] T7: Dokumentace (`docs/stages/09-rate-limiting.md`)
- [x] T8: `pytest -q` + výsledek
- [ ] T9: Commit `feat(security): add rate limiting and payload limits`

## Poznámky
- Log event `blocked` obsahuje `request_id` a důvod blokace.
- `pytest -q`: 27 passed in 2.04s
