"""
Enterprise Intelligence System - Architecture Documentation

This document describes the clean, layered architecture of the application.

## Layered Architecture Pattern

The application follows a clean, layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                   REST API Layer                     │
│              (app/api/routes.py)                     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              Service/Business Logic Layer            │
│     (app/services/query_service.py)                 │
│     (app/services/pdf_service.py)                   │
│     (app/agents/)                                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│           Data Access & RAG Layer                    │
│     (app/rag/retriever.py)                          │
│     (app/rag/uploader.py)                           │
│     (app/core/database.py)                          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            External Services                         │
│     Supabase | DuckDuckGo | yfinance | MCP          │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

### app/core/
**Purpose:** Core configuration, database connections, and application lifecycle.

- `config.py`: Environment variables and validation
- `database.py`: Supabase client factory
- `lifecycle.py`: FastAPI startup/shutdown handlers
- `__init__.py`: Public API exports

### app/api/
**Purpose:** HTTP REST API layer - routes and request/response schemas.

- `routes.py`: All endpoint handlers (GET, POST)
- `schemas.py`: Pydantic models for request/response validation
- `__init__.py`: Package initialization

### app/services/
**Purpose:** Business logic and service orchestration.

- `query_service.py`: Question processing workflow
- `pdf_service.py`: PDF upload and ingestion logic
- `__init__.py`: Package initialization

### app/agents/
**Purpose:** Specialized AI agents for different query types.

- `router.py`: Smart routing logic (which agent to use)
- `rag_agent.py`: Retrieval-Augmented Generation agent
- `web_agent.py`: Web search agent (DuckDuckGo)
- `stock_agent.py`: Financial data agent (yfinance)
- `pdf_agent.py`: PDF generation agent (MCP)
- `__init__.py`: Package initialization

### app/rag/
**Purpose:** Retrieval-Augmented Generation (RAG) system.

- `retriever.py`: Full-text search in Supabase
- `uploader.py`: PDF ingestion and chunking
- `__init__.py`: Package initialization

### app/mcp_server/
**Purpose:** Model Context Protocol (MCP) tool server.

- `server.py`: PDF generation tool exposed via MCP
- `__init__.py`: Package initialization

### app/middleware/
**Purpose:** Request/response processing middleware.

- `rate_limiter.py`: IP-based rate limiting
- `__init__.py`: Middleware registration and setup

### app/utils/
**Purpose:** Reusable utility functions and validators.

- `__init__.py`: Validation helpers (filename, PDF magic bytes, etc.)

### Root-Level App Files

- `main.py`: FastAPI application factory and entry point (40 lines)
- `state.py`: LangGraph state schema definitions
- `graph.py`: LangGraph workflow and agent orchestration

## Data Flow Example: Question Processing

1. **API Layer** (`app/api/routes.py`)
   - Receives POST /ask request
   - Validates request using `AskRequest` schema

2. **Service Layer** (`app/services/query_service.py`)
   - Calls `process_question()` with validated question
   - Orchestrates the workflow

3. **Agent Layer** (`app/agents/`)
   - Router decides which agent to use (router.py)
   - Routes to appropriate agent (rag, web, stock, pdf)
   - Agent returns answer

4. **Data Layer** (`app/rag/` or external services)
   - RAG agent queries Supabase via retriever.py
   - Web agent queries DuckDuckGo
   - Stock agent queries yfinance
   - PDF agent uses MCP server

5. **Response** 
   - Answer is returned in `AskResponse` schema
   - API returns JSON to client

## Key Design Principles

### Single Responsibility
- Each module has ONE clear purpose
- Agents handle different query types
- Services orchestrate business logic
- API routes handle HTTP only

### Dependency Injection
- `get_supabase_client()` is lazy-loaded (core/database.py)
- Configuration is centralized (core/config.py)
- Graph is lazily initialized (graph.py)

### Configuration Management
- All settings in `app/core/config.py`
- Environment variable validation on startup
- No hardcoded values

### Error Handling
- Services raise exceptions with context
- API routes catch and format errors
- Consistent HTTP status codes

### Testing-Friendly Design
- Services are testable in isolation
- No global state except config and cached clients
- Clear input/output contracts

## Technology Stack

- **Framework**: FastAPI (REST API)
- **Workflow**: LangGraph (agent orchestration)
- **Database**: Supabase (PostgreSQL + full-text search)
- **Web Search**: DuckDuckGo Search library
- **Finance**: yfinance (stock data)
- **PDF**: ReportLab (generation) + PyMuPDF (extraction)
- **Tools**: MCP (Model Context Protocol)
- **Validation**: Pydantic
- **Server**: Uvicorn (ASGI)

## Import Guidelines

### Correct Imports (from core)
```python
from app.core import UPLOADS_DIR, CHUNK_SIZE, validate_config
from app.core.database import get_supabase_client
from app.core.lifecycle import lifespan
```

### Correct Imports (from services)
```python
from app.services.query_service import process_question
from app.services.pdf_service import upload_and_ingest_pdf
```

### Correct Imports (from agents)
```python
from app.agents.router import router_node
from app.graph import get_graph
```

## Common Operations

### Adding a New Endpoint
1. Create handler in `app/api/routes.py`
2. Define request/response schemas in `app/api/schemas.py`
3. Extract business logic to `app/services/`
4. Add tests in `tests/`

### Adding a New Agent
1. Create file in `app/agents/agent_name.py`
2. Implement the agent node function
3. Register in `app/graph.py`
4. Update router logic in `app/agents/router.py` if needed

### Adding Configuration
1. Add to `app/core/config.py`
2. Update `.env.example`
3. Export from `app/core/__init__.py`
4. Use in modules as needed

## Scalability Notes

- **Rate Limiting**: Per-IP in memory; for production, use Redis
- **Caching**: LRU cache for clients; consider Redis for distributed caching
- **Sessions**: Stateless; suitable for horizontal scaling
- **Database**: Supabase handles scaling; adjust connection pooling as needed

## Security Considerations

- All file uploads validated (type, size, magic bytes)
- Path traversal prevention via `Path.name`
- Environment variables not hardcoded
- Rate limiting prevents abuse
- Supabase anon key used (not service role key)

For production deployment:
- Enable HTTPS only
- Restrict CORS to your domain
- Use API authentication (OAuth2, API keys)
- Implement proper logging and monitoring
- Use environment variables for secrets
"""
