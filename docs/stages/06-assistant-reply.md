# Stage 06: Assistant reply (stub)

## Kontext
- Potrebujeme vracet jednoduchou odpoved asistenta a ulozit ji tenant-scoped.
- Navazuje na Stage 05, kde uzivatel uklada zpravu do `messages`.
- Datovy model `messages` je definovan ve Stage 02.

## Cil etapy
- Pridat endpoint pro vytvoreni assistant odpovedi (stub/echo).
- Ulozit assistant zpravu tenant-scoped s `role="assistant"`.
- Vratit `message_id`, `conversation_id` a text odpovedi.

## Scope
### In scope
- `POST /widget/messages/assistant` napojeny na `require_widget_session`.
- Vytvoreni stub odpovedi z posledni uzivatelske zpravy v konverzaci.
- Persist assistant zpravy do tabulky `messages`.
- Cheap unit/API testy.

### Out of scope
- LLM integrace (to je pozdejsi etapa Stage 06+).
- Cteni historie zprav (Stage 08).
- Idempotence a retry-safety (Stage 11).
- Rate limiting (Stage 09).

## API kontrakty
### Endpointy
- `POST /widget/messages/assistant`
  - Headers:
    - `Authorization: Bearer <jwt>`
  - Body: zadny
  - Response 200:
    ```json
    {
      "conversation_id": "<uuid>",
      "message_id": "<uuid>",
      "text": "Echo: <posledni zprava>"
    }
    ```
  - Errors:
    - 400 `user_message_not_found`
    - 401 `missing_authorization`
    - 401 `invalid_authorization`
    - 401 `invalid_token`
    - 401 `token_expired`
    - 401 `invalid_claims`
    - 403 `conversation_not_found`
    - 403 `tenant_mismatch`

## Datovy model a DB
- Tabulka: `messages` (ze Stage 02).
- SELECT posledni uzivatelske zpravy:
  - `SELECT content FROM messages WHERE tenant_id = :tenant_id AND conversation_id = :conversation_id AND role = 'user' ORDER BY created_at DESC LIMIT 1`
- INSERT assistant zpravy:
  - `tenant_id = session.tenant_id`
  - `conversation_id = session.conversation_id`
  - `role = "assistant"`
  - `content = "Echo: <user_content>"`
  - `meta` pouze pokud sloupec existuje
- Migrace: zadne.

## Multitenancy a bezpecnost
- Endpoint musi pouzivat `require_widget_session` beze zmen.
- `tenant_id` a `conversation_id` se berou vyhradne z dependency.
- Vsechny DB dotazy musi byt tenant-scoped.

## Implementacni poznamky
- Router: `backend/src/app/api/routes/widget_assistant.py`.
- Dependency: `backend/src/app/api/dependencies/widget_auth.py` (`require_widget_session`).
- DB access: existujici DB layer ze Stage 03.

## Akceptacni kriteria
- [ ] Assistant zprava vznikne a ulozi se tenant-scoped (`role="assistant"`).
- [ ] Odpoved vraci `message_id`, `conversation_id` a `text`.
- [ ] Bez tokenu -> 401 (pres `require_widget_session`).
- [ ] Neexistujici conversation pro token -> 403.

## Test plan
### Unit testy
- Stub odpoved se vytvori z posledni uzivatelske zpravy.
- Pokud neexistuje zadna user zprava, vrati 400.

### Integracni / API testy
- Happy path: nejprve `POST /widget/messages`, pak `POST /widget/messages/assistant`.
- Pokud neni DB test infra, pouzij manualni test.

## Jak spustit (lokalne)
1. `.env.example` -> `.env` a nastav `DATABASE_URL` + `WIDGET_SESSION_JWT_SECRET`.
2. Spust Docker Compose:
   - `cd infra`
   - `docker compose up -d --build`
3. Aplikuj migrace:
   - `docker compose exec api alembic upgrade head`

## Jak otestovat
### Unit testy
- `cd backend`
- `pytest -q`

### Manualni test
1. Ziskej token pres Stage 03.
2. Vytvor user zpravu:
   ```bash
   curl -X POST http://localhost:8000/widget/messages \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"text":"Ahoj","metadata":{}}'
   ```
3. Vytvor assistant odpoved:
   ```bash
   curl -X POST http://localhost:8000/widget/messages/assistant \
     -H "Authorization: Bearer <token>"
   ```
4. Over v DB, ze existuje `role="assistant"` s `content` z echo stubu.

## Znama omezeni
- Odpoved je pouze echo posledni user zpravy.
- Bez integrace LLM.

## TODO / Follow-ups
- Stage 07: Widget UI (minimalni).
- Stage 08: Cteni historie zprav s pagingem.
- Stage 11: Idempotence pro vytvareni zprav.

## Odkazy
- ADR: [ADR-0001](</docs/adr/ADR-0001-multitenancy-a-validace-domen.md>)
- Stage predtim: [Stage 05](</docs/stages/05-widget-messages.md>)
- DB schema: [Stage 02](</docs/stages/02-db-schema.md>)
