# Stage 02 - DB schema (init migrace)

## Metadata
- ID etapy: 02-db-schema
- Datum: 2025-12-28
- Branch: `stage/02-db-schema`
- Commit/PR: (doplnit)
- Autor: Codex

## Cíl
Založit základní databázové schéma pro multi-tenant chat widget:
- `tenants`
- `tenant_domains`
- `conversations`
- `messages`
- `incidents`
- `events`

Zároveň explicitně připravit pravidla pro budoucí tabulky, které budou mít
„tenant override + global fallback“ záznamy (`tenant_id IS NULL`) – viz ADR-0001.

## Rozsah (DO)
- [ ] Přidat init Alembic migraci s výše uvedenými tabulkami + indexy.
- [ ] Přidat kompozitní FK pro ochranu proti cross-tenant vazbám:
  - `messages(tenant_id, conversation_id) -> conversations(tenant_id, id)`
  - `events(tenant_id, incident_id) -> incidents(tenant_id, id)` atd.
- [ ] Přidat dokumentaci ADR-0002 (migrace + naming conventions + partial indexy).
- [ ] Ověřit, že `alembic upgrade head` projde v Docker Compose prostředí.

## Mimo rozsah (DON'T)
- [ ] Žádná implementace endpointů `/widget/session` (to je Stage 03).
- [ ] Žádné RLS policies.
- [ ] Žádné workflow tabulky (jen připravené pravidlo pro budoucí migrace).

## Co se změnilo
### Přidané/změněné soubory
- `docs/adr/ADR-0002-migrations-a-naming-conventions.md`
- `docs/stages/02-db-schema.md`
- `backend/alembic/versions/<rev>_02_init_schema.py`

### Poznámky k návrhu
- `tenant_id` je `NOT NULL` pro všechny tenant-scope tabulky (conversations/messages/incidents/events/tenant_domains).
- `tenants` je „root“ tabulka bez `tenant_id`.
- DB-level izolace:
  - rodičovské tabulky mají `UNIQUE(tenant_id, id)`
  - child tabulky mají kompozitní FK na `(tenant_id, <parent_id>)`
- Budoucí „globální“ tabulky:
  - `tenant_id` bude nullable
  - unikátnost řešit partial unique indexy:
    - `UNIQUE(key) WHERE tenant_id IS NULL`
    - `UNIQUE(tenant_id, key) WHERE tenant_id IS NOT NULL`

## Jak spustit (lokálně)
1. `.env.example` → `.env` a nastav `DATABASE_URL` (viz Stage 01).
2. Spusť Docker Compose:
   - `cd infra`
   - `docker compose up -d`
3. Aplikuj migrace:
   - `docker compose exec api alembic upgrade head`

## Jak otestovat
- Migrace:
  - `docker compose exec api alembic current`
  - `docker compose exec api alembic history`
  - `docker compose exec api alembic downgrade base`
  - `docker compose exec api alembic upgrade head`
- Rychlá sanity kontrola v DB:
  - připojit se do Postgres a `\dt` ověřit tabulky
  - zkusit vložit `message` s `tenant_id` neodpovídajícím `conversation.tenant_id` → musí selhat na FK

## Známá omezení
- Zatím žádná aplikační vrstva nad tabulkami (CRUD, repos, endpointy).
- `events` a `incidents` jsou zatím obecné – upřesní se až s konkrétním event/incident taxonomií.

## TODO (další etapy)
- Stage 03: `/widget/session` + validace domén + založení `conversation`
- Stage 04: ukládání `messages` přes API
- Stage 0X: workflow tabulky s `tenant_id NULL` + partial unique indexy
