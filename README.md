# Agent Orchestrator

A production-grade AI Agent Orchestrator built with **Python 3.11**, **FastAPI**, and **Pydantic v2**.  
The service routes user messages to specialised agents, selects and executes tools, and returns structured responses — with a clean, extensible architecture ready for real LLM integration.

---

## Features

| Area | Detail |
|---|---|
| **Framework** | FastAPI with async lifespan management |
| **Validation** | Pydantic v2 request/response models |
| **Agents** | Declarative `Agent` dataclass with allowed-tool constraints |
| **Tools** | Abstract `BaseTool` with `CalculatorTool` and `MockSearchTool` built in |
| **Orchestration** | `Orchestrator` handles guardrails → agent lookup → tool selection → LLM → response |
| **Guardrails** | Regex-based PII detection (email + phone); raises `PIIDetectedError` before any downstream call |
| **LLM service** | Abstract `BaseLLMService`; ships with `StubLLMService` and a wiring template for `OpenAILLMService` |
| **Logging** | Structured JSON logging via Python's built-in `logging` module |
| **Docker** | Multi-stage `Dockerfile` + `docker-compose.yml` |
| **Tests** | pytest suite covering tools, registry, guardrails, and API endpoints |

---

## Project Structure

```
agent-orchestrator/
├── app/
│   ├── main.py               # FastAPI app factory & lifespan
│   ├── api/
│   │   └── routes.py         # POST /chat, GET /tools
│   ├── core/
│   │   ├── agent.py          # Agent dataclass
│   │   ├── config.py         # Pydantic BaseSettings
│   │   ├── guardrails.py     # PII detection
│   │   ├── orchestrator.py   # Central coordination logic
│   │   └── tool_registry.py  # ToolRegistry
│   ├── models/
│   │   └── schemas.py        # ChatRequest / ChatResponse / ErrorResponse
│   ├── services/
│   │   └── llm_service.py    # BaseLLMService / StubLLMService / OpenAILLMService
│   └── tools/
│       ├── base.py           # BaseTool ABC
│       ├── calculator.py     # CalculatorTool
│       └── mock_search.py    # MockSearchTool
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_guardrails.py
│   ├── test_tool_registry.py
│   └── test_tools.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Quick Start

### Local development

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
uvicorn app.main:app --reload

# API docs available at http://localhost:8000/docs
```

### Docker

```bash
docker compose up --build
# API available at http://localhost:8000
```

---

## API Reference

### `POST /api/v1/chat`

Send a message to a named agent.

**Request**
```json
{
  "message": "Add 5 and 7",
  "agent_name": "general"
}
```

**Response**
```json
{
  "response": "[STUB] I received your message: ...",
  "tool_used": "calculator"
}
```

**Error responses**

| Status | Reason |
|--------|--------|
| 400 | PII detected in message |
| 404 | Agent not found |
| 422 | Validation error or tool not found |
| 500 | Unexpected server error |

### `GET /api/v1/tools`

List all registered tools with their names and descriptions.

### `GET /health`

Liveness probe — returns `{"status": "ok"}`.

---

## Configuration

All settings can be provided as environment variables or in a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Agent Orchestrator` | Human-readable service name |
| `APP_VERSION` | `0.1.0` | Semantic version |
| `DEBUG` | `false` | Enable debug logging |
| `LOG_LEVEL` | `INFO` | Python log level |
| `OPENAI_API_KEY` | _(empty)_ | OpenAI API key (not required in stub mode) |
| `OPENAI_MODEL` | `gpt-4o` | Model identifier |
| `MAX_TOKENS` | `1024` | Max completion tokens |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Extending the System

### Add a new tool

1. Create `app/tools/my_tool.py` and subclass `BaseTool`.
2. Implement `name`, `description`, and `execute`.
3. Register it in `app/main.py`:
   ```python
   tool_registry.register(MyTool())
   ```

### Add a new agent

Call `register_agent(Agent(...))` in the lifespan block in `app/main.py`.

### Plug in a real LLM

Subclass `BaseLLMService`, implement `complete`, and pass it to the `Orchestrator` in `app/main.py`.

---

## License

MIT
