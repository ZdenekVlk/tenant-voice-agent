# CODEX Tasks — Stage 10: Observabilita (request_id, structured logs, metriky)

## Cíl
- Přidat `request_id` pro každý HTTP request (včetně error odpovědí)
- Zavést structured logs (ideálně JSON) s korelačními poli
- Přidat základní metriky (počet requestů, latence, statusy) a endpoint pro jejich export

## Guardrails (must)
- [ ] Nezalogovat citlivá data (JWT tokeny, secrets, celé request bodies).
- [ ] Tenant context (pokud existuje) musí být v logu: `tenant_id`, `conversation_id`.
- [ ] Žádné rozbití multitenancy pravidel (dotazy musí zůstat tenant-scoped).
- [ ] Vše musí být pokryté alespoň „cheap“ testy (tam kde to dává smysl).

## TODO
- [ ] T1: Navrhnout umístění a rozhraní pro request context (request_id + volitelně tenant_id/conversation_id)
- [ ] T2: Implementovat middleware pro `X-Request-Id`:
  - pokud header chybí → vygenerovat
  - nastavit do `request.state.request_id`
  - vracet `X-Request-Id` v odpovědi
- [ ] T3: Zajistit, že request_id je i v error odpovědích (včetně FastAPI/validation errors)
- [ ] T4: Structured logs:
  - request start/finish log s: method, path, status_code, duration_ms, request_id
  - error log s: request_id + (pokud existuje) error_code
  - přidat `tenant_id` + `conversation_id` do logů pro widget routy (kde je session)
- [ ] T5: Metriky:
  - počet requestů + latence (+ status) alespoň pro všechny API routes
  - endpoint `GET /metrics` (nebo ekvivalent) pro lokální export
  - dokumentovat jak metriky číst a jak je otestovat lokálně
- [ ] T6: Testy:
  - request_id: generuje se a vrací v response headeru
  - request_id: respektuje `X-Request-Id` pokud je poslané
  - (pokud je realistické) logs: obsahují request_id (např. přes `caplog`)
  - /metrics endpoint vrací 200 a obsahuje alespoň očekávané metriky
- [ ] T7: Dokumentace:
  - `docs/stages/10-observability.md`
  - `docs/tasks/10-*-codex-tasks.md` (tento checklist + výsledek `pytest -q` + poznámky)
- [ ] T8: `pytest -q` + výsledek do docs/tasks
- [ ] T9: Commit `feat(obs): add request id, structured logs, and metrics`

## Akceptační kritéria
- [ ] Každý request má `X-Request-Id` v response a je zalogovaný.
- [ ] Pro widget endpointy (kde je session) se do logů propisuje i `tenant_id` a `conversation_id`.
- [ ] Logy jsou strojově čitelné (preferovaně JSON) a neobsahují citlivá data.
- [ ] `/metrics` vrací metriky pro request count + latenci (a nepřerušuje běh API).
- [ ] Test suite pro Stage 10 prochází (`pytest -q`).
