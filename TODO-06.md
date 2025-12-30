# CODEX Tasks — Stage 06: Assistant reply (stub/echo) + persist

## Cíl
- Vytvořit assistant odpověď (stub/echo)
- Uložit assistant message tenant-scoped (role="assistant")

## Guardrails (must)
- [ ] Bez nových auth mechanik
- [ ] Tenant-scoped DB dotazy
- [ ] Konzistentní error chování s předchozími stages

## TODO
- [ ] T1: Najít pattern pro ukládání messages (Stage 05)
- [ ] T2: Implementovat stub odpověď asistenta (dle Stage 06 spec)
- [ ] T3: Persist assistant message (role="assistant") tenant-scoped
- [ ] T4: Testy (minimálně: uloží se assistant zpráva; tenant enforcement)
- [ ] T5: `pytest -q` + výsledek
- [ ] T6: `docs/tasks/06-*-codex-tasks.md`
- [ ] T7: Commit `feat(widget): assistant reply stub`

## Akceptační kritéria
- [ ] Assistant zpráva vznikne a uloží se tenant-scoped
- [ ] Historie konverzace obsahuje user + assistant zprávu (v DB)
