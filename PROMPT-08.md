ÚKOL: Implementuj Stage 08 – GET /widget/conversations/{id}/messages (paging) tenant-scoped.

POVINNĚ PŘEČTI:
- Agent.md
- docs/_template.md
- docs/roadmap-voice-agent.md
- docs/stages/02-db-schema.md
- docs/stages/04-widget-auth.md
- docs/stages/08-*.md (HLAVNÍ SPEC)

Než začneš měnit kód: vytvoř větev `stage/{NN}-{slug}` z `main` podle pravidel v docs/Agent.md.

HARD RULES:
- Tenant enforcement povinný (žádný cross-tenant únik).
- Stage není hotová bez: kód + testy + docs/tasks/08-*-codex-tasks.md.

Commit: "feat(widget): read conversation messages"
