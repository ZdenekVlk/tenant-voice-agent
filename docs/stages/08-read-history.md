# Stage 08: Čtení historie zpráv (paging)

## Kontext
- Widget UI zatím zobrazuje jen lokální historii; potřebujeme možnost načíst zprávy z backendu.
- Navazuje na Stage 04 (auth), Stage 05 (user message) a Stage 06 (assistant reply).

## Cíl etapy
- Přidat endpoint pro načtení zpráv konverzace s pagingem.
- Zajistit tenant enforcement a kontrolu konverzace proti tokenu.
- Vrátit deterministicky řazený seznam zpráv.

## Scope
### In scope
- `GET /widget/conversations/{id}/messages` s `limit` + `offset`.
- Řazení podle `created_at ASC, id ASC`.
- Tenant-scoped query + kontrola shody `conversation_id` z URL a tokenu.

### Out of scope
- Úpravy widget UI (Stage 08 se týká pouze backendu).
- Cursor-based paging nebo filtr podle role.
- Admin endpointy pro historii.

## API kontrakty
### Endpointy
- `GET /widget/conversations/{id}/messages`
  - Headers:
    - `Authorization: Bearer <jwt>`
  - Query:
    - `limit` (1..100, default 50)
    - `offset` (>= 0, default 0)
  - Response 200:
    ```json
    {
      "conversation_id": "<uuid>",
      "messages": [
        {
          "id": "<uuid>",
          "role": "user",
          "content": "Ahoj",
          "metadata": {},
          "created_at": "2025-01-01T00:00:00+00:00"
        }
      ],
      "paging": {
        "limit": 50,
        "offset": 0,
        "has_more": false
      }
    }
    ```
  - Errors:
    - 401 `missing_authorization`
    - 401 `invalid_authorization`
    - 401 `invalid_token`
    - 401 `token_expired`
    - 401 `invalid_claims`
    - 403 `conversation_not_found`
    - 403 `tenant_mismatch`
    - 403 `conversation_mismatch`
    - 422 (validace query parametrů / UUID)

## Datový model a DB
- Tabulka: `messages`.
- Použité sloupce: `tenant_id`, `conversation_id`, `role`, `content`, `meta`, `created_at`.
- Migrace: žádné.

## Multitenancy a bezpečnost
- `require_widget_session` validuje JWT a kontroluje vazbu `conversation_id -> tenant_id`.
- Endpoint odmítne požadavek, pokud `conversation_id` v URL neodpovídá tokenu.
- DB dotaz je tenant-scoped.

## Implementační poznámky
- Router: `backend/src/app/api/routes/widget_messages.py`.
- Testy: `backend/tests/test_widget_history.py`.
- Paging: `LIMIT (limit + 1)` pro výpočet `has_more`.

## Akceptační kritéria
- [ ] Vrací pouze zprávy dané konverzace pro daného tenanta.
- [ ] Paging funguje a řazení je deterministické.
- [ ] Přístup k cizí konverzaci vrací 403.

## Test plan
### Unit testy
- Happy path s pagingem.
- `conversation_id` mismatch -> 403.

### Integrační / API testy
- Pokud není DB test infra, použij manuální test.

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
1. Získej token přes Stage 03.
2. Načti historii:
   ```bash
   curl "http://localhost:8000/widget/conversations/<conversation_id>/messages?limit=20&offset=0" \
     -H "Authorization: Bearer <token>"
   ```
3. Očekávej 200 a seznam zpráv s pagingem.

## Známá omezení
- Pouze offset paging, bez cursoru a bez celkového počtu.

## TODO / Follow-ups
- Stage 09: rate limiting a limity payloadu.
- Stage 11: idempotence pro create message.

## Production checklist (later)
- (none)

## Odkazy
- ADR: [ADR-0001](</docs/adr/ADR-0001-multitenancy-a-validace-domen.md>)
- Stage předtím: [Stage 07](</docs/stages/07-widget-ui.md>)
- Stage předtím: [Stage 05](</docs/stages/05-widget-messages.md>)
- DB schema: [Stage 02](</docs/stages/02-db-schema.md>)
