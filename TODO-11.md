# CODEX Tasks — Stage 11: Idempotence (`Idempotency-Key`) pro `POST /widget/messages`

## Cíl
- Umožnit retry-safe vytvoření user zprávy přes `POST /widget/messages`.
- Při opakovaném volání se stejným `Idempotency-Key` neprodukovat duplicitní `messages` řádky.
- Při konfliktu (stejný klíč, jiný payload) vracet stabilní 409 error.

## Guardrails (must)
- [ ] Tenant-scoped dotazy (žádný cross-tenant únik).
- [ ] DB-safe idempotence (řešit přes DB unikátnost/transaction, ne in-memory).
- [ ] Nezalogovat citlivá data (tokeny, celé request bodies; text zprávy nelogovat).
- [ ] Napojit se na Stage 10 structured logs (`request_id` + kontext).

## Návrh API chování
- `Idempotency-Key` header je **volitelný**.
- Pokud je header přítomný:
  - první request vytvoří message a uloží „výsledek“ pro daný klíč
  - další request se stejným klíčem a stejným payloadem vrátí stejný `message_id`
  - stejný klíč s jiným payloadem → 409 `idempotency_key_conflict`

## TODO
- [ ] T1: Projít existující implementaci `POST /widget/messages` (Stage 05):
  - kde je router a handler
  - jak se bere `tenant_id` + `conversation_id` z `require_widget_session`
  - jak vypadá request model (text/metadata)
- [ ] T2: DB design + migrace:
  - přidat tabulku např. `idempotency_keys`
  - sloupce min.: `tenant_id`, `conversation_id`, `key`, `request_hash`, `response_json`, `created_at`
  - unikátní constraint (min.) `(tenant_id, conversation_id, key)`
  - indexy dle ADR-0002
  - Alembic migrace + `alembic upgrade head`
- [ ] T3: Implementovat `request_hash`:
  - stabilní hash z payloadu (např. canonical JSON z validovaného modelu)
  - nepoužívat raw tokeny/hlavičky
- [ ] T4: Implementovat idempotentní flow v handleru `POST /widget/messages`:
  - pokud `Idempotency-Key` chybí → stávající chování beze změn
  - pokud je přítomný:
    - transakčně zajistit, že vznikne max 1 message pro daný klíč
    - uložit response do idempotency záznamu
    - při duplicitě vrátit uloženou response
    - při konfliktu vrátit 409 `idempotency_key_conflict`
- [ ] T5: Structured logs (navazuje na Stage 10):
  - `idempotency_miss` (created)
  - `idempotency_hit` (replayed)
  - `idempotency_conflict` (409)
  - vždy s `request_id` + (kde existuje) `tenant_id`, `conversation_id`
- [ ] T6: Testy:
  - dvakrát `POST /widget/messages` se stejným `Idempotency-Key` a stejným body → stejné `message_id` + v DB jen 1 řádek
  - stejný klíč s jiným `text` → 409 `idempotency_key_conflict`
  - bez `Idempotency-Key` → každé volání vytvoří nový message
  - (bonus) základní test, že i 409 odpověď má `X-Request-Id` (Stage 10), pokud je to v projektu konzistentní
- [ ] T7: Dokumentace:
  - `docs/stages/11-idempotence.md`
  - `docs/tasks/11-*-codex-tasks.md` (tento checklist + poznámky + výsledek `pytest -q`)
- [ ] T8: `pytest -q` + výsledek do docs/tasks
- [ ] T9: Commit `feat(widget): add idempotency for create message`

## Akceptační kritéria
- [ ] Opakované volání `POST /widget/messages` se stejným `Idempotency-Key` nevytvoří duplicitní message.
- [ ] Odpověď na duplicate request vrací stejný `message_id`.
- [ ] Konflikt klíče (jiný payload) vrací 409 `idempotency_key_conflict`.
- [ ] Tenant isolation zůstává zachovaná.
- [ ] Stage 11 je zdokumentovaná a testy procházejí.
