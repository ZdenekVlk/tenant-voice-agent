# Stage <NN>: <Název etapy>

> Soubor pojmenuj: `docs/stages/<NN>-<kebab-case>.md`  
> Příklad: `docs/stages/03-widget-session.md`

## Kontext
- Proč tato etapa existuje (1–3 věty).
- Odkazy na relevantní ADR / schéma DB / předchozí stage.

## Cíl etapy
- 1–3 odrážky, co musí být na konci hotové.

## Scope
### In scope
- Co přesně se bude implementovat.

### Out of scope
- Co se v této etapě dělat nesmí (i kdyby to “dávalo smysl”).

## API kontrakty
> Uveď přesné endpointy, metody, request/response, error kódy.

### Endpointy
- `METHOD /path`
  - Headers:
  - Body:
  - Response 200:
  - Errors: 400/401/403/404/409/422 (dle potřeby)

## Datový model a DB
- Jaké tabulky/sloupce/indexy se používají nebo mění.
- Pokud jsou potřeba migrace: jaké a proč.

## Multitenancy a bezpečnost
- Jak se vynucuje tenant scope.
- Jaké jsou kritické security hrany (Origin/Referer, tokeny, CORS, rate limit – dle etapy).

## Implementační poznámky
- Doporučené soubory / moduly, kterých se změna týká.
- Preferované patterny (dependency injection, services, utils…).

## Akceptační kritéria
- [ ] Kritérium 1 (ověřitelné)
- [ ] Kritérium 2
- [ ] Kritérium 3

## Test plan
### Unit testy
- Co otestovat a kde.

### Integrační / API testy
- Scénáře: happy path / deny / edge cases.
- Pokud test infra chybí, popiš “manual test” (curl) a napiš TODO.

## Jak spustit (lokálně)
- Přesné kroky / příkazy.

## Jak otestovat
- Přesné příkazy (např. `pytest -q`, `curl ...`).
- Očekávané výstupy.

## Známá omezení
- Co zatím není vyřešené.

## TODO / Follow-ups
- 1–5 bodů, co navazuje do další etapy.

## Odkazy
- ADR: …
- Stage předtím: …
- DB schema: …
