ÚKOL: Implementuj Stage 10 – Observabilita (request_id, structured logs, základní metriky) pro backend FastAPI.

POVINNĚ PŘEČTI:
- Agent.md
- docs/_template.md
- docs/roadmap-voice-agent.md
- docs/stages/03-widget-session.md
- docs/stages/04-widget-auth.md
- docs/stages/05-widget-messages.md
- docs/stages/08-read-history.md

Než začneš měnit kód: vytvoř větev `stage/10-observability` z `main` podle pravidel v docs/Agent.md.

HARD RULES:
- Tenant enforcement a tenant-scoped dotazy se nesmí rozbít (žádný cross-tenant únik).
- Observabilita nesmí logovat citlivá data (tokeny, secrets, plná request bodies; u textů max bezpečné preview nebo vůbec).
- Stage není hotová bez: kód + testy + dokumentace (docs/stages/10-observability.md) + docs/tasks/10-*-codex-tasks.md.

Co má Stage 10 dodat (minimální, ale užitečné):
1) **request_id**
   - Middleware, který pro každý request:
     - přečte `X-Request-Id` (pokud je) a jinak vygeneruje nový,
     - nastaví `request.state.request_id` (nebo ekvivalent) a vrátí ho v response headeru `X-Request-Id`.
   - request_id musí být dostupné i v error odpovědích.

2) **structured logs**
   - Log formát ve strojově čitelné podobě (ideálně JSON) pro základní události:
     - request started / finished (method, path, status_code, duration_ms, request_id)
     - errors (request_id + error_code, bez citlivých dat)
   - Pokud je k dispozici widget session kontext (Stage 04), logy musí obsahovat i `tenant_id` a `conversation_id`.

3) **základní metriky**
   - Minimálně:
     - počet requestů (counter)
     - latence requestů (histogram/sum+count)
     - error rate jde dopočítat ze statusů (4xx/5xx)
   - Expozice metrik přes endpoint (např. `GET /metrics`) – musí být jasně zdokumentováno, jak ho používat lokálně.

4) **dokumentace**
   - Přidej nový stage dokument `docs/stages/10-observability.md` podle stylu stávajících stages.
   - Vysvětli: co se loguje, jak najít request podle request_id, jak číst metriky, jak zapnout/vypnout (pokud bude feature flag).

Commit: "feat(obs): add request id, structured logs, and metrics"
