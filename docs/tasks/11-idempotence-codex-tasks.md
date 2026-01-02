# CODEX Tasks - Stage 11: Idempotence (`Idempotency-Key`) pro `POST /widget/messages`

## Status
- [x] T1: Projít implementaci `POST /widget/messages` (router, handler, session kontext)
- [x] T2: DB design + migrace (`idempotency_keys`)
- [x] T3: Implementovat `request_hash`
- [x] T4: Implementovat idempotentní flow v handleru
- [x] T5: Structured log eventy (`idempotency_miss`, `idempotency_hit`, `idempotency_conflict`)
- [x] T6: Testy pro idempotenci
- [x] T7: Dokumentace `docs/stages/11-idempotence.md`
- [x] T8: `pytest -q` + výsledek
- [ ] T9: Commit `feat(widget): add idempotency for create message`

## Poznámky
- `request_hash` je hash canonical JSON (`text`, `metadata`) z validovaného payloadu.
- `pytest -q`: 26 passed in 1.98s
