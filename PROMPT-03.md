# Stage 03 – Úkoly (copy-paste checklist)

## 0) Git & příprava
- [ ] Vytvoř branch `stage/03-widget-session` z aktuálního main/master.
- [ ] Ověř čistý stav repa (`git status`) a že Stage 02 migrace jsou aplikovatelné.

## 1) Dokumentace etapy (povinné)
- [ ] Pokud neexistuje `docs/stages/03-widget-session.md`, vytvoř ho z `docs/stages/_template.md`.
- [ ] Vyplň metadata (ID, datum, branch, autor).
- [ ] Sepiš Scope (DO/DON'T), API kontrakt, error kódy, test plan a “How to test”.

## 2) Minimální DB layer (protože zatím není)
- [ ] Přidej `backend/src/app/core/db.py`:
  - [ ] SQLAlchemy engine + sessionmaker podle `DATABASE_URL`
  - [ ] FastAPI dependency `get_db()` (yield session, close)
  - [ ] Minimalní pattern použití v routách (bez ORM magie)

## 3) Config (env)
- [ ] Rozšiř `backend/src/app/core/config.py` o:
  - [ ] `WIDGET_SESSION_JWT_SECRET`
  - [ ] `WIDGET_SESSION_JWT_ALG` (default např. `HS256`)
  - [ ] `WIDGET_SESSION_TTL_MINUTES` (default např. 10)
- [ ] Aktualizuj `.env.example` (bez tajných hodnot).

## 4) Normalizace domény z Origin/Referer
- [ ] Přidej `backend/src/app/utils/origin.py`:
  - [ ] Vstup: `origin` + `referer` string (může být None)
  - [ ] Výstup: hostname (lowercase, bez portu, bez cesty, bez trailing slash)
  - [ ] Pokud nelze vyparsovat → `None`
  - [ ] Ošetři invalid URL a prázdné hodnoty

## 5) JWT utilita pro widget session
- [ ] Přidej `backend/src/app/core/security.py`:
  - [ ] funkce pro vytvoření krátkodobého JWT tokenu
  - [ ] claims: `tenant_id`, `conversation_id`, `iat`, `exp`
  - [ ] návrat: `(token, expires_in_seconds)`

## 6) Endpoint `POST /widget/session`
- [ ] Přidej router `backend/src/app/api/routes/widget_session.py`:
  - [ ] `POST /widget/session`
  - [ ] Získej `Origin` (fallback `Referer`) z hlaviček
  - [ ] Normalizuj hostname přes `utils/origin.py`
  - [ ] Pokud hostname chybí/nevalidní → vrať konzistentní chybu (doporučení: 400 nebo 403; zvol a zdokumentuj)
  - [ ] Lookup tenant: `SELECT tenant_id FROM tenant_domains WHERE domain = :hostname`
  - [ ] Pokud nenalezen → 403
  - [ ] Vytvoř `conversation` pro tenant (`INSERT INTO conversations ... RETURNING id`)
  - [ ] Vygeneruj JWT token (scoped na tenant + conversation)
  - [ ] Response 200:
    ```json
    {
      "conversation_id": "<uuid>",
      "token": "<jwt>",
      "expires_in": 600,
      "ui_config": {}
    }
    ```
  - [ ] Loguj strukturovaně alespoň: domain, tenant_id (pokud je), conversation_id (pokud je), důvod deny

- [ ] Zaregistruj router v `backend/src/app/api/routes/__init__.py` přidáním do `routers = [...]`.
- [ ] Ověř, že endpoint je dostupný přes `backend/src/app/main.py` (router registry pattern).

## 7) CORS (minimální, pro widget v browseru)
- [ ] Přidej/ověř CORS middleware tak, aby browser mohl zavolat `POST /widget/session`.
- [ ] Neřeš cookie auth; token se vrací v JSON.
- [ ] Poznámka do docs: CORS není bezpečnost, bezpečnost je allowlist domén + token (zapsat v Stage doc).

## 8) Testy (cheap tests)
- [ ] Unit testy pro normalizaci domény:
  - [ ] uppercase, trailing slash, port, path, invalid URL, chybějící hlavičky
- [ ] Pokud máte integrační test infra pro DB:
  - [ ] Happy path: validní domain → 200 + conversation uložená v DB s tenant_id
  - [ ] Deny: neznámá domain → 403
- [ ] Pokud infra není:
  - [ ] Přidej aspoň unit testy a do docs napiš TODO pro integrační testy.

## 9) Manuální ověření (popsat v docs)
- [ ] Postup:
  - [ ] Spusť docker compose (infra)
  - [ ] Aplikuj migrace (alembic upgrade head)
  - [ ] Vlož test tenant + tenant_domain do DB
  - [ ] Zavolej endpoint s `Origin: https://allowed.example`
  - [ ] Ověř 200 + token + že `conversations` obsahuje nový řádek pro tenant

## 10) Git deliverables
- [ ] Commity podle Conventional Commits (doporučení):
  - [ ] `feat(widget): add widget session endpoint`
  - [ ] případně samostatně `test:` / `docs:` pokud to dává smysl
- [ ] Před finálním výstupem:
  - [ ] `git status` čistý
  - [ ] žádné secrets v commitech
- [ ] Na konci napiš krokový návod git příkazů pro push + návrh merge checklistu.

## 11) Povinný závěrečný report (dle Agent.md)
- [ ] Shrnutí (max 8 řádků)
- [ ] Změněné soubory
- [ ] Jak spustit
- [ ] Jak otestovat
- [ ] Poznámky / TODO
