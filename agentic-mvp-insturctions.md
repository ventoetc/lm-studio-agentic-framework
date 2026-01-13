# Local Agentic Execution Framework

## MVP PRD — **Refactored to Build on Existing LM Studio Chat App**

---

## 0. Executive Intent (Read First)

This PRD **assumes an existing, working LM Studio chat application** (Streamlit + Python) is already in place.

The goal is **not to rebuild or replace it**, but to:
- Treat it as a **stable foundation**
- Add a **modular control layer** on top
- Enable agentic behavior **without breaking existing functionality**
- Make all new logic removable, swappable, and reset-safe

If something new breaks, the base chat app must still run unchanged.

---

## 0.1 Mandatory Git Baseline & Safety Rules (DO THIS FIRST)

These steps are **required** and are part of the specification. They exist to protect the working application.

### Baseline Commit (Non‑Optional)
Before adding **any** new files or logic:

```bash
git init
git add .
git commit -m "Baseline: working LM Studio Streamlit chat app"
```

This commit is the **golden rollback point**.

### Change Policy
- Existing files (`app.py`, `utils.py`, `README.md`, etc.) are **frozen**
- All new functionality must be added in **new modules only**
- Any change to core files must be:
  - Minimal
  - Reversible
  - Done after the baseline commit

If this rule is violated, the MVP is considered invalid.

### Tooling Note (Trae / Claude Desktop)
Because Trae and Claude Desktop have Git capabilities:
- Always verify you are on a clean working tree before scaffolding
- Commit immediately after scaffolding new modules
- Never allow an agentic tool to rewrite or refactor existing files

---


## 1. What Already Exists (Baseline Assumption)

The existing system already provides:
- A working **OpenAI-compatible LM Studio client**
- Model discovery and selection
- Streaming responses
- File and image attachments
- Persistent chat history
- A functional Streamlit UI

This existing code is considered **stable and frozen**.

---

## 2. Core Rule (Non-Negotiable)

> **The existing chat app is the base system.**
> 
> All agentic functionality must be added as **modules that wrap or intercept**, never as modifications that entangle core code.

If a module is removed, the original chat must still work.

---

## 3. New Architecture (Layered, Not Rewritten)

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

### Responsibilities by Layer

- **Streamlit UI**: Input, files, display only
- **Application Router**: Decides standard chat vs agentic flow
- **Facilitator**: Control, agents, phases, reset
- **Inference Client**: Raw LLM calls only (existing code)

---

## 4. Repository Layout (Modular by Design)

```
llm-chat/
├── app.py                # Existing Streamlit app (minimally touched)
├── utils.py              # Existing LM Studio client (frozen)
├── router.py             # NEW: routes requests to chat or facilitator
│
├── facilitator/          # NEW: all agentic logic lives here
│   ├── __init__.py
│   ├── facilitator.py    # Control loop
│   ├── phases.py         # Phase enforcement
│   ├── reset.py          # Reset + recovery
│   └── config.py         # Reads facilitator.yaml
│
├── agents/               # NEW: stateless agent roles
│   ├── orientation.py
│   ├── builder.py
│   └── critic.py
│
├── base/                 # NEW: externalized project state
│   ├── project.md
│   ├── decisions.md
│   └── tasks.json
│
├── sessions/             # NEW: append-only session summaries
├── artifacts/            # NEW: generated outputs
│
├── facilitator.yaml      # NEW: control surface
├── requirements.txt
└── README.md
```

Key principle: **Nothing inside `facilitator/` or `agents/` is allowed to import Streamlit.**

---

## 5. Application Router (Critical Isolation Layer)

### Purpose
The router protects the base chat app from agentic complexity.

### Behavior
- If agent mode is **off** → route directly to existing chat logic
- If agent mode is **on** → route to Facilitator

### Benefits
- Safe fallback
- Easy disable/enable
- Zero-risk experimentation

---

## 6. Inference Client Contract (Frozen)

The existing `utils.py` client is wrapped, not changed.

```python
def llm_call(messages, tools=None):
    """Thin wrapper around existing LM Studio client."""
    ...
```

Rules:
- No agent logic
- No retries
- No memory
- No policy

If this file changes, the MVP is invalid.

---

## 7. Facilitator Responsibilities (New, Modular)

The Facilitator:
- Loads project base on session start
- Selects agent role
- Calls `llm_call()`
- Enforces Phase 1 vs Phase 2
- Validates JSON schemas
- Handles reset and recovery
- Writes session summaries

The Facilitator **does not** render UI or reason deeply.

---

## 8. Agent Model (Stateless, Replaceable)

Each agent:
- Has one role
- Has one system prompt
- Returns JSON only
- Has no memory

Removing an agent must not affect others.

---

## 9. Two-Phase Execution (Unchanged)

### Phase 1 — Orientation
- Max 1 paragraph OR 4 sentences
- No lists, no solutions

### Phase 2 — Execution
- Unlimited output
- Requires explicit trigger

Phase enforcement is **code-level**, not prompt-based.

---

## 10. Reset & Failure Containment (Mandatory)

Reset triggers:
- Invalid JSON
- Timeout
- Phase violation
- Manual reset

Reset behavior:
1. Abort agent execution
2. Clear agent-local state
3. Reload base files
4. Return system to safe state

Base chat must remain usable after reset.

---

## 11. What Is Explicitly Removed From Scope

- Embeddings
- Vector databases
- Auto-memory
- Planner graphs
- Parallel agent execution
- UI redesign

These are intentionally excluded to preserve stability.

---

## 12. MVP Success Criteria (Revised)

The MVP is successful if:
- Existing chat app still works unchanged
- Agent mode can be toggled on/off
- Agents run without corrupting base chat
- Reset always restores a working system
- All new logic lives outside core files

---

## 13. How to Use This PRD

This document replaces earlier versions.

Give it verbatim to:
- Claude Desktop
- Codex
- Any agentic coding tool

Instruction:
> "Extend the existing LM Studio chat app per this PRD. Do not rewrite core files. Add new modules only."

---

## 14. Final Design Guarantee

This design guarantees:
- Safe iteration
- No vendor lock-in
- Easy rollback
- OSS-friendly evolution

If agentic modules fail, the chat app still works.

---

## 15. Agentic Tool Execution Rules (Kimi / Trae / Claude Desktop)

These rules are **mandatory** when using agentic coding tools (including **Kimi via Trae**).

### Allowed Actions (Initial Pass Only)
- Create directories
- Create files
- Add minimal stubs and placeholders
- Wire imports at a high level

### Explicitly Disallowed (Until Told Otherwise)
- Implementing full business logic
- Optimizing or refactoring code
- Introducing inheritance trees or complex base classes
- Modifying existing core files (`app.py`, `utils.py`, etc.)
- Adding frameworks or abstractions not specified in this PRD

### Execution Instruction to Provide the Tool (Verbatim)

> "Follow this PRD exactly. Scaffold files and directories only. Do not implement full logic or refactor existing code. Stop after scaffolding is complete."

### Rationale
Agentic tools (especially Kimi) tend to **over-complete implementations**. This rule ensures:
- Clean Git commits
- Predictable behavior
- Safe rollback points
- Human-controlled sequencing

Violation of these rules invalidates the MVP.
