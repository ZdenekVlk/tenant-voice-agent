# Stage 03: Widget session

## Kontext
- Potřebujeme vytvořit session pro widget na základě validace domény (ADR-0001).
- Stage 02 definuje tabulky `tenants`, `tenant_domains` a `conversations`.

## Cíl etapy
- Přidat endpoint `POST /widget/session` s validací domény a založením konverzace.
- Vydat krátkodobý JWT token scoped na `tenant_id` + `conversation_id`.
- Přidat minimální DB layer a CORS middleware pro browser volání.

## Scope
### In scope
- `POST /widget/session` (Origin/Referer → tenant → conversation → JWT).
- Minimalní DB layer (`engine`, `sessionmaker`, `get_db`).
- Normalizace domény z `Origin`/`Referer`.
- JWT utilita pro widget session.
- Cheap unit testy pro normalizaci domény.

### Out of scope
- Autentizace uživatele nebo admin API.
- RLS policies.
- Widget UI nebo embed script.

## API kontrakty
### Endpointy
- `POST /widget/session`
  - Headers:
    - `Origin` (preferované)
    - `Referer` (fallback)
  - Body: žádné
  - Response 200:
    ```json
    {
      "conversation_id": "<uuid>",
      "token": "<jwt>",
      "expires_in": 600,
      "ui_config": {}
    }
    ```
  - Errors:
    - 400 `invalid_origin` (chybí nebo neplatný `Origin`/`Referer`)
    - 403 `domain_not_allowed` (doména není v `tenant_domains`)

## Datový model a DB
- Použité tabulky: `tenant_domains`, `conversations` (viz Stage 02).
- Query flow:
  - `SELECT tenant_id FROM tenant_domains WHERE domain = :hostname`
  - `INSERT INTO conversations (tenant_id) VALUES (:tenant_id) RETURNING id`
- Migrace: žádná nová (využívá se init migrace ze Stage 02).

## Multitenancy a bezpečnost
- Tenant scope vynucen lookupem přes `tenant_domains` a ukládáním `tenant_id` do `conversations`.
- CORS je pouze technické povolení browseru, ne bezpečnostní ochrana.
- Bezpečnost zajišťuje allowlist domén + JWT token.

## Implementační poznámky
- Routing: `backend/src/app/api/routes/widget_session.py` + registrace v `backend/src/app/api/routes/__init__.py`.
- DB layer: `backend/src/app/core/db.py`.
- JWT utility: `backend/src/app/core/security.py`.
- Normalizace Origin/Referer: `backend/src/app/utils/origin.py`.

## Akceptační kritéria
- [ ] `POST /widget/session` vrací 200 pro povolenou doménu.
- [ ] `POST /widget/session` vrací 400 pro neplatný Origin/Referer.
- [ ] `POST /widget/session` vrací 403 pro neznámou doménu.
- [ ] Vytvořená konverzace je uložena s `tenant_id`.

## Test plan
### Unit testy
- Normalizace domény z `Origin`/`Referer` (`backend/tests/test_origin.py`).

### Integrační / API testy
- Pokud není integrační infra, použij manuální postup níže.

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
1. Přidej testovací tenant + doménu:
   ```sql
   INSERT INTO tenants (name, slug, is_active) VALUES ('Acme ISP', 'acme', true) RETURNING id;
   INSERT INTO tenant_domains (tenant_id, domain) VALUES ('<tenant_id>', 'allowed.example');
   ```
2. Zavolej endpoint:
   ```bash
   curl -X POST http://localhost:8000/widget/session \
     -H "Origin: https://allowed.example"
   ```
3. Očekávej 200 + `conversation_id` + `token`.

## Známá omezení
- Bez autentizace pro jiné API než `/widget/session`.
- `ui_config` je zatím prázdný objekt.

## TODO / Follow-ups
- Přidat validační logiku pro `Origin` + `Referer` (např. whitelist více domén).
- Přidat testy pro DB (happy path / deny) s test DB.
- Přidat session validation pro další endpointy.

## Odkazy
- ADR: `docs/adr/ADR-0001-multitenancy-a-validace-domen.md`
- ADR: `docs/adr/ADR-0002-migrations-a-naming-conventions.md`
- Stage předtím: `docs/stages/02-db-schema.md`
