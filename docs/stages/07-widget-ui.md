# Stage 07: Minimální widget UI

## Kontext
- Potřebujeme minimální UI, které vytvoří widget session, odešle zprávu a zobrazí průběh konverzace lokálně.
- Navazuje na Stage 03 (session), Stage 05 (create message) a Stage 06 (assistant stub).

## Cíl etapy
- UI umí initovat session přes `POST /widget/session` a uložit token.
- UI umí odeslat zprávu přes `POST /widget/messages` s `Authorization: Bearer` tokenem.
- UI umí zobrazit lokální seznam zpráv s optimistickým přidáním.

## Scope
### In scope
- Minimální statická widget UI bez build tooling.
- API klient pro volání existujících endpointů.
- Lokální render seznamu zpráv (optimisticky).

### Out of scope
- Načítání historie zpráv z backendu (Stage 08).
- Automatické volání `POST /widget/messages/assistant` (Stage 06).
- Persist UI stavu mimo runtime.

## API kontrakty
### Endpointy
- `POST /widget/session`
  - Headers:
    - `Origin` / `Referer` (prohlížeč)
  - Body: žádný
  - Response 200:
    ```json
    {
      "conversation_id": "<uuid>",
      "token": "<jwt>",
      "expires_in": 600,
      "ui_config": {}
    }
    ```
  - Errors: 400 `invalid_origin`, 403 `domain_not_allowed`

- `POST /widget/messages`
  - Headers:
    - `Authorization: Bearer <jwt>`
  - Body:
    ```json
    {
      "text": "Ahoj",
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
  - Errors: 400 `invalid_text`, 401/403 podle `require_widget_session`

## Datový model a DB
- Bez změn ve schématu DB.

## Multitenancy a bezpečnost
- Token z `POST /widget/session` se používá pro `POST /widget/messages`.
- Origin/Referer validace se řeší backendem (Stage 03).

## Implementační poznámky
- UI: `frontend/widget/index.html`, `frontend/widget/src/styles.css`.
- Logika: `frontend/widget/src/main.js`.
- API klient: `frontend/widget/src/api/client.js`.

## Akceptační kritéria
- [ ] Uživatel spustí session a vidí `conversation_id`.
- [ ] Uživatel odešle zprávu a vidí ji ve widgetu.
- [ ] `POST /widget/messages` používá Bearer token.
- [ ] Zpráva se zobrazí optimisticky před potvrzením serveru.

## Test plan
### Unit testy
- Žádné (minimální UI bez test infra).

### Integrační / API testy
- Manuální test podle kroků níže.

## Jak spustit (lokálně)
1. Backend podle Stage 03 (Docker Compose + migrace).
2. Přidat `localhost` do `tenant_domains`:
   ```sql
   INSERT INTO tenants (name, slug, is_active) VALUES ('Acme ISP', 'acme', true) RETURNING id;
   INSERT INTO tenant_domains (tenant_id, domain) VALUES ('<tenant_id>', 'localhost');
   ```
3. Spustit statický server:
   ```bash
   cd frontend/widget
   python -m http.server 5173
   ```
4. Otevřít `http://localhost:5173`.

## Jak otestovat
1. Kliknout "Start session".
2. Odeslat text (např. "Ahoj").
3. Ověřit, že se zpráva zobrazí v seznamu.
4. Ověřit v Network tab, že `POST /widget/messages` má `Authorization: Bearer <token>`.

## Známá omezení
- Bez načítání historie zpráv z backendu.
- Bez asistenční odpovědi v UI.

## TODO / Follow-ups
- Stage 08: čtení historie zpráv s pagingem.
- Stage 09+: ochrany a pozorovatelnost.

## Odkazy
- ADR: [ADR-0001](</docs/adr/ADR-0001-multitenancy-a-validace-domen.md>)
- Stage předtím: [Stage 06](</docs/stages/06-assistant-reply.md>)
- Stage předtím: [Stage 05](</docs/stages/05-widget-messages.md>)
