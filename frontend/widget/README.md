# Widget (minimal UI)

Minimal static widget UI for Stage 07. It starts a session, sends messages, and renders a local message list.

## Quick start
1. Serve the folder so the browser has a proper Origin:
   ```bash
   cd frontend/widget
   python -m http.server 5173
   ```
2. Add `localhost` into `tenant_domains` and run the backend.
3. Open `http://localhost:5173` and click "Start session".

## Notes
- The widget uses `POST /widget/session` and `POST /widget/messages`.
- History loading is not implemented yet (Stage 08).
