# ADR-0001: Multitenancy a validace domén widgetu

## Status
Navrženo (2025-12-27)

## Kontext
Aplikace je plánovaná jako multi-tenant SaaS: různí zákazníci (tenanti) budou embedovat náš chat widget na své weby.
Musíme zajistit:
- izolaci dat mezi tenanty (žádný cross-tenant únik),
- kontrolu, odkud se widget smí používat (doménová allowlist),
- auditovatelnost (konverzace, incidenty, event log).

Používáme:
- Backend: FastAPI + SQLAlchemy
- DB: PostgreSQL
- Migrace: Alembic

## Rozhodnutí
1) Zvolíme **shared databázi + shared schéma** (jeden set tabulek), kde každá tenant-scope entita obsahuje `tenant_id`.
2) Všechny dotazy v backendu budou **explicitně tenant-scoped** (filtr `tenant_id = ...`).
3) Widget session endpoint (`POST /widget/session`) bude validovat zdroj požadavku:
   - porovná HTTP hlavičku `Origin` (případně `Referer` jako fallback) proti `tenant_domains`.
4) Po úspěšné validaci vytvoříme `conversation` a vydáme krátkodobý session token (např. JWT) se scope:
   - `tenant_id`
   - `conversation_id`
   - expirace v minutách (krátká životnost)
5) **Row-Level Security (RLS)** v Postgres teď nenasazujeme jako povinnost, ale necháváme jako budoucí možnost pro posílení izolace.

## Důsledky
### Pozitivní
- Jednodušší provoz než schema-per-tenant / DB-per-tenant.
- Snadné škálování a jednoduché query patterns.
- Umožní rychlý vývoj a iteraci schématu přes Alembic.

### Negativní / rizika
- Chyba ve filtrování `tenant_id` může vést k úniku dat (proto bude potřeba disciplína a testy).
- Domain allowlist musí být správně implementovaná (Origin může být prázdný u některých situací).
- Bez RLS je izolace primárně na aplikační vrstvě.

## Alternativy, které jsme zvažovali
1) **Schema-per-tenant**  
   + silnější izolace a snazší “export tenant dat”  
   − složitější migrace a provoz, více práce pro každý release

2) **DB-per-tenant**  
   + nejlepší izolace  
   − výrazně složitější orchestrace, vyšší náklady

3) **Shared schema + RLS hned od začátku**  
   + silnější ochrana proti chybám v aplikaci  
   − vyšší komplexita (policies, role management, testování)

## Implementační poznámky
- `tenant_id` je povinný (NOT NULL) u všech tenant-scoped tabulek (konverzace, zprávy, incidenty, event log, KB…).
- U vybraných tabulek, které obsahují sdílené šablony/konfigurace (např. workflow definice), je povoleno `tenant_id = NULL` pro globální záznamy.
- Při čtení těchto “globálních + tenant” tabulek vždy aplikujeme pravidlo:
  1) preferuj záznam s `tenant_id = <aktuální tenant>`
  2) jinak fallback na záznam s `tenant_id IS NULL`

- Doporučené indexy:
  - `(tenant_id, created_at)` na logovacích tabulkách
  - `(tenant_id, conversation_id)` nebo `(tenant_id, id)` podle entity
  - unikátní `(tenant_id, domain)` pro `tenant_domains`
- `POST /widget/session`:
  - získat `Origin` a normalizovat (lowercase, odstranit trailing slash)
  - vyhledat tenant dle `tenant_domains.domain`
  - založit `conversation`
  - vrátit `conversation_id` + token + `ui_config`
- Token musí být krátkodobý; v pozdější etapě doplnit rate-limity per tenant.

### Výjimka: globální záznamy
U některých typů dat (např. workflow šablony, globální konfigurace) potřebujeme sdílet záznam napříč tenanty. Pro tyto tabulky povolujeme:
- `tenant_id IS NULL` pro globální záznamy
- `tenant_id = <uuid>` pro tenant-specifické záznamy

Aplikace při čtení vždy preferuje tenant-specifický záznam a fallbackuje na globální:
1) `tenant_id = <aktuální tenant>`
2) `tenant_id IS NULL`

Pro zachování konzistence používáme partial unique indexy pro globální i tenant záznamy (např. unikátní `key` pro globální řádky a unikátní `(tenant_id, key)` pro tenant řádky).


## Bezpečnostní poznámky
- Nepovažujeme doménovou validaci za „auth“, ale za minimální ochranu proti zneužití widgetu mimo povolené weby.
- Veškeré API pro chat musí vyžadovat token a kontrolovat `tenant_id` a `conversation_id` shodu.
- Doporučeno logovat podezřelé situace:
  - neplatný Origin
  - pokus o přístup k cizí konverzaci
- Globální záznamy (`tenant_id IS NULL`) jsou čitelné pro všechny tenanty, ale zapisovatelné pouze administrátorskou cestou - superadmin (interní správa).

## Otevřené otázky (na později)
- Kdy zapnout RLS (např. po dosažení určité fáze produktu)?
- Jak řešit enterprise tenant s vlastní DB?
- Jak řešit CORS a embed scénáře přes iframe/shadow DOM?

## Související dokumenty
- `docs/stages/03-widget-session.md` (až vznikne)
- `docs/adr/ADR-0002-schema-evolution.md` (pokud bude potřeba doplnit pravidla pro migrace)
