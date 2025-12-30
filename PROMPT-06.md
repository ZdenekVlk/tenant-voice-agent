ÚKOL: Implementuj Stage 06 – vytvoření assistant odpovědi (nejdřív stub/echo) + uložení tenant-scoped.

POVINNĚ PŘEČTI:
- Agent.md
- docs/_template.md
- docs/roadmap-voice-agent.md
- docs/stages/*.md

Nejprve vytvoř `docs/stages/0X-{slug}.md` podle `docs/_template.md` (na základě roadmapy a existujících stage 02–05), potom implementuj kód, testy a vytvoř `docs/tasks/0X-{slug}-codex-tasks.md`.

HARD RULES:
- Žádné nové auth/session rozhodnutí.
- Tenant-scoped všude.
- Stage není hotová bez: kód + testy + docs/tasks/NN-*-codex-tasks.md.

DODEJ:
- PLAN → implementace → testy → docs/tasks → commit.
Commit: "feat(widget): assistant reply stub"
