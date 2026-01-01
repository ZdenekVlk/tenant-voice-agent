# CODEX Tasks - Stage 10: Observabilita (request_id, structured logs, metriky)

## Status
- [x] T1: Navrhnout umístění a rozhraní pro request context
- [x] T2: Implementovat middleware pro `X-Request-Id`
- [x] T3: Zajistit `request_id` v error odpovědích
- [x] T4: Structured logs (start/finish + error, tenant kontext)
- [x] T5: Metriky + endpoint `/metrics`
- [x] T6: Testy (request_id + /metrics)
- [x] T7: `pytest -q` + výsledek
- [x] T8: Dokumentace (`docs/stages/10-observability.md`)
- [ ] T9: Commit `feat(obs): add request id, structured logs, and metrics`

## Poznámky
- `X-Request-Id` se vždy vrací v odpovědi (včetně chyb).
- `pytest -q`: 27 passed in 3.11s
