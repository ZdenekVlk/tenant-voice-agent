# Stage 01 - Bootstrap projektu

## Metadata
- ID etapy: 01-bootstrap
- Datum: 2025-12-28
- Branch: `stage/01-bootstrap`
- Commit/PR: (zatím bez commitu)
- Autor: Codex

## Cíl
Inicializovat základní strukturu repozitáře a vývojové minimum pro backend.
Připravit Docker Compose pro PostgreSQL + backend API a kostru Alembic konfigurace
bez migrací.

## Rozsah (DO)
- [x] Vytvořit výchozí adresářovou strukturu (`backend/`, `frontend/widget/`, `docs/`).
- [x] Přidat `.env.example`, `.gitignore`, `.editorconfig`.
- [x] Zprovoznit lokální prostředí přes Docker Compose pro backend + DB (frontend/widget mimo compose).
- [x] Základ FastAPI aplikace s `/health`.
- [x] Připravit Alembic (init + config přes `DATABASE_URL`).

## Mimo rozsah (DON'T)
- [x] Žádná RAG logika.
- [x] Žádný LangGraph agent.
- [x] Žádné UI řešení do hloubky.
- [x] Žádné produkční deploymenty.
- [x] Nepřidán pgAdmin do docker-compose.

## Co se změnilo
### Přidané/změněné soubory
- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/.gitkeep`
- `backend/src/app/main.py`
- `backend/src/app/api/routes/health.py`
- `backend/src/app/api/routes/__init__.py`
- `backend/src/app/core/config.py`
- `backend/src/app/__init__.py`
- `backend/src/app/api/__init__.py`
- `backend/src/app/core/__init__.py`
- `frontend/widget/README.md`
- `infra/docker-compose.yml`
- `.env.example`
- `.gitignore`
- `.editorconfig`
- `docs/stages/01-bootstrap.md`

### Poznámky k návrhu
- Backend používá jednoduchý `src/` layout a samostatné moduly pro routy.
- Alembic je připraven bez modelů a migrací; pouze konfigurace a běh.
- `.env` je používán jako jediný zdroj `DATABASE_URL` pro Alembic i běh API.
- Docker Compose je v `infra/`, aby se oddělila infrastruktura od aplikačního kódu.

## Jak spustit (lokálně)
### Požadavky
- Docker + Docker Compose
- Python 3.12
- Node.js (pro widget v další etapě)

### Kroky
1. Zkopíruj `.env.example` → `.env` a uprav hodnoty (min. `DATABASE_URL`).
2. Spusť infrastrukturu:
   - `cd infra`
   - `docker compose up -d`
3. Ověř health endpoint:
   - `GET http://localhost:8000/health`

## Alembic (migrace)
- Běh příkazů (z adresáře `backend`):
  - `alembic current`
  - `alembic history`
- Alternativa přes Docker image (z adresáře `infra`):
  - `docker compose exec api alembic current`
  - `docker compose exec api alembic history`
- Poznámky:
  - V této etapě neexistují migrace ani modely, jen konfigurace.
  - `DATABASE_URL` se načítá z `.env` v kořeni repozitáře.

## Jak otestovat
- Ruční test:
  - `/health` vrací 200
  - Postgres běží a je dostupný z backendu
- Alembic přes Docker:
  - `docker compose exec api alembic current`
  - `docker compose exec api alembic history`

## Známá omezení
- Zatím bez auth a bez validace domén widgetu.
- Zatím bez DB schématu a migrací.
- Frontend/widget je pouze placeholder.

## Další etapa (návrh)
- 02-db-schema: tabulky + první init migrace
- 03-widget-session: `/widget/session` + validace domény + založení konverzace

## Checklist pro uzavření etapy
- [x] Dokumentace aktualizována
- [x] Základní run instrukce fungují
- [x] Žádná tajemství v commitu
