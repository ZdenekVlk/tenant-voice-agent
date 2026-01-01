# Tenant Voice Agent

Multi-tenant SaaS chat widget pro podporu ISP (zatím pouze text). Frontend je minimální embed widget, backend je Python + FastAPI s PostgreSQL a JWT autentizací pro widget session.

## Stav vyvoje
- Milestone M1 (stage 01-08) je hotovy.
- Detailní stav a seznam hotových funkcionalit: [docs/notes/development-status.md](</docs/notes/development-status.md>)
- Roadmapa: [docs/roadmap-voice-agent.md](</docs/roadmap-voice-agent.md>)

## Architektura (stručně)
- `frontend/widget` - statický widget UI pro testování
- `backend` - FastAPI API, DB modely, sluzby
- `infra` - Docker Compose (API + PostgreSQL)

## Rychlý start (lokálně)
1. Zkopíruj `.env.example` do `.env` a uprav hodnoty podle potřeby.
2. Spust kontejnery:
   ```bash
   cd infra
   docker compose up -d --build
   ```
3. Aplikuj migrace:
   ```bash
   docker compose exec api alembic upgrade head
   ```

## Spuštění widgetu (dev)
Widget je statický, spuštění přes jednoduchý server (kvůli Origin).
```bash
cd frontend/widget
python -m http.server 5173
```
Pak otevři `http://localhost:5173`.

## Testy
```bash
cd backend
pytest -q
```

## Dokumentace
- Stage zapisy: [docs/stages](</docs/stages>)
- ADR: [docs/adr](</docs/adr>)
- Poznámky k produkčním gapům: [docs/notes/prod-gaps.md](</docs/notes/prod-gaps.md>)
