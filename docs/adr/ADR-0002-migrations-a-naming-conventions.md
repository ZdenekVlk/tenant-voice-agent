# ADR-0002: Pravidla pro migrace a naming conventions v Alembic

## Status
Navrženo (2025-12-28)

## Kontext
Projekt je multi-tenant SaaS se sdílenou databází a sdíleným schématem. Každá tenant-scope entita musí být
bezpečně oddělená podle `tenant_id` a migrace musí zůstat dlouhodobě udržitelné (deterministické, čitelné,
bez „magie“ autogenerate diffs).

Současně potřebujeme připravit vzorec pro tabulky, které budou mít **tenant-specifické i globální záznamy**
(`tenant_id IS NULL`) – typicky definice workflow / šablony / konfigurace.

Navazuje na ADR-0001 (multitenancy, validace domén, pravidlo tenant override + global fallback). 

## Rozhodnutí

### 1) Naming conventions (SQLAlchemy + Alembic)
- Použijeme **SQLAlchemy naming conventions** pro deterministická jména constraintů.
- V migracích budeme **explicitně pojmenovávat indexy a constrainty** (nenechávat to na implicitním pojmenování DB),
  aby šel schéma diff dobře číst a downgrade byl spolehlivý.
- Konvence jmen (doporučený pattern):
  - PK: `pk_<table>`
  - FK: `fk_<table>__<col>__<reftable>`
  - UQ: `uq_<table>__<cols>`
  - IX: `ix_<table>__<cols>`
  - CK: `ck_<table>__<name>`
- Pro více sloupců používáme `__` mezi částmi (lepší čitelnost a grepovatelnost).

Doporučený naming_convention dict (pro budoucí autogenerate – patří do `MetaData(...)`):
```python
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s__%(column_0_N_name)s",
    "uq": "uq_%(table_name)s__%(column_0_N_name)s",
    "ck": "ck_%(table_name)s__%(constraint_name)s",
    "fk": "fk_%(table_name)s__%(column_0_N_name)s__%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
```

### 2) Tenant vs global data: pravidlo a databázová ochrana
- Tenant-scope tabulky mají `tenant_id NOT NULL`.
- Tabulky typu „tenant override + global fallback“ mají `tenant_id NULLABLE` a v aplikaci platí pravidlo:
  1) preferuj `tenant_id = <aktuální tenant>`
  2) jinak fallback `tenant_id IS NULL`
- Pro unikátnost v těchto tabulkách používáme **partial unique indexy**:
  - unikát pro globální řádky: `UNIQUE(key) WHERE tenant_id IS NULL`
  - unikát pro tenant řádky: `UNIQUE(tenant_id, key) WHERE tenant_id IS NOT NULL`

Příklad (tabulka `workflow_definitions(key, tenant_id NULLABLE, ...)`):
```python
op.create_index(
    "uq_workflow_definitions__key__tenant_null",
    "workflow_definitions",
    ["key"],
    unique=True,
    postgresql_where=sa.text("tenant_id IS NULL"),
)
op.create_index(
    "uq_workflow_definitions__tenant_id__key__tenant_not_null",
    "workflow_definitions",
    ["tenant_id", "key"],
    unique=True,
    postgresql_where=sa.text("tenant_id IS NOT NULL"),
)
```

**Poznámka:** V Alembic `op.create_index(..., postgresql_where=...)` je preferované před `op.execute("CREATE INDEX ...")`,
protože:
- Alembic to umí správně zapsat do downgrade (přes `op.drop_index(...)`),
- je to čitelnější a méně náchylné na chyby.

### 3) Cross-tenant ochrana na úrovni DB (kompozitní FK)
Aby se minimalizovalo riziko „připíchnutí“ child řádku pod cizí tenant (např. message od tenanta A odkazuje na conversation tenanta B),
používáme v rodičovských tabulkách (conversations, incidents, …) **unikátní constraint na `(tenant_id, id)`** a v child tabulkách
**kompozitní foreign key**:
- `messages(tenant_id, conversation_id) -> conversations(tenant_id, id)`
- `events(tenant_id, incident_id) -> incidents(tenant_id, id)` atd.

To je „cheap“ ochrana, která výrazně snižuje možnost cross-tenant úniku i při aplikační chybě.

### 4) Pravidla pro psaní migrací
- Každá migrace musí mít:
  - deterministický `upgrade()` a `downgrade()`,
  - explicitní názvy indexů/constraintů,
  - žádné závislosti na lokálním stavu DB (kromě `IF NOT EXISTS` u extension).
- Preferujeme:
  - `sa.dialects.postgresql.UUID(as_uuid=True)` + `server_default=sa.text("gen_random_uuid()")`
  - `sa.DateTime(timezone=True)` + `server_default=sa.text("now()")`
  - `sa.dialects.postgresql.JSONB()` + `server_default=sa.text("'{}'::jsonb")`
- Extension:
  - pokud používáme `gen_random_uuid()`, migrace musí vytvořit `pgcrypto`:
    `op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')`
- Indexy:
  - logovací/časové tabulky: `(tenant_id, created_at)` je default.
  - vztahové tabulky: `(tenant_id, <parent_id>, created_at)` pro rychlé načítání historie konverzace.
- „Neautogenerovat“ bez kontroly:
  - `alembic revision --autogenerate` je ok, ale vždy ručně zkontrolovat diff.
  - Partial indexy a kompozitní FK často vyžadují ruční úpravu.

### 5) Naming v Alembic revisions
- Zprávy migrací (message) držet krátké a jednoznačné:
  - `02 init schema`
  - `add uq tenant_domains domain`
  - `add partial uq workflow_definitions`
- Jeden logický krok = jedna migrace (malé, reviewovatelné).
- Revize se netagují datem v názvu souboru (to řeší Alembic), ale message musí být srozumitelná.

## Důsledky
- Schéma bude mít čitelné a stabilní názvy constraintů (snazší debug i ruční zásahy).
- Kompozitní FK zvyšují bezpečnost multi-tenant izolace bez RLS.
- Partial unique indexy umožní čistý „tenant override + global fallback“ pattern bez hacků v aplikaci.

## Související dokumenty
- ADR-0001: Multitenancy a validace domén widgetu
- Stage 02: DB schema (init migrace)
