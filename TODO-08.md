# CODEX Tasks — Stage 08: GET messages history (paging)

## Cíl
- Přidat endpoint pro načtení zpráv konverzace
- Paging + správné řazení
- Tenant enforcement

## Guardrails (must)
- [ ] Tenant-scoped dotazy
- [ ] Auth přes existující dependency (dle Stage 04 / spec)
- [ ] Paging parametry validované

## TODO
- [ ] T1: Přidat GET endpoint dle Stage 08 spec
- [ ] T2: Implementovat DB query tenant-scoped + conversation-scoped
- [ ] T3: Paging (limit/offset nebo cursor dle spec)
- [ ] T4: Testy (happy path + cross-tenant pokus → deny)
- [ ] T5: `pytest -q` + výsledek
- [ ] T6: `docs/tasks/08-*-codex-tasks.md`
- [ ] T7: Commit `feat(widget): read conversation messages`

## Akceptační kritéria
- [ ] Vrací jen zprávy dané konverzace pro daného tenanta
- [ ] Paging funguje a je deterministické řazení
