ÚKOL: Implementuj Stage 05 – POST /widget/messages (uložení user zprávy tenant-scoped).

POVINNĚ PŘEČTI JAKO PRVNÍ:
- Agent.md
- docs/stages/_template.md
- docs/adr/roadmap-voice-agent.md
- docs/stages/02-db-schema.md
- docs/stages/03-widget-session.md
- docs/stages/04-widget-auth.md
- docs/stages/05-widget-messages.md  (HLAVNÍ SPEC)

HARD RULES:
- Použij require_widget_session PŘESNĚ tak jak je ve Stage 04 (bez změn, bez nových auth rozhodnutí).
- tenant_id a conversation_id ber výhradně z require_widget_session (nesmí být v request body).
- Stage není hotová bez: (a) změn v backend kódu, (b) testů, (c) docs/tasks/05-widget-messages-codex-tasks.md.

DODEJ:
1) PLAN (kroky + seznam souborů)
2) Implementaci endpointu POST /widget/messages dle Stage 05 spec
3) Testy + spusť pytest a uveď výsledek
4) Vytvoř/aktualizuj docs/tasks/05-widget-messages-codex-tasks.md
5) Commit: "feat(widget): create message endpoint"
