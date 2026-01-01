# Stage 10: Observabilita (request_id, structured logs, metriky)

## Kontext
- Po Stage 08 chybí základní nástroje pro dohledatelnost requestů a incidentů.
- Potřebujeme korelaci mezi requesty (request_id), strojově čitelné logy a minimální metriky.
- Navazuje na Stage 04/05/08, kde existuje widget session kontext (tenant_id + conversation_id).

## Cíl etapy
- Každý request má `request_id` a vrací `X-Request-Id` v odpovědi (včetně chyb).
- Logy jsou strukturované (JSON) a obsahují request_id + tenant kontext, pokud existuje.
- Základní metriky jsou dostupné přes endpoint `/metrics`.

## Scope
### In scope
- Middleware pro `X-Request-Id` (read/generate + response header).
- Strukturované logy: request start/finish + error logy (bez citlivých dat).
- In-memory metriky pro počet requestů a latenci + `/metrics` endpoint.

### Out of scope
- Plnohodnotný observability stack (Prometheus/Grafana/ELK).
- Distributed tracing.
- Per-tenant dashboards nebo alerty.

## API kontrakty
### Endpointy
- `GET /metrics`
  - Headers: žádné
  - Body: žádné
  - Response 200: text/plain (Prometheus format) s metrikami:
    - `http_requests_total`
    - `http_request_duration_ms_sum`
    - `http_request_duration_ms_count`

### Globální hlavičky
- `X-Request-Id`: odpověď vždy obsahuje request_id (pokud je v requestu poslaný, vrací se stejný).

## Datový model a DB
- Bez změn DB a bez migrací.

## Multitenancy a bezpečnost
- Logy nikdy neobsahují tokeny ani celé request body.
- Pokud je dostupný widget session kontext, logy obsahují `tenant_id` a `conversation_id`.
- Tenant-scoped dotazy zůstávají beze změn.

## Implementační poznámky
- Middleware: `backend/src/app/middleware/observability.py`.
- Logování: JSON formatter v `backend/src/app/core/logging.py`.
- Metriky: in-memory store v `backend/src/app/core/metrics.py` + route `backend/src/app/api/routes/metrics.py`.
- Error logy jsou emitované z FastAPI exception handlerů v `backend/src/app/main.py`.

## Akceptační kritéria
- [ ] Každý request vrací `X-Request-Id`.
- [ ] Request start/finish log obsahuje `method`, `path`, `status_code`, `duration_ms`, `request_id`.
- [ ] Error log obsahuje `request_id` a `error_code` (bez citlivých dat).
- [ ] `/metrics` vrací metriky pro request count + latenci.

## Test plan
### Unit testy
- `X-Request-Id` je generované a vracené v odpovědi.
- `X-Request-Id` respektuje hodnotu z requestu.
- `/metrics` vrací 200 a obsahuje očekávané metriky.

### Integrační / API testy
- Pokud nebude DB test infra, stačí ověřit přes `curl` lokálně.

## Jak spustit (lokálně)
1. `.env.example` -> `.env` a nastav `DATABASE_URL` + `WIDGET_SESSION_JWT_SECRET`.
2. Spusť Docker Compose:
   - `cd infra`
   - `docker compose up -d --build`
3. Aplikuj migrace:
   - `docker compose exec api alembic upgrade head`

## Jak otestovat
### Unit testy
- `cd backend`
- `pytest -q`

### Manuální test
1. `X-Request-Id`:
   ```bash
   curl -i http://localhost:8000/health
   curl -i http://localhost:8000/health -H "X-Request-Id: demo-123"
   ```
2. `/metrics`:
   ```bash
   curl http://localhost:8000/metrics
   ```

## Známá omezení
- Metriky jsou in-memory (po restartu procesu se resetují).
- Neexistuje distribuovaný tracing ani per-tenant agregace.

## TODO / Follow-ups
- Napojit export metrik do Prometheus (pokud bude potřeba).
- Zvážit sampling/omezení logů v produkci.

## Production checklist (later)
- Prometheus scrape konfigurace pro `/metrics`.
- Centralizované logy (sink + retence).
- Ošetření vysoké kardinality v `path` labelech.

## Odkazy
- Stage předtím: [Stage 08](</docs/stages/08-read-history.md>)
- Stage auth: [Stage 04](</docs/stages/04-widget-auth.md>)
