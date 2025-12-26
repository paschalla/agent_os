# Agent-OS Operational Standards

> **Global Policy & User Manual** > _Established: December 26, 2025_

This document outlines the operational policies, coding standards, and maintenance procedures for the `agent-os` environment. All agents and users should adhere to these guidelines to ensure system stability and safety.

---

## 🛡️ 1. Zero-Trust Policy

### Library Implementation

- **Trigger**: Before adding any new library or tool.
- **Action**: Do not rely on training data. Perform a fresh search for _current_ best practices.
- **Verification**: Log sources or citations if the implementation is complex.

### Operational Safety

- **Constraint**: Never run global destructive commands (e.g., `docker compose down` on the entire system) when working on a specific service.
- **Isolation**: Always target specific containers or services.

---

## 💻 2. Deployment & Standards

### Docker

- **Version**: Use Docker Compose V2 syntax (no `version:` field).
- **Command**: Use `docker compose` (space, no hyphen).
- **Network**: Ensure non-conflicting ports. `agent-os` uses port `8000` (API) and `5173` (Frontend).

### Git / Source Control

- **Commits**: Use Conventional Commits (e.g., `feat:`, `fix:`, `chore:`).
- **Ignores**:
  - **Never** commit `venv/`, `__pycache__/`, or `.env` files.
  - **Never** commit internal conversation logs (`HANDOFF.md`, `*.db`).
- **Syncing**: If a push is rejected, pull with rebase (`git pull --rebase`) before forcing, unless the remote history is known to be wrong.

---

## 🔧 3. Maintenance Procedures

### System Cleanup (RAM Dump)

If the system becomes sluggish or IDE processes hang:

1.  **Kill Dev Processes**: Terminate `vite`, `uvicorn`, `python` (main.py).
2.  **Reload Window**: In VS Code, use `Ctrl+Shift+P` -> `Reload Window` to free visual editor RAM.
3.  **Command**: You can run the automated workflow: `@agent /maintenance`.

### Knowledge Base

- **Storage**: Conversations are stored in `~/.andy-os/memory.db`.
- **Export**: To create a readable knowledge base, run:
  ```bash
  python3 scripts/export_chats.py
  ```
- **Usage**: The agent can "read" these exported files to recall facts (e.g., "What was the secret code?").

---

## 🚀 4. Workflow Automation

(See `.agent/workflows` for automated scripts)

---

## 🤖 5. AI System Context (Global Memory)

To ensure immediate alignment, add this efficient block to your **Custom Instructions**:

```markdown
# ⚡ Agent-OS Core Protocol

**System State**: Local-First | Docker-Backed | Knowledge-Driven

- **Infrastructure**: Ollama (Docker) running on `aw` (localhost:11434).
- **Tools**: Native `ollama` CLI wrapper ready.
- **Ops**:
  - **Clean**: `@agent /maintenance` (Kills vite/uvicorn).
  - **Memory**: Knowledge auto-exports to `exports/`. Check it first.
- **Code Law**: Zero-Trust library installs. No `venv` in Git.
```
