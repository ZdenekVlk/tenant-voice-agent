# Stage 04 – Úkoly (copy-paste checklist)

## 0) Git & příprava
- [ ] Checkout a pull aktuální main/master.
- [ ] Vytvoř branch `stage/04-widget-auth`.
- [ ] Ověř, že Stage 03 existuje a `/widget/session` vrací token (použij lokálně nebo přes test).
- [ ] `git status` musí být čistý před začátkem.

## 1) Dokumentace etapy (povinné)
- [ ] Pokud neexistuje `docs/stages/04-widget-auth.md`, vytvoř ho z `docs/stages/_template.md`.
- [ ] Vyplň metadata (ID, datum, branch, autor).
- [ ] Uveď Scope (DO/DON'T), API kontrakt, error kódy, test plan a “How to test”.
- [ ] Explicitně popiš standard přenosu tokenu:
  - `Authorization: Bearer <jwt>`

## 2) Definuj “Widget Session Context” (tenant + conversation)
- [ ] Přidej datovou strukturu pro kontext (doporučení: Pydantic model nebo dataclass):
  - `tenant_id: UUID`
  - `conversation_id: UUID`
  - volitelně: `expires_at` / `exp`
- [ ] Umístění dle vašeho stylu (např. `backend/src/app/core/types.py` nebo `backend/src/app/api/dependencies/widget_auth.py`).

## 3) Ověření JWT tokenu (signature + exp + shape claims)
- [ ] Implementuj funkci pro dekódování a validaci widget tokenu:
  - vstup: Authorization header
  - výstup: claims / session context
- [ ] Validace:
  - [ ] Header existuje a má tvar `Bearer <token>` → jinak 401
  - [ ] JWT signature validní (`secret`, `alg`) → jinak 401
  - [ ] exp neexpirované → jinak 401
  - [ ] `tenant_id` + `conversation_id` existují a jsou validní UUID → jinak 401
- [ ] Zaveď jednotné chyby:
  - 401 pro chybějící/invalid/expired token
  - (volitelně) 403 pro “token validní, ale přístup odmítnut” (viz DB check níž)

## 4) DB sanity check tokenu (doporučeno)
Cíl: obrana proti stale tokenu / smazané conversation / nesoulad tenant<->conversation.
- [ ] Přidej DB kontrolu:
  - `SELECT tenant_id FROM conversations WHERE id = :conversation_id`
  - [ ] Pokud neexistuje → 403 (nebo 401; zvol a drž konzistentně, zdokumentuj ve stage doc)
  - [ ] Pokud `tenant_id` z DB != `tenant_id` z tokenu → 403
- [ ] Tato kontrola musí být tenant-safe (tady ověřuješ přímo vazbu token↔DB).

## 5) FastAPI dependency `require_widget_session`
- [ ] Vytvoř dependency (doporučený název): `require_widget_session`
  - bere `Request` (kvůli headers) + `db=Depends(get_db)`
  - vrací `WidgetSessionContext`
  - používá JWT decode + DB sanity check
- [ ] Připrav i helpery pro snadné použití:
  - `get_tenant_id(session=Depends(require_widget_session))`
  - `get_conversation_id(session=Depends(require_widget_session))`
  (volitelné, ale urychlí Stage 05/06)

## 6) Chráněný “smoke test” endpoint
Aby Stage 04 byla ověřitelná ještě před `/widget/messages`.
- [ ] Přidej endpoint např. `GET /widget/whoami` (nebo `/widget/session/validate`)
  - [ ] vyžaduje `require_widget_session`
  - [ ] vrací:
    ```json
    {
      "tenant_id": "<uuid>",
      "conversation_id": "<uuid>"
    }
    ```
- [ ] Umísti do vhodného router souboru:
  - buď nově `backend/src/app/api/routes/widget_auth.py`
  - nebo do existujícího `widget_session.py` (pokud už existuje a dává to smysl)
- [ ] Zaregistruj router v `backend/src/app/api/routes/__init__.py`.

## 7) CORS úprava (nutné pro browser)
- [ ] Ověř / uprav CORS middleware tak, aby preflight povolil header `Authorization`.
  - buď přidej `Authorization` do `allow_headers`
  - nebo nastav `allow_headers=["*"]` (pokud je to váš standard)
- [ ] Zapiš do docs, jaké hlavičky jsou očekávané: `Origin` (Stage 03), `Authorization` (Stage 04).

## 8) Logging (minimální observability)
- [ ] Při deny loguj důvod (bez logování celého tokenu!)
  - příklady důvodů: missing_header, invalid_format, invalid_signature, expired, conversation_not_found, tenant_mismatch
- [ ] Při success loguj aspoň `tenant_id`, `conversation_id` (ne token).

## 9) Testy (cheap tests)
- [ ] Unit testy pro parser Authorization header:
  - [ ] missing header → 401
  - [ ] špatný prefix / prázdný token → 401
- [ ] Unit testy pro JWT:
  - [ ] invalid signature → 401
  - [ ] expired token → 401
  - [ ] missing claims / non-uuid → 401
- [ ] Pokud máte DB test infra:
  - [ ] vytvoř tenant + domain + conversation
  - [ ] zavolej `GET /widget/whoami` s validním tokenem → 200
  - [ ] zavolej s tokenem, kde `conversation_id` neexistuje → 403/401 dle volby
  - [ ] zavolej s tokenem, kde `tenant_id` neodpovídá conversation (pokud to jde nasimulovat) → 403
- [ ] Pokud DB infra není:
  - [ ] unit testy + TODO v docs pro integrační testy.

## 10) Manuální ověření (popsat v docs)
- [ ] Postup:
  - [ ] `POST /widget/session` s `Origin: https://allowed.example` → vezmi token
  - [ ] `GET /widget/whoami` s `Authorization: Bearer <token>` → 200
  - [ ] zkus bez `Authorization` → 401
  - [ ] zkus s “Bearer garbage” → 401

## 11) Git deliverables
- [ ] Commity (doporučení):
  - [ ] `feat(widget): add widget token auth dependency`
  - [ ] `feat(widget): add whoami endpoint`
  - [ ] `test(widget): add auth tests` (pokud zvlášť)
  - [ ] `docs(stage): add stage 04 spec`
- [ ] Před finálním výstupem:
  - [ ] `git status` čistý
  - [ ] žádné secrets v commitech

## 12) Povinný závěrečný report (dle Agent.md)
- [ ] Summary (max 8 bodů)
- [ ] Files changed
- [ ] How to test (přesné curl příklady)
- [ ] Tests run + výsledky
- [ ] Follow-ups / Risks (např. Stage 05 `/widget/messages` naváže na `require_widget_session`)
