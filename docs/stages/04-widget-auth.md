# Stage 04: Ověření widget session tokenu

## Metadata
- ID: 04
- Datum: 2025-12-29
- Branch: `stage/04-widget-auth`
- Autor: Codex

## Kontext
- Potřebujeme ověřovat widget JWT tokeny a vynutit tenant + conversation kontext pro budoucí `/widget/*` endpointy.
- Navazuje na Stage 03, která vydává widget session tokeny.

## Cíl etapy
- Přidat dependency `require_widget_session` (JWT validace + DB sanity check).
- Standardizovat přenos tokenu přes `Authorization: Bearer <jwt>`.
- Přidat chráněný endpoint `GET /widget/whoami` pro ověření session.

## Scope
### In scope
- Parser a validátor `Authorization` headeru (Bearer).
- Ověření JWT: signature, exp, claims (tenant_id, conversation_id).
- DB kontrola vazby `conversation_id -> tenant_id`.
- CORS úprava pro `Authorization` a GET.
- Cheap unit testy pro token validaci.

### Out of scope
- Plnohodnotné `/widget/messages` API.
- RLS policies nebo pokročilé rate-limity.
- Widget UI nebo embed script.

## API kontrakty
### Endpointy
- `GET /widget/whoami`
  - Headers:
    - `Authorization: Bearer <jwt>`
  - Body: žádný
  - Response 200:
    ```json
    {
      "tenant_id": "<uuid>",
      "conversation_id": "<uuid>"
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

## Datový model a DB
- Použité tabulky: `conversations`.
- DB sanity check:
  - `SELECT tenant_id FROM conversations WHERE id = :conversation_id`
- Migrace: žádná.

## Multitenancy a bezpečnost
- JWT musí obsahovat `tenant_id` + `conversation_id`.
- DB kontrola vynucuje vazbu `conversation_id -> tenant_id` a chrání proti stale tokenům.
- CORS umožňuje poslat `Authorization` header z prohlížeče.

## Implementační poznámky
- Dependency: `backend/src/app/api/dependencies/widget_auth.py`.
- Router: `backend/src/app/api/routes/widget_auth.py`.
- CORS: `backend/src/app/main.py`.

## Akceptační kritéria
- [ ] `GET /widget/whoami` vrací 200 s tenant + conversation pro validní token.
- [ ] Chybějící / nevalidní `Authorization` vrací 401.
- [ ] Expired token vrací 401.
- [ ] Neexistující nebo nesedící conversation vrací 403.

## Test plan
### Unit testy
- Parser Authorization headeru (missing/invalid).
- JWT validace (invalid signature, expired).
- Claims validace (missing/non-uuid).

### Integrační / API testy
- Pokud není DB test infra, použij manuální test.

## Jak spustit (lokálně)
1. `.env.example` → `.env` a nastav `DATABASE_URL` + `WIDGET_SESSION_JWT_SECRET`.
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
1. Vytvoř tenant + doménu:
   ```sql
   INSERT INTO tenants (name, slug, is_active) VALUES ('Acme ISP', 'acme', true) RETURNING id;
   INSERT INTO tenant_domains (tenant_id, domain) VALUES ('<tenant_id>', 'allowed.example');
   ```
2. Získej token:
   ```bash
   curl -X POST http://localhost:8000/widget/session \
     -H "Origin: https://allowed.example"
   ```
3. Ověř token:
   ```bash
   curl http://localhost:8000/widget/whoami \
     -H "Authorization: Bearer <token>"
   ```
4. Očekávej 200 + tenant_id + conversation_id.
5. Zkus bez `Authorization` → 401.
6. Zkus `Authorization: Bearer garbage` → 401.

## Známá omezení
- Endpointy `/widget/*` zatím existují pouze pro `whoami`.
- Bez integračních testů s DB (jen manuální).

## TODO / Follow-ups
- Napojit budoucí `/widget/messages` na `require_widget_session`.
- Přidat integrační testy pro DB sanity check.

## Odkazy
- Stage předtím: [Stage 03](</docs/stages/03-widget-session.md>)
