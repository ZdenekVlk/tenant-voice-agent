# CODEX Tasks - Stage 08: Čtení historie zpráv (paging)

## Status
- [x] T1: Přidat GET endpoint dle Stage 08 spec
- [x] T2: Implementovat DB query tenant-scoped + conversation-scoped
- [x] T3: Paging (limit/offset)
- [x] T4: Testy (happy path + cross-tenant pokus → deny)
- [x] T5: `pytest -q` + výsledek
- [x] T6: `docs/tasks/08-*-codex-tasks.md`
- [ ] T7: Commit `feat(widget): read conversation messages`

## Poznámky
- `conversation_id` v URL musí odpovídat tokenu, jinak 403.
- `pytest -q`: 24 passed in 1.71s
