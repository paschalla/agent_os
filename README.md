# Agent-OS

![Agent-OS Interface](https://via.placeholder.com/800x400?text=Agent-OS+Interface)

**Agent-OS** is a comprehensive local agentic system designed to bridge the gap between secure, local Linux administration and modern AI capabilities. It consolidates multiple tools—an advanced terminal interface, a safety-focused "Turtle Shell" execution layer, and a web-based chat frontend—into a single, cohesive operating environment for your AI interactions.

## 🚀 Features

- **Local-First Architecture**: Powered by local LLMs (via Ollama) for privacy and offline capability.
- **Turtle Shell Safety Layer**: A robust permission and safety verification system that acts as a guardrail between the AI and your system kernel.
- **Hybrid Intelligence**: Seamlessly route complex queries to cloud models (like Google Gemini) while keeping sensitive system operations local.
- **Multi-Interface Access**:
  - **CLI REPL**: A rich terminal user interface for direct, low-latency interaction.
  - **Web Frontend**: A modern, responsive React/Vite interface for a polished chat experience.
- **Context-Aware**: Intelligently manages context across sessions to maintain continuity without overwhelming the model.

## 🛠️ Prerequisites

Before running Agent-OS, ensure you have the following installed:

- **Python 3.10+**
- **Node.js & npm** (for the frontend)
- **Ollama**: Must be installed and running (`ollama serve`).
  - _Note_: Ensure you have pulled the necessary models (e.g., `llama3`, `mistral`).

## 📥 Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/agent-os.git
    cd agent-os
    ```

2.  **Set up the Python Environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up the Frontend**:

    ```bash
    cd frontend
    npm install
    cd ..
    ```

4.  **Configure Environment**:
    Create a `.env` file in the root directory with your API keys (if using cloud fallbacks):
    ```env
    GOOGLE_API_KEY=your_key_here
    ```

## 🚦 Quick Start

### 1. Start Ollama

Ensure your local LLM backend is running. Open a terminal and run:

```bash
ollama serve
```

### 2. Launch Agent-OS (Backend + REPL)

In a new terminal:

```bash
source venv/bin/activate
python main.py
```

_This starts the core system and the text-based interface._

### 3. Launch the Frontend (Optional)

To use the web interface:

```bash
cd frontend
npm run dev
```

Open your browser to `http://localhost:5173`.

## 🛡️ Safety & Security

Agent-OS implements a **Zero-Trust** approach to system commands. The **Turtle Shell** module analyzes every generated command for potential destruction (file deletion, system config changes) and requires explicit user confirmation for high-risk actions.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and suggest improvements.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <p><sub>Developed with the assistance of <b>Google Gemini 3 Pro</b> and <b>Claude 4.5 Opus</b>.</sub></p>
</div>
