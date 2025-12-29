# Agent Instructions (CODEX)

## 0) Kontext projektu
Budujeme multi-tenant SaaS chat widget (zatím pouze text) pro podporu ISP:
- React embed widget na webu zákazníka (ISP)
- Backend: Python + FastAPI
- DB: PostgreSQL (+ pgvector později)
- Agenti: LangChain / LangGraph
- LLM: OpenAI API
- Kromě frontendu (widgetu) běží vše v Docker kontejnerech:
  - backend API
  - PostgreSQL
  - (později) worker pro agenty
  PgAdmin je provozován mimo tento projekt a v tomto repozitáři se nekonfiguruje.


## 1) Zásady (non-negotiables)
- Multi-tenant od začátku: každá DB entita musí mít `tenant_id` a všechny dotazy musí být tenant-scoped.
- Žádné tajné klíče do gitu. Používej `.env` lokálně, udržuj `.env.example`.
- DB schéma spravujeme přes **Alembic migrace**. Změna schématu = nová migrace + `upgrade`.
- Každá etapa musí aktualizovat dokumentaci v `docs/stages/NN-*.md`.
- Změny drž malé a kontrolovatelné.

## 2) Struktura repozitáře (orientačně)
- `backend/` FastAPI aplikace, DB modely, služby
- `frontend/widget/` vložitelný widget
- `docs/stages/` zápisy etap
- `docs/adr/` architecture decision records

## 3) Workflow podle etap
Při zadání nové etapy od uživatele:
1) Implementuj pouze scope, který je výslovně uveden v promptu.
2) Přidej/aktualizuj testy, pokud je to rozumné (cheap tests).
3) Přidej/aktualizuj Alembic migrace (pokud se mění DB).
4) Udržuj `docs/stages/<NN>-<nazev>.md`:
   - Pokud soubor pro danou etapu ještě neexistuje, vytvoř ho z `docs/stages/_template.md`:
     - zkopíruj šablonu
     - doplň všechny placeholdery podle aktuálního zadání (promptu)
     - pojmenuj soubor jako `<NN>-<kebab-case>.md` (např. `03-widget-session.md`)
   - Cíl etapy
   - Co se změnilo
   - Jak spustit
   - Jak otestovat
   - Známá omezení + TODO
5) Připrav návrh commit message (Conventional Commits).

### Požadovaný formát závěrečné odpovědi (vždy česky)
Na konci každého úkolu odpověz **česky** a dodrž tento formát:
- Shrnutí (max 8 řádků)
- Změněné soubory (odrážky)
- Jak spustit
- Jak otestovat
- Poznámky / TODO

## 4) DB a Alembic pravidla
- Používáme Alembic pro migrace (např. `alembic revision --autogenerate -m "..."`).
- Před commitem vždy zkontroluj autogenerate diff (indexy/constraints často vyžadují ruční úpravy).
- Každá migrace musí být deterministická a bezpečná pro opakované spouštění v CI.
- Pokud přidáváš pgvector: vytvoření extension řeš v migraci (např. `op.execute(...)`).

## 5) Jazyk a čeština (UTF-8)
Když vytváříš/edituješ dokumenty nebo komentáře v češtině:
- Vždy používej UTF-8 a správnou diakritiku.
- Piš přirozenou technickou češtinou (ne kostrbatý překlad).
- Dodržuj konzistentní terminologii (např. „konverzace“, „zpráva“, „tenant“, „incident/porucha“ – jednou zvol a drž se).
- V textech nepřepínej zbytečně do angličtiny; anglické názvy jen pro názvy knihoven, API a kódu.
- U nadpisů a vět dodrž českou interpunkci; vyhýbej se „caps lock“ stylu.

## 6) Mermaid a Markdown odkazy (povinné)
Pokud je úkolem vytvořit Mermaid diagram nebo generovat Markdown odkazy:
- Dodrž **instrukce v souboru `create_mermaid_instructions.md`**.
- Minimálně platí:
  - Markdown odkazy piš s URL/cestou v ostrých závorkách: `[Text](</cesta/s mezerami.md>)`
  - Mermaid uzly v hranatých závorkách vždy uvozuj: `A["Text uzlu"]` (ne `A[Text]`)
  - Pro více řádků v popisku uzlu používej `<br/>`, ne surové zalomení řádku.

## 7) Bezpečnost a multitenancy (minimum pro V1)
- `/widget/session` musí validovat `Origin`/doménu vůči `tenant_domains`.
- Session tokeny (JWT) krátkodobé, scoped na `tenant_id` + `conversation_id`.
- Žádný cross-tenant access: i admin routy musí filtrovat podle tenanta.

## 8) Coding standards (stručně)
### Backend (Python/FastAPI)
- Routy v `backend/src/app/api/routes`
- Konfigurace v `backend/src/app/core/config.py`
- Loguj strukturovaně (tenant_id, conversation_id, request_id kde jde)
- Preferuj čitelnost před “framework magií”

### Frontend (React widget)
- Udrž API klienta odděleně (např. `src/api/client.ts`)
- UI drž minimalistické a stabilní
- Mysli na embed (izolace CSS; později iframe/shadow DOM)

## 9) Co NEDĚLAT bez výslovného zadání
- Nepřidávat zbytečnou infra (K8s, observability stack…)
- Nepřepisovat strukturu projektu „pro jistotu“
- Nezavádět nové knihovny bez důvodu uvedeného v promptu

## 10) Git workflow (povinné)
- Používej branch per stage: `stage/NN-name` (např. `stage/03-widget-session`), vždy vytvořenou z aktuálního `main`.
- Základní postup (spusť lokálně a uveď výsledek, pokud je to možné):
  1) `git checkout main`
  2) `git pull --ff-only`
  3) `git checkout -b stage/NN-name`
- Během práce:
  - Dělej malé, logické commity (žádné `WIP`).
  - Před každým commitem:
    - `git status`
    - `git diff` (zkontroluj, že změny odpovídají scope)
    - spusť dostupné testy / kontroly (např. `pytest`, `ruff`, `mypy`), nebo to výslovně uveď, pokud v projektu zatím nejsou.
  - Dodrž Conventional Commits (např. `feat(widget): add widget session endpoint`).
  - Nikdy necommituj secrets (`.env`, klíče, tokeny). Pokud přidáváš konfiguraci, aktualizuj `.env.example` bez tajných hodnot.
- Zakázané bez výslovného pokynu uživatele:
  - `rebase`
  - `reset --hard`
  - `push --force`
- Na konci etapy:
  - Repo musí být čisté (`git status` bez změn).
  - Navrhni nebo rovnou připrav commit(y) a uveď:
    - přesné git příkazy (step-by-step) k pushnutí větve (např. `git push -u origin stage/NN-name`)
    - doporučenou commit message / seznam commitů
    - kontrolní seznam před merge do `main` (tests passing, docs updated, `.env.example` updated, migrace přítomné).
- Pokud dojde ke konfliktu, navrhni bezpečný postup řešení (bez rebase/force).
