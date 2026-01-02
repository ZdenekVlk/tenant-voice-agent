# Stage 09: Rate limiting + payload limity

## Kontext
- Po Stage 08 chybí základní ochrany proti zneužití a runaway nákladům.
- Potřebujeme omezit requesty per tenant a per IP na kritických POST routách.
- Navazuje na Stage 04/05 a očekává logování blokací s request_id (Stage 10).

## Cíl etapy
- Rate limiting pro `POST /widget/session` a `POST /widget/messages` (tenant + IP).
- Payload limity: max velikost JSON body a max délka textu zprávy.
- Při blokaci vzniká structured log event `blocked` s `request_id`.

## Scope
### In scope
- In-memory rate limiter (per process).
- Payload size limit middleware pro dvě POST routy.
- Validace maximální délky textu zprávy.

### Out of scope
- Distribuovaný limiter (Redis) a per-tenant dashboardy.
- Ochrany pro jiné endpointy než `POST /widget/session` a `POST /widget/messages`.

## API kontrakty
### Endpointy
- `POST /widget/session`
  - Errors:
    - 429 `rate_limited` + `Retry-After`
    - 413 `payload_too_large`
- `POST /widget/messages`
  - Errors:
    - 400 `text_too_long`
    - 429 `rate_limited` + `Retry-After`
    - 413 `payload_too_large`

### Příklady response
- 429:
  ```json
  { "detail": "rate_limited" }
  ```
- 413:
  ```json
  { "detail": "payload_too_large" }
  ```

## Datový model a DB
- Bez změn DB a bez migrací.

## Multitenancy a bezpečnost
- Tenant scoped limity používají `tenant_id` z DB (session) nebo JWT (messages).
- IP limit je best-effort (X-Forwarded-For první hodnota, jinak request.client.host).
- Logy neobsahují tokeny ani celé request body.

## Implementační poznámky
- Config: `backend/src/app/core/config.py` + `.env.example`.
- Rate limiter: `backend/src/app/core/rate_limiter.py`.
- Payload limit middleware: `backend/src/app/middleware/payload_limit.py`.
- Request ID helper: `backend/src/app/utils/request_id.py`.
- IP helper: `backend/src/app/utils/client_ip.py`.
- Routy: `backend/src/app/api/routes/widget_session.py`, `backend/src/app/api/routes/widget_messages.py`.

## Akceptační kritéria
- [ ] `POST /widget/session` a `POST /widget/messages` mají rate limit per tenant + per IP.
- [ ] Při překročení limitu vrací 429 + `Retry-After` a loguje `blocked` s `request_id`.
- [ ] Payload size limit vrací 413 a loguje `blocked`.
- [ ] Max délka textu zprávy je validována a blokace je zalogována.
- [ ] Limity jdou nastavit přes ENV a jsou zdokumentované.

## Test plan
### Unit testy
- Rate limit pro `POST /widget/messages` (N+1 -> 429).
- Payload size limit (413).
- Text length limit (400).

### Integrační / API testy
- Pokud není DB test infra, stačí manuální test přes `curl`.

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
1. Rate limit:
   ```bash
   curl -X POST http://localhost:8000/widget/session -H "Origin: https://allowed.example"
   ```
2. Payload limit:
   ```bash
   curl -X POST http://localhost:8000/widget/messages \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"text":"...velky payload..."}'
   ```

## Známá omezení
- Rate limiter je in-memory (per process), v multi-worker režimu se limity nesdílí.
- IP je best-effort; bez důvěryhodného proxy není garantovaná.

## TODO / Follow-ups
- Přepnout na distribuovaný limiter (např. Redis), pokud bude potřeba.
- Přidat per-tenant observability pro blokace.

## Production checklist (later)
- Nasazení reverzní proxy s real IP (a validace X-Forwarded-For).
- Centralizovaný rate limit store (Redis).
- Tuning limitů podle reálného provozu.

## Odkazy
- Stage předtím: [Stage 08](</docs/stages/08-read-history.md>)
- Stage auth: [Stage 04](</docs/stages/04-widget-auth.md>)
- Stage observabilita: [Stage 10](</docs/stages/10-observability.md>)
