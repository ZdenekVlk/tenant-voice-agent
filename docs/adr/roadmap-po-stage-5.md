# Roadmap: Tenant Voice Agent (Widget text chat MVP → voice later)

> Tento dokument je „řídící“ roadmapa pro CODEX (PM + implementátor) a pro tebe jako zadavatele.
> Navazuje na existující stage dokumenty v `docs/stages/` a ADR v `docs/adr/`.

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

---

## Stav k 2025-12-30
Hotovo:
- [x] Stage 01 — bootstrap (`docs/stages/01-bootstrap.md`)
- [x] Stage 02 — DB schema (`docs/stages/02-db-schema.md`)
- [x] Stage 03 — `POST /widget/session` (`docs/stages/03-widget-session.md`)
- [x] Stage 04 — `require_widget_session` + `GET /widget/whoami` (`docs/stages/04-widget-auth.md`)

Aktuální další krok:
- [ ] **Stage 05 — `POST /widget/messages` + uložení user zprávy tenant-scoped (povinně přes `require_widget_session`)**

---

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

---

## Stage 05 — Spec (základ pro implementaci)
**Název:** `POST /widget/messages` + uložení user zprávy tenant-scoped  
**Přísné omezení:** Stage 05 **musí používat přesně** `require_widget_session` ze Stage 04 **bez dalších rozhodnutí** (tj. žádné nové auth mechaniky, žádné nové token claims, žádný nový způsob přenosu tokenu).

### Cíl
- Přidat endpoint pro vytvoření zprávy v konverzaci.
- Uložit zprávu do tabulky `messages` jako `role="user"` a tenant-scoped.

### In scope
- `POST /widget/messages`
- validace vstupu (`text` povinný, rozumné limity)
- persist `messages` (tenant_id + conversation_id z `require_widget_session`)
- response s `message_id` (+ echo `conversation_id`)
- cheap unit/API testy

### Out of scope
- Generování odpovědi asistenta (to je Stage 06)
- Načítání historie (to je Stage 08)
- Idempotence / retry-safety (to je Stage 11)
- Rate-limity (to je Stage 09)

### Povinné napojení na Stage 04
- Endpoint musí mít dependency `require_widget_session`.
- `tenant_id` a `conversation_id` se berou **výhradně** z výsledku dependency.
- Body nesmí umožnit poslat `tenant_id` ani `conversation_id` (aby se eliminoval prostor pro cross-tenant bug).

### API kontrakt
#### `POST /widget/messages`
Headers:
- `Authorization: Bearer <jwt>` (ověřuje `require_widget_session`)

Request body (JSON):
```json
{
  "text": "Ahoj, potřebuji pomoct s fakturou.",
  "metadata": {}
}
```

Response 200:
```json
{
  "conversation_id": "<uuid>",
  "message_id": "<uuid>"
}
```

Chyby:
- 401: stejné jako Stage 04 (`missing_authorization`, `invalid_authorization`, `invalid_token`, `token_expired`, `invalid_claims`)
- 403: stejné sanity chyby jako Stage 04 (`conversation_not_found`, `tenant_mismatch`)
- 422: validace těla (FastAPI/Pydantic)
- 400: `invalid_text` (pokud zavedete vlastní kontrolu, např. prázdný string po trimu)

### Datový model & DB
- Tabulka: `messages` (z Stage 02).
- Minimální insert:
  - `tenant_id = session.tenant_id`
  - `conversation_id = session.conversation_id`
  - `role = "user"`
  - `content/text = <request.text>`
  - `metadata JSONB` volitelné (pokud ve schématu existuje; jinak vynechat bez migrace)

> Důležité: nic v DB schématu se nemění, pokud Stage 02 už obsahuje všechny potřebné sloupce pro zprávy.
> Pokud by se ukázalo, že `messages` nemá vhodný sloupec pro text/metadata, Stage 05 musí přidat migraci,
> ale stále bez měnění auth nebo session mechanismu.

### Akceptační kritéria
- [ ] Validní token + validní body → 200 a vznikne `messages` řádek s `role=user`.
- [ ] Uložený row je tenant-scoped: `messages.tenant_id` odpovídá tokenu.
- [ ] `conversation_id` v uloženém row odpovídá tokenu.
- [ ] Bez tokenu → 401 (přes `require_widget_session`).
- [ ] Neexistující conversation pro token → 403 (stejně jako Stage 04).

### Test plan
Cheap testy (minimálně):
- Unit: validace request modelu (`text` trim, min length)
- API test: happy path (pokud existuje test DB fixture), jinak manuální test níže

Manuální test (stejný setup jako Stage 03/04):
1) V DB založ tenant + doménu (viz Stage 03).
2) `POST /widget/session` → získat `token` + `conversation_id`
3) `POST /widget/messages` s tokenem:
```bash
curl -X POST http://localhost:8000/widget/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Ahoj","metadata":{}}'
```
4) Ověřit v DB, že `messages` řádek existuje a má správné `tenant_id` + `conversation_id`.

### Dotčené části kódu (orientačně)
- Router: `backend/src/app/api/routes/` (nový modul např. `widget_messages.py`)
- Dependency: použít existující `backend/src/app/api/dependencies/widget_auth.py` (bez změn designu)
- DB access: použít existující DB layer ze Stage 03

---

## Protokol práce pro CODEX (PM + implementátor)
Každý běh stage musí skončit odpovědí (česky) ve formátu:
- Shrnutí (max 8 řádků)
- Změněné soubory (odrážky)
- Jak spustit
- Jak otestovat
- Poznámky / TODO

CODEX má u Stage 05 povinnost:
1) Přečíst: `docs/stages/04-widget-auth.md` a **použít `require_widget_session` beze změn**.
2) Implementovat pouze scope Stage 05.
3) Doplnit/aktualizovat `docs/stages/05-widget-messages.md` (vzor podle Stage 03/04).
4) Spustit testy (minimálně `pytest -q` pokud existuje) a uvést výsledek.

---

## Copy‑paste prompt pro CODEX (Stage 05)
Použij tento prompt beze změn:

> **Úkol:** Implementuj Stage 05: `POST /widget/messages` (uložení user zprávy tenant-scoped).  
> **Povinné omezení:** Endpoint musí používat **přesně** existující dependency `require_widget_session` ze Stage 04. Nedělej žádná nová rozhodnutí kolem auth/session (žádné nové claims, žádné nové token flows, žádné alternativní headery).  
> **Postup:**  
> 1) Otevři a přečti: `docs/stages/03-widget-session.md`, `docs/stages/04-widget-auth.md`, `docs/stages/02-db-schema.md`, relevantní ADR.  
> 2) Navrhni plán změn (seznam souborů + kroky).  
> 3) Přidej endpoint `POST /widget/messages` pod `/widget/*` a použij `require_widget_session`.  
> 4) Ulož řádek do `messages` s `tenant_id` + `conversation_id` z dependency, `role="user"`, a textem z request body.  
> 5) Přidej testy (cheap) a aktualizuj dokumentaci `docs/stages/05-widget-messages.md` (stejný styl jako Stage 03/04).  
> 6) Spusť testy a uveď výsledek.  
> **Výstup:** Připrav commit s message `feat(widget): create message endpoint`.

---

## Poznámky k budoucím stages (pro plánování)
- Stage 06 (assistant reply): nejdřív stub (echo), potom LLM; vždy persist assistant message tenant-scoped.
- Stage 08 (history): paging + order by created_at; kompozitní index `(tenant_id, conversation_id, created_at)` pokud bude potřeba.
- M2 (rate-limity, idempotence): držet odděleně, ať Stage 05 zůstane malá.

