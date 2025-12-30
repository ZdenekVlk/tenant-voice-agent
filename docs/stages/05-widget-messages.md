# Stage 05: Vytvoření zprávy ve widgetu

## Kontext
- Potřebujeme ukládat uživatelské zprávy v rámci existující widget session (Stage 03/04).
- Navazuje na Stage 04, která zavádí `require_widget_session` a ověřuje `tenant_id` + `conversation_id`.
- Datový model zpráv je definovaný ve Stage 02.

## Cíl etapy
- Přidat endpoint `POST /widget/messages` pro vytvoření zprávy uživatele.
- Uložit zprávu tenant-scoped s `role="user"` a textem z requestu.
- Vrátit `message_id` a `conversation_id` v odpovědi.

## Scope
### In scope
- `POST /widget/messages` s validací těla (povinný `text`, rozumné limity).
- Persist do tabulky `messages` s `tenant_id` + `conversation_id` z `require_widget_session`.
- Volitelná `metadata` (pokud je ve schématu).
- Cheap unit/API testy.

### Out of scope
- Generování odpovědi asistenta (Stage 06).
- Čtení historie (Stage 08).
- Idempotence a retry-safety (Stage 11).
- Rate limiting (Stage 09).

## API kontrakty
### Endpointy
- `POST /widget/messages`
  - Headers:
    - `Authorization: Bearer <jwt>`
  - Body:
    ```json
    {
      "text": "Ahoj, potřebuji pomoct s fakturou.",
      "metadata": {}
    }
    ```
  - Response 200:
    ```json
    {
      "conversation_id": "<uuid>",
      "message_id": "<uuid>"
    }
    ```
  - Errors:
    - 400 `invalid_text` (např. prázdný text po trimu)
    - 401 `missing_authorization`
    - 401 `invalid_authorization`
    - 401 `invalid_token`
    - 401 `token_expired`
    - 401 `invalid_claims`
    - 403 `conversation_not_found`
    - 403 `tenant_mismatch`
    - 422 (validace těla)

## Datový model a DB
- Tabulka: `messages` (ze Stage 02).
- Minimální insert:
  - `tenant_id = session.tenant_id`
  - `conversation_id = session.conversation_id`
  - `role = "user"`
  - `content/text = <request.text>`
  - `metadata` pouze pokud sloupec existuje
- Migrace: žádná, pokud tabulka už obsahuje potřebné sloupce.

## Multitenancy a bezpečnost
- Endpoint musí používat `require_widget_session` beze změn.
- `tenant_id` a `conversation_id` se berou výhradně z dependency, ne z těla requestu.
- Body nesmí umožnit poslat `tenant_id` ani `conversation_id`.

## Implementační poznámky
- Router: `backend/src/app/api/routes/widget_messages.py` (nový modul).
- Dependency: `backend/src/app/api/dependencies/widget_auth.py` (`require_widget_session`).
- DB access: existující DB layer ze Stage 03.

## Akceptační kritéria
- [ ] Validní token + validní body -> 200 a vznikne řádek v `messages` s `role="user"`.
- [ ] Uložený řádek je tenant-scoped (`messages.tenant_id` odpovídá tokenu).
- [ ] `conversation_id` v uloženém řádku odpovídá tokenu.
- [ ] Bez tokenu -> 401 (přes `require_widget_session`).
- [ ] Neexistující conversation pro token -> 403.

## Test plan
### Unit testy
- Validace request modelu (`text` trim, min length).

### Integrační / API testy
- Happy path s tokenem a vložením zprávy.
- Pokud není DB test infra, použij manuální test níže.

## Jak spustit (lokálně)
1. `.env.example` -> `.env` a nastav `DATABASE_URL` + `WIDGET_SESSION_JWT_SECRET`.
2. Spusť Docker Compose:
   - `cd infra`
   - `docker compose up -d --build`
3. Aplikuj migrace:
   - `docker compose exec api alembic upgrade head`

## Jak otestovat
### Unit testy
- `cd backend`
- `pytest -q`

### Manuální test
1. V DB založ tenant + doménu:
   ```sql
   INSERT INTO tenants (name, slug, is_active) VALUES ('Acme ISP', 'acme', true) RETURNING id;
   INSERT INTO tenant_domains (tenant_id, domain) VALUES ('<tenant_id>', 'allowed.example');
   ```
2. Získej token:
   ```bash
   curl -X POST http://localhost:8000/widget/session \
     -H "Origin: https://allowed.example"
   ```
3. Vytvoř zprávu:
   ```bash
   curl -X POST http://localhost:8000/widget/messages \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"text":"Ahoj","metadata":{}}'
   ```
4. Ověř v DB, že zpráva existuje a má správné `tenant_id` + `conversation_id`.

## Známá omezení
- Bez integračních testů s DB (jen manuální ověření).
- Odpověď asistenta není součástí této etapy.

## TODO / Follow-ups
- Stage 06: uložení odpovědi asistenta.
- Stage 08: čtení historie zpráv s pagingem.
- Stage 11: idempotence `POST /widget/messages`.

## Odkazy
- ADR: [ADR-0001](</docs/adr/ADR-0001-multitenancy-a-validace-domen.md>)
- Stage předtím: [Stage 04](</docs/stages/04-widget-auth.md>)
- DB schema: [Stage 02](</docs/stages/02-db-schema.md>)
