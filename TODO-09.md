# CODEX Tasks — Stage 09: Rate limiting + payload limity

## Cíl
- Omezit zneužití a runaway náklady:
  - rate limit per tenant (a ideálně per IP) pro `POST /widget/session` a `POST /widget/messages`
  - payload limity (max JSON size, max délka textu)
- Vše konfigurovatelné přes ENV + logování „blocked“ událostí (navazuje na Stage 10)

## Guardrails (must)
- [ ] Nezalogovat citlivá data (tokeny, secrets, celé request bodies).
- [ ] Tenant enforcement nesmí být oslaben (žádný cross-tenant únik).
- [ ] Limity musí jít nastavit ENV (defaulty rozumné).
- [ ] Při blokaci musí vzniknout structured log „blocked“ + `request_id`.

## Návrh ENV (doporučení)
- `RATE_LIMIT_SESSION_TENANT` (např. "30/min")
- `RATE_LIMIT_MESSAGES_TENANT` (např. "120/min")
- `RATE_LIMIT_SESSION_IP` (např. "20/min")
- `RATE_LIMIT_MESSAGES_IP` (např. "60/min")
- `MAX_JSON_BODY_BYTES` (např. 65536)
- `MAX_MESSAGE_TEXT_LEN` (např. 2000)

> Pokud má projekt existující settings/config modul, použij ho. Jinak vytvoř minimální, konzistentní konfiguraci.

## TODO
- [ ] T1: Zmapovat existující routy a request modely:
  - `POST /widget/session`
  - `POST /widget/messages`
  - kde získat `tenant_id` + `conversation_id` (z auth/session dependency)
  - odkud brát IP (request.client.host, X-Forwarded-For pokud relevantní — ale opatrně, bez slepé důvěry)
- [ ] T2: Implementovat rate limiter (minimálně in-memory, per-process) + klíče:
  - tenant key: `{tenant_id}:{route}`
  - ip key: `{ip}:{route}`
  - time window (fixed window / sliding — jednoduché, deterministické)
- [ ] T3: Napojit limiter na dvě POST routy:
  - při překročení -> 429 + `Retry-After`
  - vytvořit log event „blocked“ s poli: `reason=rate_limit`, `scope=tenant/ip`, `route`, `tenant_id?`, `conversation_id?`, `request_id`
- [ ] T4: Implementovat payload limit middleware:
  - pokud `Content-Length` > limit -> 413 (bez čtení body)
  - pokud chybí Content-Length -> přečti body jednou, zkontroluj velikost, pak pokračuj (pozor na znovupoužití body ve Starlette/FastAPI)
  - log event „blocked“ s `reason=payload_size`
- [ ] T5: Implementovat max délku textu zprávy:
  - validace v Pydantic modelu (nebo ve route handleru, pokud model není vhodné měnit)
  - error response konzistentní se stávajícím stylem
  - log event „blocked“ s `reason=payload_text_length`
- [ ] T6: Testy:
  - rate limit: nastav nízký limit přes ENV a ověř 429 při (N+1) requestu
  - payload size: pošli body nad limit a ověř 413
  - text length: pošli příliš dlouhý text a ověř 4xx (dle zvoleného chování)
  - (pokud je realistické) ověř `X-Request-Id` přítomný i při 429/413 (Stage 10)
- [ ] T7: Dokumentace:
  - `docs/stages/09-rate-limiting.md`
  - `docs/tasks/09-*-codex-tasks.md` (tento checklist + poznámky + výsledek `pytest -q`)
- [ ] T8: `pytest -q` + výsledek do docs/tasks
- [ ] T9: Commit `feat(security): add rate limiting and payload limits`

## Akceptační kritéria
- [ ] `POST /widget/session` a `POST /widget/messages` mají rate limit per tenant (a pokud možno per IP).
- [ ] Při překročení limitu: 429 + `Retry-After` + structured log „blocked“ + `request_id`.
- [ ] Payload size limit vrací 413 a loguje „blocked“.
- [ ] Max délka textu zprávy je validovaná a blokace je zalogovaná.
- [ ] Limity se nastavují přes ENV a jsou zdokumentované.
- [ ] Test suite pro Stage 09 prochází (`pytest -q`).
