# CODEX Tasks — Stage 05: POST /widget/messages (uložení user zprávy)

## Cíl
- Přidat `POST /widget/messages`
- Uložit user message tenant-scoped (role="user")
- Vrátit `conversation_id` + `message_id`

## Guardrails (must)
- [ ] Použít `require_widget_session` beze změn (Stage 04)
- [ ] `tenant_id` + `conversation_id` pouze z dependency (ne z body)
- [ ] Bez nových auth mechanik / claimů / headerů
- [ ] Tenant-scoped DB dotazy

## TODO
- [ ] T1: Najít existující pattern pro widget routy + DB insert (Stage 03/04)
- [ ] T2: Přidat router `POST /widget/messages` + napojit dependency `require_widget_session`
- [ ] T3: Implementovat insert do `messages` (tenant_id, conversation_id, role="user", text)
- [ ] T4: Ošetřit validaci `text` (minimálně neprázdné po trimu)
- [ ] T5: Přidat testy (happy path + bez tokenu → 401; případně conversation missing → 403 dle Stage 04)
- [ ] T6: Spustit testy (`pytest -q`) a zapsat výsledek do PR/summary
- [ ] T7: Vytvořit/aktualizovat `docs/tasks/05-widget-messages-codex-tasks.md`
- [ ] T8: Commit `feat(widget): create message endpoint`

## Akceptační kritéria
- [ ] 200 + vytvořený row v `messages` s `role="user"`
- [ ] `messages.tenant_id` odpovídá tokenu
- [ ] `messages.conversation_id` odpovídá tokenu
- [ ] Bez tokenu → 401 (přes require_widget_session)
- [ ] Neplatný/nesedící stav konverzace → 403 dle Stage 04

## Test plan
- `pytest -q`
- (pokud existuje, přidej i konkrétní test soubor a test case názvy)

## Manuální test (curl)
- `POST /widget/session` → získat token
- `POST /widget/messages` s `Authorization: Bearer <token>`
