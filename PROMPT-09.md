ÚKOL: Implementuj Stage 09 – Rate limiting + payload limity (ochrana proti zneužití a runaway nákladům).

POVINNĚ PŘEČTI:
- Agent.md
- docs/_template.md
- docs/roadmap-voice-agent.md
- docs/stages/04-widget-auth.md
- docs/stages/05-widget-messages.md
- docs/stages/10-observability.md (request_id + logging; Stage 09 musí logovat „blocked“ události)

Než začneš měnit kód: vytvoř větev `stage/09-rate-limiting` z `main` podle pravidel v docs/Agent.md.

HARD RULES:
- Tenant enforcement se nesmí rozbít (žádný cross-tenant únik).
- Limity musí být konfigurovatelné přes ENV (rozumné defaulty).
- Při blokaci musí vzniknout structured log událost typu „blocked“ (bez citlivých dat) + musí být dohledatelná přes request_id.
- Rate limiting musí být minimálně:
  - per tenant
  - a ideálně per IP (pokud je dostupná)
- Stage není hotová bez: kód + testy + dokumentace (docs/stages/09-rate-limiting.md) + docs/tasks/09-*-codex-tasks.md.

Rozsah (minimální implementace, ale užitečná):
1) **Rate limiting** pouze pro:
   - `POST /widget/session`
   - `POST /widget/messages`
   Limity:
   - per tenant: {route} / time window
   - per IP: {route} / time window (fallback: pokud IP není, loguj a aplikuj jen tenant limit)
   Doporučené chování:
   - při překročení vrať `429 Too Many Requests`
   - přidej `Retry-After` (sekundy; může být hrubý odhad)
   - tělo odpovědi: krátký, stabilní error code (např. `rate_limited`)

2) **Payload limity**
   - Max velikost JSON body (bytes) na těchto POST routách (413 Payload Too Large).
   - Max délka textu zprávy (např. `text`/`message` pole dle existujícího request modelu) — validace na úrovni Pydantic (422/400 podle existujícího stylu).
   - V případě blokace loguj „blocked“ i pro payload limity.

3) **Dokumentace**
   - Přidej `docs/stages/09-rate-limiting.md`:
     - jaké limity jsou, jaké env proměnné, default hodnoty
     - které endpointy jsou chráněné
     - příklady response (429/413) a log event „blocked“
     - omezení (např. in-memory limiter; co to znamená v multi-worker prostředí)

Commit: "feat(security): add rate limiting and payload limits"
