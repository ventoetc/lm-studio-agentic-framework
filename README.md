# LM Studio Agentic Framework

An autonomous agent framework built on top of a local LLM (via LM Studio) and Streamlit.

## 🌟 Features

*   **Standard Chat**: Talk to your local LLM with history, attachments, and settings.
*   **Agent Mode**: A guided development experience with specialized agents.
    *   **Orientation Agent (Phase 1)**: Clarifies requirements and plans the solution.
    *   **Builder Agent (Phase 2)**: Generates production-ready code based on the plan.
*   **Local Privacy**: All data stays on your machine (using LM Studio).

## 🚀 Getting Started

1.  **Start LM Studio**:
    *   Load a model (e.g., Llama 3, Mistral).
    *   Start the Local Server (default: `http://localhost:1234/v1`).

2.  **Run the App**:
    ```bash
    python -m streamlit run app.py
    ```

3.  **Using Agent Mode**:
    *   Open the Sidebar Settings.
    *   Check **"Enable Agent Mode"**.
    *   Type your request (e.g., "Build a Python calculator").
    *   Follow the agent's guidance!

## 📂 Architecture

*   `app.py`: Main UI and Router integration.
*   `router.py`: Routes messages to Chat or Facilitator.
*   `facilitator/`: Core logic for agent orchestration.
    *   `facilitator.py`: State machine and control loop.
    *   `phases.py`: Enforces rules (e.g., max 4 sentences in Phase 1).
*   `agents/`: Specialized agent personas.
    *   `orientation.py`: Planning & Requirements.
    *   `builder.py`: Code Generation.

## 🛠️ Configuration

Edit `facilitator.yaml` (if available) or `facilitator/config.py` to tune agent behavior.

## 📝 Requirements

*   Python 3.10+
*   `requirements.txt` packages (streamlit, openai, pypdf, etc.)
