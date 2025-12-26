# System Architecture & Configuration

> **Auto-Generated Knowledge File** > _Status: Active_

## Environment Protocols

### 1. AI Model Hosting

- **Host**: Local Machine (`aw`) via Docker.
- **Service**: Docker Container `ollama`.
- **Port**: `11434`.
- **Address**: `http://localhost:11434` (Internal), `0.0.0.0:11434` (External).
- **Wrapper**: `/usr/local/bin/ollama` proxies commands to `docker exec -it ollama ollama ...`.

### 2. Network & Ports

- **Agent-OS API**: Port `8000`.
- **Agent-OS Frontend**: Port `5173`.
- **Zero-Trust**: Do not bind 0.0.0.0 for API unless specifically required for Tailscale access.

### 3. Server Management

- **Startup**: Use `bash scripts/launch_server.sh`.
- **Shutdown**: `Ctrl+C` triggers `cleanup()` which runs `scripts/export_chats.py`.
- **Logs**: `server.log` and `frontend.log` (gitignored).

### 4. Source Control Policy

- **Ignored**: `venv/`, `__pycache__/`, `*.db`, `exports/`.
- **Sync**: Pull with rebase (`git pull --rebase`) to avoid divergent history.
