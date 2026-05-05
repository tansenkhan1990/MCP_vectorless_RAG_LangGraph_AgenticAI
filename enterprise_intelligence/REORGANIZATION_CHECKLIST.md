"""
Complete File Organization Checklist & Cleanup Guide

## Final Step: Remove Deprecated Files

The following OLD files have been replaced by the NEW structure.
All application code now imports from the NEW locations.

### Files to Remove

#### Priority 1: Critical (Remove First)
These files conflict with the new structure:

1. ❌ **app/graph.py**
   - Replaced by: **app/workflows/graph.py**
   - Status: New version created with same functionality
   - Action: DELETE

2. ❌ **app/state.py**
   - Replaced by: **app/workflows/state.py**
   - Status: New version created with same functionality
   - Action: DELETE

#### Priority 2: High (Remove Second)
These files should be removed to avoid confusion:

3. ❌ **app/config.py**
   - Replaced by: **app/core/config.py**
   - Status: All imports updated to use core/config.py
   - Action: DELETE

4. ❌ **app/db.py**
   - Replaced by: **app/core/database.py**
   - Status: All imports updated to use core/database.py
   - Action: DELETE

5. ❌ **app/lifecycle.py**
   - Replaced by: **app/core/lifecycle.py**
   - Status: All imports updated to use core/lifecycle.py
   - Action: DELETE

#### Priority 3: Medium (Remove Third)
These should be removed to maintain clean structure:

6. ❌ **app/schemas.py**
   - Replaced by: **app/api/schemas.py**
   - Status: All imports updated to use api/schemas.py
   - Action: DELETE

7. ❌ **app/constants.py**
   - Replaced by: **app/core/config.py** (merged)
   - Status: All constants moved to core/config.py
   - Action: DELETE


## How to Remove Files

### Option 1: Using Terminal (Recommended)
```bash
cd /Users/tansenkhan/Documents/learning/MCP/MCP_vectorless_RAG_LangGraph_AgenticAI/enterprise_intelligence/app
rm graph.py state.py config.py db.py lifecycle.py schemas.py constants.py
```

### Option 2: Using VS Code
1. Open VS Code File Explorer (Cmd+Shift+E)
2. Navigate to app/ folder
3. Right-click each deprecated file
4. Select \"Delete\" or \"Move to Trash\"

### Option 3: Using Finder
1. Open Finder
2. Navigate to enterprise_intelligence/app/
3. Select each deprecated file
4. Press Cmd+Delete (Move to Trash)


## Verification Checklist

After removing deprecated files, verify:

### 1. Project Structure ✓
- [ ] No old files in app/ root (graph.py, state.py, etc.)
- [ ] All directories exist:
  - [ ] app/core/
  - [ ] app/api/
  - [ ] app/workflows/
  - [ ] app/agents/
  - [ ] app/services/
  - [ ] app/rag/
  - [ ] app/mcp_server/
  - [ ] app/middleware/
  - [ ] app/utils/

### 2. New Workflow Package ✓
- [ ] app/workflows/__init__.py exists
- [ ] app/workflows/graph.py exists
- [ ] app/workflows/state.py exists
- [ ] All contain correct code

### 3. Core Package ✓
- [ ] app/core/config.py exists
- [ ] app/core/database.py exists
- [ ] app/core/lifecycle.py exists
- [ ] app/core/__init__.py exports all APIs

### 4. API Package ✓
- [ ] app/api/routes.py exists
- [ ] app/api/schemas.py exists

### 5. Services Package ✓
- [ ] app/services/query_service.py exists
- [ ] app/services/pdf_service.py exists

### 6. No Broken Imports ✓
- [ ] No imports from app.graph (should be app.workflows)
- [ ] No imports from app.state (should be app.workflows)
- [ ] No imports from app.config (should be app.core)
- [ ] No imports from app.db (should be app.core.database)
- [ ] No imports from app.schemas (should be app.api.schemas)
- [ ] No imports from app.lifecycle (should be app.core.lifecycle)
- [ ] No imports from app.constants (should be app.core)

### 7. Application Works ✓
Test the application:
```bash
cd enterprise_intelligence
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 8. Endpoints Respond ✓
Test health check:
```bash
curl http://localhost:8000/
```

Expected response:
```json
{"message":"Enterprise Intelligence API is running"}
```

### 9. No Python Errors ✓
- [ ] No import errors
- [ ] No module not found errors
- [ ] No circular import warnings
- [ ] Application starts without errors


## Current Valid Directory Structure (After Cleanup)

```
app/
├── core/
│   ├── __init__.py          ✅
│   ├── config.py            ✅
│   ├── database.py          ✅
│   └── lifecycle.py         ✅
├── api/
│   ├── __init__.py          ✅
│   ├── routes.py            ✅
│   └── schemas.py           ✅
├── workflows/               ✅ (NEW)
│   ├── __init__.py          ✅
│   ├── state.py             ✅
│   └── graph.py             ✅
├── agents/
│   ├── __init__.py          ✅
│   ├── router.py            ✅
│   ├── rag_agent.py         ✅
│   ├── web_agent.py         ✅
│   ├── stock_agent.py       ✅
│   └── pdf_agent.py         ✅
├── services/
│   ├── __init__.py          ✅
│   ├── query_service.py     ✅
│   └── pdf_service.py       ✅
├── rag/
│   ├── __init__.py          ✅
│   ├── retriever.py         ✅
│   └── uploader.py          ✅
├── mcp_server/
│   ├── __init__.py          ✅
│   └── server.py            ✅
├── middleware/
│   ├── __init__.py          ✅
│   └── rate_limiter.py      ✅
├── utils/
│   ├── __init__.py          ✅
├── main.py                  ✅
└── __init__.py              ✅


## Import Migration Summary

| Old Import | New Import | File(s) Updated |
|-----------|-----------|-----------------|
| `from app.graph import` | `from app.workflows import` | query_service.py |
| `from app.state import` | `from app.workflows import` | 5 agents, pdf_agent.py |
| `from app.config import` | `from app.core import` | rag files, agents, mcp_server |
| `from app.db import` | `from app.core.database import` | rag/uploader.py, rag/retriever.py |
| `from app.lifecycle import` | `from app.core.lifecycle import` | main.py |
| `from app.schemas import` | `from app.api.schemas import` | routes.py |

**Status**: ✅ ALL IMPORTS UPDATED


## Next Steps

1. **Remove deprecated files** (see instructions above)
2. **Verify project structure** (run checklist above)
3. **Test application** (run endpoint tests)
4. **Commit changes** to git:
   ```bash
   git add .
   git commit -m \"Reorganize project to clean architecture pattern

   - Create app/workflows/ for LangGraph orchestration
   - Move graph.py and state.py to workflows/
   - Update all imports to reference new locations
   - Remove deprecated root-level config files
   - All functionality preserved, only structure improved\"
   ```


## Documentation Files Created

- ✅ **ARCHITECTURE.md** - Detailed architecture documentation
- ✅ **CLEANUP.md** - Original cleanup guide
- ✅ **DEVELOPER_GUIDE.md** - Developer quick reference
- ✅ **PROJECT_STRUCTURE.md** - Complete structure reference
- ✅ **REORGANIZATION_CHECKLIST.md** - This file


## Questions?

If you encounter issues:

1. **Check imports**: Use grep to find any remaining old imports
   ```bash
   grep -r \"from app.graph import\" app/
   grep -r \"from app.state import\" app/
   grep -r \"from app.config import\" app/
   ```

2. **Check for circular imports**: Look at import statements in core/ files

3. **Run the app**: Start with `uvicorn app.main:app --reload` to see any errors

4. **Check file permissions**: Ensure files are readable/writable
"""
