# Stage 11: Idempotence pro `POST /widget/messages`

## Kontext
- Po Stage 05 potřebujeme retry-safe odesílání zpráv z widgetu.
- Navazuje na Stage 04 (session kontext) a Stage 10 (request_id + logování).
- Stage 11 zavádí idempotenci pro `POST /widget/messages`.

## Cíl etapy
- Volitelný `Idempotency-Key` header zajistí, že duplicitní request nevytvoří další zprávu.
- Stejný klíč + stejný payload vrací stejný `message_id` a `conversation_id`.
- Stejný klíč + jiný payload vrací 409 `idempotency_key_conflict`.

## Scope
### In scope
- Idempotence pro `POST /widget/messages` na úrovni DB (unikátní constraint).
- Detekce konfliktu přes hash validovaného payloadu.
- Structured log eventy `idempotency_miss`, `idempotency_hit`, `idempotency_conflict`.
- Testy pro idempotentní chování.

### Out of scope
- Retence/cleanup idempotency záznamů (follow-up).
- Idempotence pro jiné endpointy.
- Distribuované locky / cross-service idempotence.

## API kontrakty
### Endpointy
- `POST /widget/messages`
  - Headers:
    - `Authorization: Bearer <jwt>`
    - `Idempotency-Key: <string>` (volitelný)
  - Body:
    ```json
    {
      "text": "Ahoj, potřebuji pomoct s fakturou.",
      "metadata": {}
    }
    ```
  - Response 200:
    ```json
    {
      "conversation_id": "<uuid>",
      "message_id": "<uuid>"
    }
    ```
  - Errors:
    - 400 `invalid_text`
    - 401 `missing_authorization` / `invalid_authorization` / `invalid_token` / `token_expired` / `invalid_claims`
    - 403 `conversation_not_found` / `tenant_mismatch`
    - 409 `idempotency_key_conflict`
    - 422 (validace těla)

## Datový model a DB
- Nová tabulka `idempotency_keys`:
  - `tenant_id`, `conversation_id`, `key` (unikátní kombinace)
  - `request_hash` (hash canonical JSON payloadu)
  - `response_json` (uložený response s `message_id`)
  - `created_at`
- Unikátní constraint: `uq_idempotency_keys__tenant_id__conversation_id__key`.
- Kompozitní FK: `idempotency_keys(tenant_id, conversation_id)` -> `conversations(tenant_id, id)`.

## Multitenancy a bezpečnost
- `tenant_id` a `conversation_id` se berou výhradně z `require_widget_session`.
- Všechny dotazy jsou tenant-scoped.
- Logy neobsahují text zpráv ani celé request body.

## Implementační poznámky
- Handler: `backend/src/app/api/routes/widget_messages.py`.
- Migrace: `backend/alembic/versions/6b1c4c2f8a47_add_idempotency_keys.py`.
- Testy: `backend/tests/test_widget_messages.py`.

## Akceptační kritéria
- [ ] Duplicitní request se stejným `Idempotency-Key` nevytvoří novou zprávu.
- [ ] Duplicitní request vrací stejné `message_id` a `conversation_id`.
- [ ] Konflikt stejného klíče s jiným payloadem vrací 409 `idempotency_key_conflict`.
- [ ] Tenant isolation zůstává zachovaná.

## Test plan
### Unit testy
- `Idempotency-Key` replay vrací stejný response.
- Konflikt klíče s jiným payloadem vrací 409.
- Bez `Idempotency-Key` zůstává stávající chování.

### Integrační / API testy
- Pokud není DB test infra, stačí manuální test (curl).

## Jak spustit (lokálně)
1. `.env.example` -> `.env` a nastav `DATABASE_URL` + `WIDGET_SESSION_JWT_SECRET`.
2. Spusť Docker Compose:
   - `cd infra`
   - `docker compose up -d --build`
3. Aplikuj migrace:
   - `docker compose exec api alembic upgrade head`

## Jak otestovat
- `cd backend`
- `pytest -q`

## Známá omezení
- Retence/cleanup idempotency záznamů zatím není řešena.

## TODO / Follow-ups
- Cleanup/retence `idempotency_keys` (např. TTL).
- Monitoring objemu tabulky v produkci.

## Production checklist (later)
- (none)

## Odkazy
- ADR: [ADR-0002](</docs/adr/ADR-0002-migrations-a-naming-conventions.md>)
- Stage předtím: [Stage 10](</docs/stages/10-observability.md>)
- Stage kontrakt: [Stage 05](</docs/stages/05-widget-messages.md>)
