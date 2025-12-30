# Roadmap: Tenant Voice Agent (Widget text chat MVP → voice later)


---

## Kontext projektu (shrnutí)
Budujeme multi-tenant SaaS chat widget (zatím **text**), embedovatelný na webu tenanta. Backend je FastAPI + PostgreSQL.
Multitenancy je povinná od začátku a všechna data musí být tenant-scoped. (Viz `docs/adr/ADR-0001-multitenancy-a-validace-domen.md`.)  

**Non‑negotiables pro implementaci (platí pro všechny stages):**
- Každý DB dotaz musí být tenant-scoped.
- Žádné tajné klíče do gitu (`.env` lokálně, `.env.example` v repu).
- Změna schématu = Alembic migrace + `upgrade` + test.
- Každá etapa aktualizuje `docs/stages/NN-*.md`.
- Změny držet malé a kontrolovatelné.


## Milestones (produktově)

### Milestone M1 — Widget Text Chat MVP (end‑to‑end, jednoduchý)
Cíl: web tenanta embedne widget → vznikne session + conversation → uživatel pošle text → zpráva se uloží (a následně i odpověď asistenta). Vše tenant-scoped.

| Stage | Název | Výstup | Stav |
|---:|---|---|---|
| 03 | Widget session | `POST /widget/session` + JWT + založení conversation | ✅ |
| 04 | Widget auth | `require_widget_session` + `GET /widget/whoami` | ✅ |
| 05 | Create message | `POST /widget/messages` uloží user message tenant-scoped | ⏳ |
| 06 | Assistant reply (stub → LLM) | uloží assistant message tenant-scoped | ⏺︎ |
| 07 | Widget UI (minimální) | UI zavolá session + messages, vykreslí historii | ⏺︎ |
| 08 | Read history | `GET /widget/conversations/{id}/messages` (paging) | ⏺︎ |

> Výstup M1: „Funguje textový chat přes widget na allowlist doméně.“

### Milestone M2 — Production‑ready Widget (robustnost, bezpečnost, pozorovatelnost)
Cíl: odolné chování v browseru, auditovatelnost, ochrany proti zneužití.

- Stage 09: rate limiting + limity velikosti payloadu
- Stage 10: observabilita (structured logs, request_id, metriky)
- Stage 11: idempotence (`Idempotency-Key`) pro create message
- Stage 12: admin tooling (správa domén/tenantů, health/debug)
- Stage 13: security hardening (rotace secretu, stricter CORS, key versioning)

### Milestone M3 — Voice (po stabilizaci text MVP)
Cíl: přidat voice pipeline (STT/TTS) a případně realtime streaming.  
Pozn.: tento milestone zatím není rozpracován do stages (bude až po M1/M2).

