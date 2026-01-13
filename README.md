# LM Studio Agentic Framework

## Overview

This repository contains a **local agentic execution framework** that extends an existing LM Studio chat application with modular agentic capabilities.

### Key Features

- 🔒 **Safe Extension**: Built on top of existing LM Studio chat app without modifying core files
- 🧩 **Modular Architecture**: Agentic logic lives in separate, swappable modules  
- 🔄 **Reset-Safe**: Built-in failure containment and recovery mechanisms
- 🎯 **Two-Phase Execution**: Orientation → Execution workflow enforcement
- 📊 **Session Management**: Persistent chat history and agent session tracking

## Architecture

```
Streamlit UI (existing)
        ↓
Application Router (new, thin)
        ↓
Facilitator (new, modular)
        ↓
Inference Client (existing utils.py)
        ↓
LM Studio
```

## Repository Structure

```
lm-studio-agentic-framework/
├── app.py                    # Existing Streamlit app (minimally touched)
├── utils.py                  # Existing LM Studio client (frozen)
├── router.py                 # NEW: routes requests to chat or facilitator
├── facilitator/              # NEW: all agentic logic lives here
│   ├── __init__.py
│   ├── facilitator.py        # Control loop
│   ├── phases.py             # Phase enforcement
│   ├── reset.py              # Reset + recovery
│   └── config.py             # Reads facilitator.yaml
├── agents/                   # NEW: stateless agent roles
│   ├── orientation.py        # Phase 1 agent (1 paragraph max)
│   ├── builder.py            # Phase 2 execution agent
│   └── critic.py             # Review and validation agent
├── base/                     # NEW: externalized project state
│   ├── project.md
│   ├── decisions.md
│   └── tasks.json
├── sessions/                 # NEW: append-only session summaries
├── artifacts/                # NEW: generated outputs
├── facilitator.yaml          # NEW: control surface configuration
├── requirements.txt
├── .gitignore
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.8+
- LM Studio running locally
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/lm-studio-agentic-framework.git
   cd lm-studio-agentic-framework
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start LM Studio**
   - Launch LM Studio
   - Load your preferred model
   - Ensure API server is running (default: http://localhost:1234)

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   - Open your browser to the displayed URL
   - Toggle agent mode on/off as needed

## Usage

### Standard Chat Mode
- Use like any normal chat application
- Select models, upload files, maintain conversation history

### Agentic Mode
1. **Enable agent mode** in the UI
2. **Phase 1 - Orientation**: Agent provides brief orientation (1 paragraph max)
3. **Phase 2 - Execution**: Agent executes tasks with full capabilities
4. **Monitor progress** through session summaries
5. **Reset if needed** using built-in reset mechanisms

## Safety Features

- **Baseline Protection**: Original chat functionality preserved
- **Modular Design**: Agentic components can be removed without breaking base app
- **Reset Mechanisms**: Automatic reset on failures, timeouts, or manual request
- **Phase Enforcement**: Code-level enforcement of two-phase execution
- **Stateless Agents**: No persistent agent state to corrupt

## Development

### Adding New Agents
1. Create new agent file in `agents/` directory
2. Implement required interface (JSON responses, single role)
3. Register in facilitator configuration
4. Test with reset mechanisms

### Modifying Core Behavior
- **Never modify** `app.py` or `utils.py` directly
- **Use router.py** for routing changes
- **Use facilitator/** for control logic changes
- **Follow PRD specifications** for all changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the PRD specifications
4. Test that base chat still works
5. Submit pull request with detailed description

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check existing issues on GitHub
- Create new issue with detailed description
- Include system information and error logs

---

**Note**: This framework follows strict safety protocols. If agentic modules fail, the base chat application will continue to work unchanged.