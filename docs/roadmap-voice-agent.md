# Roadmap: Tenant Voice Agent (Widget text chat MVP → voice later)

## Kontext projektu (shrnutí)

Budujeme multi-tenant SaaS chat widget (zatím **text**), embedovatelný na webu tenanta. Backend je FastAPI + PostgreSQL. Multitenancy je povinná od začátku a všechna data musí být tenant-scoped.

**Non‑negotiables pro implementaci (platí pro všechny stages):**

- Každý DB dotaz musí být tenant-scoped.
- Žádné tajné klíče do gitu (`.env` lokálně, `.env.example` v repu).
- Změna schématu = Alembic migrace + `upgrade` + test.
- Každá etapa aktualizuje `docs/stages/NN-*.md`.
- Změny držet malé a kontrolovatelné.

---

## Milestones (produktově)

### Milestone M1 — Embedovaný widget: textový chat end‑to‑end

Cíl: web tenanta embedne widget → vznikne session + conversation → uživatel pošle text → zpráva se uloží (včetně odpovědi asistenta). Vše tenant-scoped.

| Stage | Název           | Výstup                                                  | Stav |
| ----- | --------------- | ------------------------------------------------------- | ---- |
| 01    | Bootstrap       | repo skeleton + Docker compose (backend + DB)           | ✅    |
| 02    | DB schema       | initial schema + Alembic migrace + základní DB validace | ✅    |
| 03    | Widget session  | `POST /widget/session` + JWT + založení conversation    | ✅    |
| 04    | Widget auth     | `require_widget_session` + `GET /widget/whoami`         | ✅    |
| 05    | Widget messages | uložení user message tenant-scoped                      | ✅    |
| 06    | Assistant reply | uložení assistant message tenant-scoped (stub / základ) | ✅    |
| 07    | Widget UI       | UI: session + send message + render historie            | ✅    |
| 08    | Read history    | `GET /widget/conversations/{id}/messages` (paging)      | ✅    |

> Výstup M1: „Funguje textový chat přes widget na allowlist doméně.“

---

### Milestone M2 — Pilot‑ready widget: robustnost, bezpečnost, pozorovatelnost

Cíl: odolné chování v browseru, auditovatelnost, ochrany proti zneužití.

- Stage 09: rate limiting + limity velikosti payloadu
- Stage 10: observabilita (structured logs, request\_id, metriky)
- Stage 11: idempotence (`Idempotency-Key`) pro create message
- Stage 12: admin tooling (správa domén/tenantů, health/debug)
- Stage 13: security hardening (rotace secretu, stricter CORS, key versioning)

**Zvolený postup (kompromis „pilot minimum, ale ne slepý“):**

1. **Stage 10 – Observabilita** (abychom nebyli při incidentech slepí)
2. **Stage 09 – Rate limiting + payload limity** (základní ochrana)
3. **Stage 11 – Idempotence** (retry-safe odesílání)
4. **Stage 13 – Security hardening** (jen věci, které se později blbě dohánějí)
5. **Stage 12 – Admin tooling** (až onboarding přes DB začne bolet)

---

### Milestone M3 — Textový agent: kostra finálního řešení (bez voice)

Cíl: zapojit **skutečný LLM agent** nad existující konverzací (zatím text), abys viděl reálnou problematiku „kostry“ finální aplikace: orchestrace konverzace, kontext, tool-calls, limity, logování/trace.

### Milestone M4 — Voice: STT/TTS a realtime (až po stabilizaci textového agenta)

Cíl: přidat hlasovou vrstvu (STT/TTS) a případně realtime streaming nad již stabilním agentem.

---

# Rozpracování roadmapy (pracovní část)

## Aktuální stav a nejbližší krok

- **M1 je dokončen** (Stage 01–08 ✅).
- **Nejbližší krok:** M2 pojmeme jako **„pilot minimum, ale ne slepý“** a pojedeme v pořadí: **Stage 10 → 09 → 11 → 13 → 12**.

## Milestone M1 — DoD (splněno)

- Tenant allowlist domén funguje (a je zdokumentované chování při deny).
- Session tokeny mají expiraci a UI umí session obnovit.
- Zprávy se ukládají tenant-scoped (DB i aplikačně), včetně asistenta.
- Lze načíst historii z backendu (paging) deterministicky.
- Widget UI umí: init session, poslat zprávu, zobrazit historii.

---

## Milestone M2 — rozpad do konkrétnějších etap (realizační plán)

### Zvolená strategie

**Pilot minimum, ale ne slepý** = rychle nasadit k pilotním tenantům, ale mít od začátku minimum, které nejvíc šetří čas při ladění a brání průšvihům.

**Pořadí implementace:**

1. **Stage 10 – Observabilita**
2. **Stage 09 – Rate limiting + payload limity**
3. **Stage 11 – Idempotence**
4. **Stage 13 – Security hardening (minimum)**
5. **Stage 12 – Admin tooling (až později)**

### Stage 09 — Rate limiting + payload limity

- **Cíl:** ochrana proti zneužití a runaway nákladům.
- **Backend:**
  - rate limit per tenant (a ideálně per IP) pro `POST /widget/session` a `POST /widget/messages`.
  - limity payloadu (např. max JSON size, max text length).
- **DoD:** limity jsou konfigurovatelné přes env a logují „blocked“ události.

### Stage 10 — Observabilita

- **Cíl:** mít možnost dohledat requesty a incidenty.
- **Backend:**
  - `request_id` (middleware), structured logs (tenant\_id, conversation\_id).
  - základní metriky (počty requestů, latence, error rate).
- **DoD:** pro každý request se loguje request\_id, a chyby jsou dohledatelné.

### Stage 11 — Idempotence pro create message

- **Cíl:** retry-safe POST.
- **Backend:**
  - `Idempotency-Key` header pro `POST /widget/messages`.
  - uložit klíč + výsledek a při duplicitě vracet stejnou odpověď.
- **DoD:** opakované volání se stejným klíčem nevytváří duplicitní řádek.

### Stage 12 — Admin tooling (minimum)

- **Cíl:** základní správa tenantů/domén bez přímého SQL.
- **Backend:**
  - interní admin endpointy (chráněné separátním mechanizmem) pro CRUD tenantů a domén.
  - health/debug endpointy pro diagnostiku.
- **DoD:** lze založit tenant + doménu přes API a je to auditované.

### Stage 13 — Security hardening

- **Cíl:** dotáhnout bezpečnost a stabilitu.
- **Body:**
  - rotace JWT secretu (key versioning / kid), kratší TTL, případně refresh.
  - stricter CORS (origin allowlist napojená na tenants), bezpečné defaulty.
  - základní abuse detection logy (invalid origin, conversation mismatch).
- **DoD:** dokumentovaný threat model pro widget API (stručný).

---

## Milestone M3 — Textový agent (návrh rozkladu na stages)

> Cíl: co nejdřív si „osahat“ reálné problémy agentního jádra (prompting, kontext, tool-calls, limity, observabilita) – zatím čistě textově, nad existujícími conversations/messages.

### Stage 14 — Agent runtime (LLM adapter + prompt kontrakt)

- Vytvořit servis/vrstvu „agent runtime“, která:
  - vezme `conversation_id` + poslední zprávy,
  - sestaví prompt (system + tenant kontext + historie),
  - zavolá LLM (zatím nejjednodušší integrace),
  - uloží odpověď jako `role="assistant"`.
- DoD: deterministické logování (request\_id, tenant\_id, conversation\_id) + základní limity (max tokens, max historie).

### Stage 15 — Tool-calls (první reálné nástroje)

- Zavést bezpečný mechanismus tool-calls:

  - registry nástrojů + Pydantic schémata vstupů/výstupů,
  - validace vstupů, limity, audit log (tenant\_id, conversation\_id, tool\_name, duration).

- **Tool 1: ****\`\`**** (DB, dočasná mock tabulka)**

  - Backend tool čte z dočasné tabulky produktů v PostgreSQL (např. `mock_products`).
  - Minimální funkce: vyhledání podle `query` (název/slug) + vrácení seznamu položek.
  - Tenant scoping: buď `tenant_id` sloupec v mock tabulce, nebo explicitně „global“ data (dokumentovat).
  - Seed dat: 5–20 řádků pro rychlé testování.

- **Tool 2: ****\`\`**** přes MCP (mock nad CSV)**

  - Spustit **jednoduchý MCP server** (lokálně / v dockeru), který poskytne nástroj `get_localities`.
  - Data: CSV soubor lokalit (např. `localities.csv`) + jednoduché filtrování (contains/prefix).
  - Backend funguje jako **MCP client**: při tool-call předá dotaz MCP serveru a výsledek vrátí agentovi.
  - Cíl: ověřit integrační kostru (transport, schémata, timeouty, error handling), ne řešit „dokonalé“ lokality.

- DoD:

  - `get_product` funguje end‑to‑end a je tenant-scoped (nebo explicitně global, ale zdokumentované).
  - `get_localities` funguje přes MCP end‑to‑end (včetně timeoutu a smysluplné chyby při nedostupnosti MCP).
  - Testy pro tool-calls: minimálně happy path + invalid input + MCP down.

### Stage 16 — Orchestrace a „agent loop“ (minimum)

- Přidat jednoduchou smyčku: **LLM → (tool?) → LLM → odpověď**.
- Přidat ochrany:
  - max počet kroků (např. 3–5),
  - timeouty na LLM i nástroje,
  - fallback odpověď, když nástroj selže (a logování chyby).

#### Co znamená „kde běží loop“

„Loop“ je **řídicí logika**, která rozhoduje, jestli se po odpovědi LLM má zavolat nástroj, a pak znovu LLM.

- **Doporučení pro tuto fázi (nejjednodušší a nejčistší):** loop běží **na backendu** uvnitř jednoho API requestu (např. endpoint typu `POST /widget/agent/reply`).

  - Výhody: žádné tajné klíče v prohlížeči, jednotné logování/trace, jedno místo pro limity a ochrany.
  - Nevýhody: request musí doběhnout v rozumném čase (proto step limit + timeout).

- **Později (až bude potřeba):** loop může běžet v **workeru** (async job), zatímco UI jen polluje / streamuje stav.

- DoD:

  - Stabilní běh bez nekonečných smyček.
  - Tool-flow (`get_product`, `get_localities`) projde loopem a skončí odpovědí asistenta.
  - Logy/trace jasně ukazují kroky (LLM call #1, tool call, LLM call #2).

---

### Mini‑spec: `POST /widget/agent/reply` (M3)

> Cíl: jeden endpoint, který v rámci **jednoho requestu** uloží user vstup a vrátí finální odpověď asistenta (včetně případných tool‑calls uvnitř).

#### Auth & headers

- `Authorization: Bearer <widget_session_jwt>` (stejné jako ostatní widget endpointy)
- `Idempotency-Key: <uuid|string>` (doporučeno; po M2/Stage 11 očekáváme retry-safe chování)
- `X-Request-Id` (volitelné; pokud není, server vygeneruje)

#### Request body (JSON)

```json
{
  "conversation_id": "<uuid>",
  "text": "<user text>",
  "options": {
    "max_steps": 4,
    "max_history_messages": 20,
    "timeout_ms": 25000,
    "debug": false
  }
}
```

Poznámky:

- `conversation_id` musí patřit do session v JWT (jinak 403).
- `text` validace: trim, min 1, max dle globálního limitu (payload/text limit z M2).
- `options.*` jsou volitelné; server má bezpečné defaulty a upper-boundy.

#### Side‑effects (DB)

1. Vloží `messages` řádek `role="user"` pro danou `conversation_id`.
2. Spustí agent loop:
   - LLM call #1 (prompt = system + tenant context + poslední N zpráv)
   - (volitelně) 0..k tool callů (`get_product`, `get_localities`)
   - LLM call #2 (finální odpověď)
3. Vloží `messages` řádek `role="assistant"`.

> Tool-call „audit“ minimálně do logů; pokud později bude potřeba, dá se doplnit tabulka `tool_invocations` (zatím není nutné).

#### Response 200 (JSON)

```json
{
  "conversation_id": "<uuid>",
  "user_message": {
    "id": "<uuid>",
    "role": "user",
    "text": "...",
    "created_at": "2026-01-01T12:00:00Z"
  },
  "assistant_message": {
    "id": "<uuid>",
    "role": "assistant",
    "text": "...",
    "created_at": "2026-01-01T12:00:01Z"
  },
  "meta": {
    "request_id": "<string>",
    "steps": 2,
    "tools_used": ["get_product", "get_localities"]
  }
}
```

#### Debug režim (volitelně)

Když `options.debug=true`, přidat `trace` (bez citlivých dat):

- seznam kroků (llm/tool), duration, případně zkrácené výstupy toolů.

#### Error model (JSON)

```json
{ "error": { "code": "...", "message": "...", "request_id": "..." } }
```

Doporučené statusy:

- `400` invalid input
- `401` no/invalid token
- `403` conversation mismatch / forbidden
- `404` conversation not found
- `409` idempotency conflict (pokud bude implementováno tímto způsobem)
- `429` rate limited
- `502/504` LLM/MCP timeout nebo nedostupnost

#### Vazba na existující UI

- UI místo dvojvolání (send message → assistant reply) může volat **jen** `POST /widget/agent/reply`.
- Pro načtení historie zůstává `GET /widget/conversations/{id}/messages`.

#### Vazba na tooly

- `get_product(query)` = DB lookup v `mock_products`.
- `get_localities(query)` = MCP call na lokální MCP server nad `localities.csv` (timeout + fallback).

---

## Milestone M4 — Voice (návrh rozkladu na stages)

> Pozn.: Dává smysl až po M3, protože voice je primárně „transport“, zatímco agent je mozek.

### Technologická volba (doporučení)

- **Reálný cíl pro realtime voice:** použít **LiveKit (SDK + server)**.
- **Učení „raw protokolů“** uděláme jen jako **krátký, time‑boxovaný spike** (na pochopení konceptů), ale **nebudeme stavět produkční řešení na vlastním WebRTC/signaling/TURN**.

**Proč takhle:** WebRTC transport (NAT traversal, UDP porty, TURN, signaling, QoS) je sám o sobě velký projekt. LiveKit to abstrahuje a je přímo navržený pro realtime audio/video a „agents“. (Detaily: server je WebRTC SFU, podporuje self‑hosting i cloud.)

### Stage 16.5 — Voice transport spike (volitelné, max 1–2 dny)

- Cíl: pochopit základy (frames/codec vs. „prostě audio stream“, latence, jitter, VAD/turn taking).
- Realizace: jednoduchý experiment mimo produkční kód (např. websocket stream PCM/Opus do backendu + měření latence).
- DoD: krátká poznámka do docs „co jsem pochopil“ + rozhodnutí potvrzené, že realtime poběží přes LiveKit.

### Stage 17 — Voice API (batch, bez streamingu)

- `POST /voice/transcribe` (audio → text) a `POST /voice/speak` (text → audio)
- Jednoduché soubory (multipart) + tenant-scoped logování.
- Cíl: ověřit STT/TTS provider pipeline, formáty audia, limity a ukládání výsledků – bez realtime složitosti.

### Stage 18 — Voice v UI (push-to-talk, bez realtime)

- UI: nahrát krátký audio blob, poslat na transcribe, vložit text do chat flow.
- Volitelně: přehrát TTS odpověď jako audio soubor.
- Cíl: rychle ověřit end‑to‑end UX bez WebRTC.

### Stage 19 — Realtime streaming (LiveKit)

- **LiveKit Server** (self-host nebo LiveKit Cloud) + **LiveKit JS SDK** ve widgetu.

- Backend přidá endpoint pro vydání LiveKit tokenu (tenant-scoped): např. `POST /widget/voice/token`.

- UI:

  - připojit se do room,
  - publikovat mikrofon track,
  - odebírat audio track agenta (TTS výstup).

- Měřit latenci a fallback chování (network změny, reconnect).

- Měřit latenci a fallback chování.

### Stage 20 — Voice agent orchestrace

- Napojení na agent loop z M3 (tool-calls, limity, logování, guardrails).
- Pro realtime: napojit LiveKit audio stream na STT/turn detection a TTS zpět do room.
- DoD: funguje přerušení (barge‑in), základní turn taking a bezpečné limity.



## Otevřené otázky (držet viditelné)

- Jaký je cílový embed model pro produkci (iframe vs. shadow DOM) a jak to ovlivní integraci voice (LiveKit)?
- Jak a kdy bude řešena per-tenant konfigurace UI (`ui_config`) (kde bude uložená, jak se verzionuje, jak se načítá ve widgetu)?
- Kdy zavést RLS v Postgres (nebo rozhodnout, že ne) — aspoň pro produkční režim?
- Jaké jsou první 1–2 „tenanti“ pro end-to-end pilot (vertikály + minimální test data)?
- M3: jaký LLM provider/model použijeme a jak budeme verzovat prompt kontrakt (system/tenant rules)?
- M3: budeme logovat tool invocations jen do logů, nebo zavedeme tabulku `tool_invocations` (audit/debug)?
- M4: LiveKit self-host vs. LiveKit Cloud (náklady, provoz, SLA)?
- M4: kde poběží „agent participant“ (server participant v room vs. backend pipeline) a jak řešit STT/TTS providery a turn-taking?

## Backlog (parkoviště)

- Export konverzace (tenant audit).
- GDPR/retence: TTL mazání dat, anonymizace.
- Multi-region / enterprise tenant DB-per-tenant.
- RAG / KB pro asistenta (až po text MVP stabilizaci).

