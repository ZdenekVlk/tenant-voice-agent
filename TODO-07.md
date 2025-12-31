# CODEX Tasks — Stage 07: Minimální widget UI

## Cíl
- UI umí založit session
- UI umí poslat message
- UI umí zobrazit průběh konverzace (minimálně lokálně / základně)

## Guardrails (must)
- [ ] Používat existující endpointy (Stage 03/05/06)
- [ ] Žádné změny backend kontraktů bez stage spec

## TODO
- [ ] T1: Napojit init: `POST /widget/session` → uložit token + conversation_id
- [ ] T2: Odeslání: `POST /widget/messages` s Authorization Bearer token
- [ ] T3: Render messages (minimálně lokální seznam + optimistické přidání)
- [ ] T4: Smoke test / manuální test kroky (v docs/tasks)
- [ ] T5: `docs/tasks/07-*-codex-tasks.md`
- [ ] T6: Commit `feat(widget-ui): minimal chat widget`

## Akceptační kritéria
- [ ] Uživatel odešle text a vidí ho ve widgetu
- [ ] Token je používán pro volání messages endpointu
