[STAGE] 01-bootstrap

Dodrž instrukce v Agent.md.
Respektuj ADR: docs/adr/ADR-0001-multitenancy-a-validace-domen.md.

Goal:
- Založit výchozí strukturu repozitáře (backend, frontend/widget, docs).
- Připravit Docker Compose pro Postgres + backend API (frontend mimo compose).
- Inicializovat FastAPI skeleton s /health.
- Inicializovat Alembic (bez kompletního schématu; stačí připravená konfigurace a ověřený běh `alembic current`).

Scope (DO):
- Přidat/ověřit: .gitignore, .editorconfig, .env.example
- Přidat infra/docker-compose.yml (db + api), bez pgAdmin
- Backend: spustitelný FastAPI s /health
- Alembic: init + konfigurace z env (DATABASE_URL)
- Dokumentace: vyplnit docs/stages/01-bootstrap.md (podle šablony a reálně provedených změn)

Out of scope (DON'T):
- Žádné DB tabulky pro tenanty/konverzace (to bude stage 02)
- Žádné RAG, žádný LangGraph
- Žádné auth/tokeny (jen skeleton)

Acceptance criteria:
- `docker compose up -d` zvedne db a api
- `GET /health` vrátí 200
- `alembic current` a `alembic history` funguje (i bez migrací)
- docs/stages/01-bootstrap.md obsahuje přesné instrukce run/test

Deliverables:
- Seznam změněných souborů
- How to run / How to test
- Návrh commit message
- Závěrečná odpověď česky ve formátu definovaném v Agent.md
