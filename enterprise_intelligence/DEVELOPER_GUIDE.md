"""
Developer Guide - Enterprise Intelligence System

Quick navigation and common tasks for working with this codebase.

## Project Structure at a Glance

```
enterprise_intelligence/
├── app/                       # Application code
│   ├── core/                 # Core configuration & services
│   ├── api/                  # REST API routes
│   ├── services/             # Business logic
│   ├── agents/               # AI agents
│   ├── rag/                  # RAG system
│   ├── mcp_server/           # PDF generation tool
│   ├── middleware/           # Request processing
│   ├── utils/                # Utilities
│   ├── main.py               # Entry point
│   ├── state.py              # LangGraph state
│   └── graph.py              # LangGraph workflow
│
├── schema/                    # Database schema
├── uploads/                   # PDF uploads & reports
├── ARCHITECTURE.md            # Architecture documentation
├── CLEANUP.md                 # Deprecated files cleanup
├── README.md                  # Project overview
├── main.py                    # Server startup
├── pyproject.toml             # Dependencies
└── .env.example               # Configuration template
```

## Quick Start

### 1. Setup
```bash
cd enterprise_intelligence
cp .env.example .env
# Edit .env with your credentials
uv pip install -r requirements.txt
```

### 2. Run the Server
```bash
python main.py
# OR
uvicorn app.main:app --reload
```

### 3. Test the API
```bash
# Health check
curl http://localhost:8000/

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the stock price of Apple?"}'

# Upload a PDF
curl -X POST http://localhost:8000/upload-pdf \
  -F "file=@document.pdf"
```

## Where to Find Things

### I need to...

#### Add a new REST endpoint
1. Add handler function to `app/api/routes.py`
2. Define request/response in `app/api/schemas.py`
3. Extract business logic to `app/services/`
4. Document in docstring

#### Create a new AI agent
1. Create `app/agents/my_agent.py`
2. Implement agent function: `def my_agent_node(state: GraphState) -> dict:`
3. Register in `app/graph.py`
4. Update router in `app/agents/router.py`

#### Add configuration setting
1. Add to `app/core/config.py`
2. Update `.env.example`
3. Export from `app/core/__init__.py`
4. Use in code: `from app.core import MY_SETTING`

#### Handle errors properly
1. Let exceptions propagate to service layer
2. Services catch and log with context
3. Routes catch ServiceException and format HTTP response
4. Always include error details in logs

#### Validate user input
1. Use Pydantic models in `app/api/schemas.py`
2. Define validators on model fields
3. Pydantic raises ValidationError automatically
4. Routes catch ValidationError and return 422

### Configuration

All settings in `app/core/config.py`:
- `OPENAI_BASE_URL`: LLM endpoint
- `OPENAI_API_KEY`: LLM API key
- `SUPABASE_URL`, `SUPABASE_KEY`: Database
- `MAX_UPLOAD_SIZE_MB`: File upload limit
- `RAG_MATCH_COUNT`: Search results per query
- `CHUNK_SIZE`, `CHUNK_OVERLAP`: PDF chunking
- `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW`: Rate limiting

### Logging

All modules use:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message: %s", value)  # Always use % formatting
```

Logging is configured in `app/main.py`.

## Data Flow Examples

### Question Processing
1. `POST /ask` → `app/api/routes.py:ask()`
2. Validate with `AskRequest` schema
3. Call `app/services/query_service.process_question()`
4. Get graph from `app/graph.get_graph()`
5. Graph invokes router node: `app/agents/router.router_node()`
6. Router chooses agent: rag, web, stock, or pdf
7. Agent executes and returns answer
8. Response formatted as `AskResponse` schema
9. Return JSON to client

### PDF Upload
1. `POST /upload-pdf` → `app/api/routes.py:upload_pdf()`
2. Validate file (type, size, magic bytes)
3. Sanitize filename
4. Call `app/services/pdf_service.upload_and_ingest_pdf()`
5. Save to `uploads/`
6. Extract text via `app/rag/uploader.ingest_pdf()`
7. Chunk text
8. Insert chunks to Supabase via `get_supabase_client()`
9. Return chunk count to user

### RAG Search
1. Agent receives question
2. Calls `app/rag/retriever.search_documents(question)`
3. Gets Supabase client via `app/core/database.get_supabase_client()`
4. Calls RPC function `search_private_company_details()`
5. Returns top matching chunks
6. Agent formats results
7. Returns to user

## Testing

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/

# Query RAG
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"information from company database"}'

# Query web
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"search the web for latest tech news"}'

# Query stock
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"apple stock price"}'

# Generate PDF
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"create a pdf report about ASML future growth"}'
```

### Interactive API Testing
Open browser to: `http://localhost:8000/docs` (Swagger UI)

## Common Issues & Solutions

### Issue: "SUPABASE_URL is not configured"
**Solution**: Set `SUPABASE_URL` in `.env` file

### Issue: "Supabase is not configured"
**Solution**: Check that both `SUPABASE_URL` and `SUPABASE_KEY` are set in `.env`

### Issue: Rate limit errors
**Solution**: Wait 60 seconds or change `RATE_LIMIT_WINDOW` in `app/core/config.py`

### Issue: PDF generation times out
**Solution**: Increase `PDF_GENERATION_TIMEOUT_SECONDS` in `.env`

## Performance Tips

1. **Caching**: Use `@lru_cache` for expensive operations (like `get_supabase_client()`)
2. **Batch Operations**: Insert RAG chunks in batches instead of one-by-one
3. **Connection Pooling**: Let Supabase handle it
4. **Search Optimization**: Full-text search is fast; consider stemming for better results
5. **Rate Limiting**: Adjust `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW` for your needs

## Security Checklist for Production

- [ ] Disable `allow_origins=["*"]` in CORS; use specific domain
- [ ] Add authentication (OAuth2, API keys)
- [ ] Use HTTPS only
- [ ] Don't expose `.env` file
- [ ] Validate all user input
- [ ] Use Supabase anon key (not service role)
- [ ] Enable Supabase Row-Level Security (RLS)
- [ ] Set up request logging and monitoring
- [ ] Use environment variables for secrets
- [ ] Add rate limiting to Redis for distributed systems

## Dependencies

See `requirements.txt` and `pyproject.toml`:
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **langgraph**: Agent orchestration
- **supabase**: Database client
- **reportlab**: PDF generation
- **PyMuPDF**: PDF extraction
- **duckduckgo-search**: Web search
- **yfinance**: Stock data
- **mcp**: Tool server protocol

## Contributing

1. Follow the existing code structure
2. Use type hints in all functions
3. Write descriptive docstrings
4. Use `%` formatting for logs (not f-strings)
5. Keep functions focused and small
6. Add error handling with context
7. Test manually before committing
8. Update ARCHITECTURE.md if structure changes

## Useful Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Supabase Documentation](https://supabase.com/docs)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
"""
