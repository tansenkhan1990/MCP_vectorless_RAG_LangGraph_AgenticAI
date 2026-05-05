"""
Final Project Structure - Clean Architecture Implementation

After complete reorganization, the app directory follows this structure:

## Directory Tree

app/
├── core/                          ✅ Core configuration and services
│   ├── __init__.py               # Public API exports
│   ├── config.py                 # Environment variables, validation
│   ├── database.py               # Supabase client factory
│   └── lifecycle.py              # FastAPI startup/shutdown
│
├── api/                           ✅ REST API Layer
│   ├── __init__.py
│   ├── routes.py                 # All HTTP endpoints
│   └── schemas.py                # Pydantic request/response models
│
├── workflows/                     ✅ LangGraph Orchestration
│   ├── __init__.py               # Exports GraphState, get_graph
│   ├── state.py                  # GraphState schema
│   └── graph.py                  # LangGraph workflow builder
│
├── agents/                        ✅ AI Agents
│   ├── __init__.py
│   ├── router.py                 # Smart routing logic
│   ├── rag_agent.py              # RAG queries
│   ├── web_agent.py              # Web search
│   ├── stock_agent.py            # Financial data
│   └── pdf_agent.py              # PDF generation
│
├── services/                      ✅ Business Logic
│   ├── __init__.py
│   ├── query_service.py          # Question processing
│   └── pdf_service.py            # PDF upload/ingestion
│
├── rag/                           ✅ RAG System
│   ├── __init__.py
│   ├── retriever.py              # Supabase full-text search
│   └── uploader.py               # PDF ingestion & chunking
│
├── mcp_server/                    ✅ MCP Tool Server
│   ├── __init__.py
│   └── server.py                 # PDF generation tool
│
├── middleware/                    ✅ Request Processing
│   ├── __init__.py               # Middleware registration
│   └── rate_limiter.py           # IP-based rate limiting
│
├── utils/                         ✅ Utilities
│   └── __init__.py               # Validation helpers
│
├── main.py                        ✅ FastAPI entry point (40 lines)
│
├── __init__.py                    ✅ Package initialization
│
└── [DEPRECATED - TO BE REMOVED]
    ├── config.py                 → Use: app/core/config.py
    ├── db.py                     → Use: app/core/database.py
    ├── constants.py              → Use: app/core/config.py
    ├── schemas.py                → Use: app/api/schemas.py
    ├── lifecycle.py              → Use: app/core/lifecycle.py
    ├── graph.py                  → Use: app/workflows/graph.py
    └── state.py                  → Use: app/workflows/state.py


## Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│   Presentation Layer                                │
│   app/api/routes.py (HTTP endpoints)               │
│   app/api/schemas.py (Request/Response models)     │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│   Application/Service Layer                         │
│   app/services/ (business logic)                   │
│   app/workflows/ (LangGraph orchestration)         │
│   app/agents/ (specialized agents)                 │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│   Data Access Layer                                 │
│   app/rag/retriever.py (search)                    │
│   app/rag/uploader.py (ingestion)                  │
│   app/core/database.py (Supabase client)           │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│   External Services                                 │
│   Supabase | DuckDuckGo | yfinance | MCP           │
└─────────────────────────────────────────────────────┘
```


## Module Responsibilities

### app/core/
**Responsibility**: Configuration management and core infrastructure

- `config.py`: Load and validate environment variables
- `database.py`: Lazy-loaded Supabase client
- `lifecycle.py`: FastAPI startup/shutdown events
- `__init__.py`: Export public APIs

**Files**: 4 | **Lines**: ~150

---

### app/api/
**Responsibility**: HTTP REST API interface

- `routes.py`: All endpoints (GET /, POST /ask, POST /upload-pdf)
- `schemas.py`: Pydantic models (AskRequest, AskResponse, MessageResponse)
- `__init__.py`: Package init

**Files**: 3 | **Lines**: ~180

---

### app/workflows/
**Responsibility**: LangGraph workflow orchestration

- `state.py`: GraphState schema (shared state between agents)
- `graph.py`: Build and compile the LangGraph workflow
- `__init__.py`: Export GraphState and get_graph()

**Files**: 3 | **Lines**: ~100

---

### app/agents/
**Responsibility**: Specialized AI agents for different query types

- `router.py`: Smart routing based on query content
- `rag_agent.py`: Retrieval-Augmented Generation
- `web_agent.py`: Web search via DuckDuckGo
- `stock_agent.py`: Financial data via yfinance
- `pdf_agent.py`: PDF generation via MCP
- `__init__.py`: Package init

**Files**: 6 | **Lines**: ~400

---

### app/services/
**Responsibility**: High-level business logic orchestration

- `query_service.py`: Process questions through workflow
- `pdf_service.py`: PDF upload and ingestion logic
- `__init__.py`: Package init

**Files**: 3 | **Lines**: ~100

---

### app/rag/
**Responsibility**: Retrieval-Augmented Generation system

- `retriever.py`: Full-text search in Supabase
- `uploader.py`: PDF text extraction and chunking
- `__init__.py`: Package init

**Files**: 3 | **Lines**: ~150

---

### app/mcp_server/
**Responsibility**: Model Context Protocol tool server

- `server.py`: FastMCP PDF generation tool
- `__init__.py`: Package init

**Files**: 2 | **Lines**: ~150

---

### app/middleware/
**Responsibility**: Request/response processing

- `rate_limiter.py`: IP-based rate limiting
- `__init__.py`: Register middleware with app

**Files**: 2 | **Lines**: ~80

---

### app/utils/
**Responsibility**: Reusable utilities and helpers

- `__init__.py`: Validation functions (is_valid_pdf_file, etc.)

**Files**: 1 | **Lines**: ~40

---

### Root-Level App Files

- `main.py`: FastAPI application factory (40 lines)
- `__init__.py`: Package marker

**Files**: 2 | **Lines**: ~40


## Data Flow: Complete Request Path

### Question Processing (POST /ask)

1. **Request** → HTTP
   - Client sends: `{"question": "..."}`

2. **API Layer** → app/api/routes.py
   - Handler: `async def ask(req: AskRequest)`
   - Validates using: `AskRequest` schema
   - Calls: `process_question(req.question)`

3. **Service Layer** → app/services/query_service.py
   - Function: `async def process_question(question: str)`
   - Calls: `get_graph()` from workflows

4. **Workflow Layer** → app/workflows/graph.py
   - Function: `get_graph()` returns compiled LangGraph
   - Invokes: `graph.invoke({"question": question})`
   - State schema: `GraphState` from workflows/state.py

5. **Router Agent** → app/agents/router.py
   - Function: `router_node(state: GraphState)`
   - Decides: which agent to use (rag, web, stock, pdf)
   - Sets: `state["route"]`

6. **Routed Agent** → app/agents/{agent_type}_agent.py
   - RAG Agent: Calls `app/rag/retriever.py`
   - Web Agent: Uses DuckDuckGo
   - Stock Agent: Uses yfinance
   - PDF Agent: Uses MCP server

7. **Data Layer** → varies by agent
   - RAG: `app/core/database.py` → Supabase
   - Web/Stock/PDF: External services

8. **Response** → app/api/routes.py
   - Formats using: `AskResponse` schema
   - Returns: JSON response

---

### PDF Upload (POST /upload-pdf)

1. **Request** → HTTP
   - Client uploads file

2. **API Layer** → app/api/routes.py
   - Handler: `async def upload_pdf(file: UploadFile)`
   - Validates file
   - Calls: `upload_and_ingest_pdf(filename, contents)`

3. **Service Layer** → app/services/pdf_service.py
   - Validates: type, size, magic bytes
   - Calls: `ingest_pdf()` from app/rag/uploader.py

4. **Ingestion** → app/rag/uploader.py
   - Extracts text using PyMuPDF
   - Chunks text
   - Inserts to Supabase via `app/core/database.py`

5. **Response** → app/api/routes.py
   - Returns: success message with chunk count

---

## Import Guidelines

### ✅ Correct Imports

```python
# Configuration
from app.core import UPLOADS_DIR, CHUNK_SIZE, validate_config

# Database
from app.core.database import get_supabase_client

# Lifecycle
from app.core.lifecycle import lifespan

# API
from app.api.schemas import AskRequest, AskResponse
from app.api.routes import router

# Workflows
from app.workflows import GraphState, get_graph
from app.workflows.state import GraphState
from app.workflows.graph import get_graph, build_graph

# Services
from app.services.query_service import process_question
from app.services.pdf_service import upload_and_ingest_pdf

# Agents
from app.agents.router import router_node
from app.agents.rag_agent import rag_node

# RAG
from app.rag.retriever import search_documents
from app.rag.uploader import ingest_pdf

# Middleware
from app.middleware import setup_middleware
from app.middleware.rate_limiter import check_rate_limit
```

### ❌ Deprecated Imports (Do NOT use)

```python
# OLD → NEW
from app.config import ...              → from app.core import ...
from app.db import ...                  → from app.core.database import ...
from app.constants import ...           → from app.core import ...
from app.schemas import ...             → from app.api.schemas import ...
from app.lifecycle import ...           → from app.core.lifecycle import ...
from app.graph import ...               → from app.workflows import ...
from app.state import ...               → from app.workflows import ...
```

---

## Adding New Features

### Add a New REST Endpoint

1. Create handler in `app/api/routes.py`
2. Define schema in `app/api/schemas.py`
3. Extract logic to `app/services/` if complex
4. Add tests in `tests/`

### Add a New Agent

1. Create `app/agents/new_agent.py`
2. Implement: `def new_agent_node(state: GraphState) -> dict:`
3. Import `GraphState` from `app.workflows`
4. Register in `app/workflows/graph.py`
5. Update router logic in `app/agents/router.py`

### Add Configuration

1. Add to `app/core/config.py`
2. Update `.env.example`
3. Export from `app/core/__init__.py`
4. Import: `from app.core import MY_CONFIG`

### Add Middleware

1. Create in `app/middleware/my_middleware.py`
2. Register in `app/middleware/__init__.py`
3. Called in `setup_middleware(app)` in main.py

---

## Project Statistics

| Category | Count |
|----------|-------|
| Directories | 11 |
| Python Packages | 11 |
| Python Modules | 25+ |
| Total Lines (app/) | ~2000 |
| Avg Lines/Module | ~80 |

---

## Best Practices Implemented

✅ **Single Responsibility Principle**: Each module has one clear purpose
✅ **Dependency Inversion**: Services depend on abstractions
✅ **Configuration Management**: Centralized in core/
✅ **Lazy Loading**: Supabase client loaded only when needed
✅ **Error Handling**: Clear exception handling with context
✅ **Validation**: Pydantic models for all inputs
✅ **Logging**: Structured logging throughout
✅ **Testing-Friendly**: Services are independently testable
✅ **Documentation**: Comprehensive docstrings
✅ **Type Hints**: Full type annotations in functions

---

## Next Steps

1. **Remove deprecated files** (see CLEANUP.md)
2. **Run tests** to verify everything works
3. **Update documentation** if structure changes
4. **Add integration tests** for workflows
5. **Add unit tests** for services
"""
