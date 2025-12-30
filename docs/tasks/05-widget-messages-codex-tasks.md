# CODEX Tasks - Stage 05: POST /widget/messages (ulozeni user zpravy)

## Status
- [x] T1: Najit existujici pattern pro widget routy + DB insert (Stage 03/04)
- [x] T2: Pridat router POST /widget/messages + napojit dependency require_widget_session
- [x] T3: Implementovat insert do messages (tenant_id, conversation_id, role="user", text)
- [x] T4: Osetrit validaci text (minimalne neprazdny po trimu)
- [x] T5: Pridat testy (happy path + bez tokenu -> 401)
- [ ] T6: Spustit testy (pytest -q) a zapsat vysledek
- [x] T7: Vytvorit/aktualizovat docs/tasks/05-widget-messages-codex-tasks.md
- [x] T8: Commit feat(widget): create message endpoint

## Poznamky
- require_widget_session pouzit beze zmen.
- pytest neni dostupny v lokalnim Pythonu (python -m pytest: No module named pytest).
