ÚKOL: Implementuj Stage 11 – Idempotence (`Idempotency-Key`) pro `POST /widget/messages` (retry-safe odesílání zpráv).

POVINNĚ PŘEČTI:
- Agent.md
- docs/_template.md
- docs/roadmap-voice-agent.md
- docs/stages/05-widget-messages.md (kontrakt create message)
- docs/stages/04-widget-auth.md (session/tenant context)
- docs/stages/10-observability.md (request_id + structured logs)
- docs/stages/09-rate-limiting.md (pokud existuje – navazuje na ochrany a logování blokací)

Než začneš měnit kód: vytvoř větev `stage/11-idempotence` z `main` podle pravidel v docs/Agent.md.

HARD RULES:
- Tenant enforcement se nesmí rozbít (žádný cross-tenant únik).
- Idempotence nesmí logovat citlivá data (tokeny, celé request bodies).
- Idempotence musí být DB-safe (žádné „jen in-memory“ řešení). Při souběhu requestů se stejným klíčem nesmí vzniknout duplicitní `messages` řádky.
- Stage není hotová bez: kód + migrace (pokud je potřeba) + testy + dokumentace (docs/stages/11-idempotence.md) + docs/tasks/11-*-codex-tasks.md.

Co má Stage 11 dodat (minimální, ale produkčně smysluplné):

1) **Idempotency-Key pro `POST /widget/messages`**
   - Pokud request obsahuje header `Idempotency-Key`, endpoint musí být retry-safe.
   - Opakované zavolání se stejným klíčem a stejným payloadem:
     - nesmí vytvořit další řádek v `messages`
     - musí vrátit stejnou odpověď (stejné `message_id`, `conversation_id`).

2) **Konflikt klíče**
   - Pokud je stejný `Idempotency-Key` použit s jiným payloadem (např. jiný `text` / `metadata`):
     - vrať 409 `idempotency_key_conflict` (stabilní error code)
     - v logu pouze metadata (request_id, tenant_id, conversation_id, reason), bez textu.

3) **DB model (doporučení)**
   - Přidej novou tabulku např. `idempotency_keys` (nebo obdobně), tenant-scoped, s unikátním klíčem minimálně přes:
     - `(tenant_id, conversation_id, key, scope)` nebo jednodušší `(tenant_id, conversation_id, key)` pro Stage 11.
   - Ulož minimálně:
     - `tenant_id`, `conversation_id`, `key`
     - `request_hash` (hash payloadu, aby šel detekovat konflikt)
     - `response` (např. JSONB s `message_id` a `conversation_id`)
     - `created_at`
   - Vše přes Alembic migraci dle ADR-0002 naming conventions.

4) **Implementační chování (doporučení)**
   - V jedné DB transakci:
     - pokus o insert idempotency záznamu
     - pokud insert uspěl: vytvoř `messages` řádek a ulož response do idempotency záznamu
     - pokud insert neuspěl: načti existující záznam
       - pokud `request_hash` sedí a response existuje: vrať uloženou response
       - pokud `request_hash` nesedí: vrať 409 `idempotency_key_conflict`

5) **Observabilita**
   - Přidej structured log eventy (navazuje na Stage 10):
     - `idempotency_hit` (duplicitní request → vrácena uložená response)
     - `idempotency_miss` (nový klíč → vytvořen message)
     - `idempotency_conflict` (stejný klíč, jiný payload)
   - Logy musí obsahovat `request_id` a pokud existuje session kontext i `tenant_id` + `conversation_id`.

6) **Dokumentace**
   - Přidej `docs/stages/11-idempotence.md`:
     - jak se používá `Idempotency-Key`
     - jaké je chování při retry / konfliktu
     - DB design a omezení (např. retention/cleanup je pozdější follow-up)

Commit: "feat(widget): add idempotency for create message"
