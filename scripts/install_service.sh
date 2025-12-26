#!/bin/bash
set -e

SERVICE_FILE="/etc/systemd/system/agent-os.service"
USER="andy"
WORKING_DIR="/home/andy/proj/agent-os"
VENV_PYTHON="$WORKING_DIR/venv/bin/python"

echo "Creating systemd service file..."

cat <<EOF | sudo tee $SERVICE_FILE
[Unit]
Description=Agent-OS Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$WORKING_DIR
ExecStart=$VENV_PYTHON src/interface/server.py
Restart=always
RestartSec=5
Environment="PATH=$WORKING_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="OLLAMA_HOST=http://localhost:11434"

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Service created at $SERVICE_FILE"
echo "You can now start it with: sudo systemctl start agent-os"
echo "Enable boot start with: sudo systemctl enable agent-os"
