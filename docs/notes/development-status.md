# Stav vyvoje (M1: Stage 01-08)

## Shrnutí
M1 pokrývá základ multi-tenant backend, session autentizaci pro widget, odesílání zpráv a minimální UI. Historie zpráv je dostupná přes API, ale widget ji zatím nečte.

## Hotove stage
- [Stage 01: bootstrap](</docs/stages/01-bootstrap.md>)
- [Stage 02: DB schema](</docs/stages/02-db-schema.md>)
- [Stage 03: widget session](</docs/stages/03-widget-session.md>)
- [Stage 04: widget auth](</docs/stages/04-widget-auth.md>)
- [Stage 05: widget messages](</docs/stages/05-widget-messages.md>)
- [Stage 06: assistant reply](</docs/stages/06-assistant-reply.md>)
- [Stage 07: widget UI](</docs/stages/07-widget-ui.md>)
- [Stage 08: read history](</docs/stages/08-read-history.md>)

## Funkční rozsah (M1)
- Multi-tenant DB modely a tenant-scoped dotazy.
- Session pro widget s validací domény (Origin) a JWT pro přístup.
- API pro odeslání zprávy uživatele a návrat assistant odpovědi.
- Minimální widget UI pro start session a odesílání zpráv.
- API pro načítání historie konverzace (offset paging).

## Omezení a známé mezery
- Widget UI zatím nenačítá historii zpráv (backend endpoint existuje).
- CORS je v dev režimu permissive; produkční allowlist není hotový.
- Pouze offset paging, bez cursoru a bez celkového počtu zpráv.
- Bez workeru pro agenty a bez integrace hlasu (voice).

## Testy
- Backend unit testy pres `pytest -q` (viz [docs/stages](</docs/stages>)).

## Další kroky (návaznost)
- Stage 09: rate limiting a limity payloadu.
- Stage 11: idempotence pro create message.
- Napojení widgetu na historii zpráv.
