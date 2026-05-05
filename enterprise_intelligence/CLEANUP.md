"""
Cleanup Guide for Deprecated Files

After the architectural reorganization, the following files in app/ are DEPRECATED
and should be removed as they have been replaced by new implementations:

## Deprecated Files to Remove

1. app/config.py
   └─ REPLACED BY: app/core/config.py
   └─ Reason: Consolidated configuration in core package

2. app/db.py
   └─ REPLACED BY: app/core/database.py
   └─ Reason: Database connections moved to core package

3. app/constants.py
   └─ REPLACED BY: app/core/config.py (merged)
   └─ Reason: Constants consolidated into core config

4. app/schemas.py
   └─ REPLACED BY: app/api/schemas.py
   └─ Reason: Request/response models belong in API layer

5. app/lifecycle.py
   └─ REPLACED BY: app/core/lifecycle.py
   └─ Reason: Lifecycle management moved to core package

## How to Remove These Files

Option 1: Using Terminal
```bash
cd app/
rm config.py db.py constants.py schemas.py lifecycle.py
```

Option 2: Manual Deletion
In VS Code:
1. Open File Explorer (Cmd+Shift+E)
2. Navigate to app/ folder
3. Right-click each deprecated file
4. Select "Delete" or "Move to Trash"

## Verification Checklist

After removal, verify:
- [x] All imports updated to use new locations
- [x] app/core/ contains: config.py, database.py, lifecycle.py
- [x] app/api/ contains: routes.py, schemas.py
- [x] app/services/ contains: query_service.py, pdf_service.py
- [x] app/middleware/ contains: rate_limiter.py
- [x] app/utils/ contains: validators and helpers
- [x] No Python syntax errors in app/main.py

## Testing After Cleanup

Run the application to ensure everything works:
```bash
uvicorn app.main:app --reload
```

Then test endpoints:
```bash
curl http://localhost:8000/
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question":"test"}'
```

## Current Clean Architecture Structure

app/
├── core/                    ✓ Configuration, DB, Lifecycle
├── api/                     ✓ REST API routes & schemas
├── services/                ✓ Business logic
├── middleware/              ✓ Request processing
├── agents/                  ✓ AI agents
├── rag/                     ✓ RAG system
├── mcp_server/              ✓ PDF tool server
├── utils/                   ✓ Utilities
├── main.py                  ✓ Entry point
├── state.py                 ✓ LangGraph state
└── graph.py                 ✓ LangGraph workflow
"""
