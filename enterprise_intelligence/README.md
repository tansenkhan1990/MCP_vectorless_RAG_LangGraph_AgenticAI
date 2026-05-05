"# Enterprise Intelligence System

> **Multi-Agent AI Platform** — LangGraph orchestrates OpenAI Agent SDK-powered agents with tool-calling for RAG, real-time web search, stock market data, and MCP-based PDF generation.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-orchestration-orange.svg)
![OpenAI SDK](https://img.shields.io/badge/OpenAI%20Agent%20SDK-tool--calling-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## Table of Contents

- [What Is This?](#-what-is-this)
- [System Architecture](#-system-architecture)
- [How a Question Flows Through the System](#-how-a-question-flows-through-the-system)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Agents Deep Dive](#-agents-deep-dive)
- [Tools Reference](#-tools-reference)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [LangGraph Workflow](#-langgraph-workflow)
- [MCP PDF Server](#-mcp-pdf-server)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Example Queries](#-example-queries)
- [Dependencies](#-dependencies)
- [Roadmap](#-roadmap)"

A sophisticated agentic AI system built with **LangGraph** that intelligently routes queries to specialized agents for comprehensive enterprise intelligence. The system seamlessly integrates Retrieval-Augmented Generation (RAG), real-time web search, financial data analysis, and document processing capabilities.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Agents Overview](#-agents-overview)
- [Database Schema](#-database-schema)
- [Troubleshooting](#-troubleshooting)

## ✨ Features

### Intelligent Query Routing
- **Smart Router**: Automatically routes queries to the most appropriate agent based on content analysis
- **Context-Aware**: Understands query intent and delegates to specialized agents

### Multi-Agent Architecture
- **RAG Agent**: Retrieves company-specific information from Supabase vector database
- **Web Agent**: Performs real-time web searches using DuckDuckGo
- **Stock Agent**: Fetches real-time financial data using yfinance
- **PDF Agent**: Processes and generates PDF documents using MCP
- **Router Agent**: Intelligently routes incoming queries to appropriate agents

### Enterprise Capabilities
- **PDF Upload & Ingestion**: Upload PDF documents for RAG system ingestion with automatic chunking
- **Vector-less RAG**: Efficiently search documents without vector embeddings
- **Real-time Data**: Access latest financial information and web content
- **Document Generation**: Create formatted reports and documents

## 🏗️ Architecture

The system uses a state-machine based architecture powered by **LangGraph**:

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│    Router    │ ◄─── Routes based on query content
└──────┬───────┘
       │
   ┌───┴────┬────────┬────────┐
   │        │        │        │
   ▼        ▼        ▼        ▼
┌─────┐ ┌──────┐ ┌────────┐ ┌──────┐
│ RAG │ │ Web  │ │ Stock  │ │ PDF  │
└─────┘ └──────┘ └────────┘ └──────┘
   │        │        │        │
   └────────┴────────┴────────┘
            │
            ▼
       ┌─────────┐
       │ Response│
       └─────────┘
```

### Key Components

1. **FastAPI Server**: RESTful API with async support
2. **LangGraph**: State management and agent orchestration
3. **Supabase**: Vector database for RAG storage
4. **MCP Server**: Model Context Protocol for tool integration

## 📦 Prerequisites

- **Python 3.10+**
- **macOS, Linux, or Windows**
- **uv** (Fast Python package manager) - [Install uv](https://github.com/astral-sh/uv)
- **Ollama** (For local LLM) - Optional but recommended
- **Supabase Account** - For database storage

### Required Accounts

1. **Supabase**: Create a free account at [supabase.com](https://supabase.com)
   - Get your Project URL and anon key
2. **Ollama** (Optional): Download from [ollama.ai](https://ollama.ai)
   - For running models locally: `qwen3-vl:235b-cloud`

## 🚀 Installation

### Step 1: Clone or Navigate to Project

```bash
cd /path/to/enterprise_intelligence
```

### Step 2: Initialize UV Project (if not already done)

```bash
uv init
```

### Step 3: Install Dependencies

Using **uv** (recommended - much faster than pip):

```bash
uv add fastapi uvicorn langgraph openai-agents python-dotenv supabase mcp reportlab duckduckgo-search yfinance pymupdf python-multipart httpx
```

Or using requirements.txt:

```bash
uv pip install -r requirements.txt
```

### Step 4: Create Virtual Environment (Recommended)

```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows
```

### Step 5: Install all dependencies

```bash
uv pip install -r requirements.txt
```

## ⚙️ Configuration

### Environment Variables

Create or update `.env` file in the root directory. Use `.env.example` as a template:

```bash
cp .env.example .env
```

Then edit `.env` and fill in your actual credentials:

```env
# OpenAI/Ollama Configuration
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=your-api-key-here

# Telemetry Settings
OPENAI_AGENTS_DISABLE_TRACING=1
OPENAI_DISABLE_TELEMETRY=true

# Local Model Configuration
LOCAL_MODEL_NAME=qwen3-vl:235b-cloud
LOCAL_EMBEDDING_MODEL=nomic-embed-text:latest

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Application Configuration (Optional)
MAX_UPLOAD_SIZE_MB=50          # Max PDF upload size
RAG_MATCH_COUNT=5              # Number of RAG results
CHUNK_SIZE=1200                # PDF chunk size
PDF_GENERATION_TIMEOUT_SECONDS=30  # PDF generation timeout
```

### Environment Variable Explanation

| Variable | Purpose | Example |
|----------|---------|---------|
| `OPENAI_BASE_URL` | Ollama server endpoint | `http://localhost:11434/v1` |
| `OPENAI_API_KEY` | API key for Ollama | `ollama` |
| `LOCAL_MODEL_NAME` | LLM model to use | `qwen3-vl:235b-cloud` |
| `LOCAL_EMBEDDING_MODEL` | Embedding model | `nomic-embed-text:latest` |
| `SUPABASE_URL` | Supabase project URL | `https://project.supabase.co` |
| `SUPABASE_KEY` | Supabase anon key | Your project anon key |
| `MAX_UPLOAD_SIZE_MB` | Max file upload size | `50` |
| `RAG_MATCH_COUNT` | Results per RAG search | `5` |
| `CHUNK_SIZE` | PDF chunk size for indexing | `1200` |
| `PDF_GENERATION_TIMEOUT_SECONDS` | PDF generation timeout | `30` |

## 🔐 Security Best Practices

### Critical Security Notes

1. **Never commit `.env` to version control**
   - `.env` is automatically ignored by `.gitignore`
   - Use `.env.example` as a template for your development team

2. **Secure your API in production**
   - Implement authentication (OAuth2, API keys)
   - Use HTTPS only
   - Restrict CORS origins to your domains
   - Add rate limiting (currently set to 10 requests/min per IP)

3. **Protect your Supabase credentials**
   - Use the **anon key** (public) - provided in `.env`
   - Never expose the **service role key** in client-facing code
   - Implement row-level security (RLS) in Supabase

4. **Validate file uploads**
   - Only PDF files are accepted
   - Maximum file size: 50 MB (configurable)
   - Files are validated for PDF format (magic bytes check)

5. **Rate limiting**
   - `/ask` and `/upload-pdf` endpoints: 10 requests per 60 seconds per IP
   - Adjust `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW` in `app/main.py` for production

### Environment Setup for Different Environments

**Development** (`.env`):
```env
OPENAI_BASE_URL=http://localhost:11434/v1
SUPABASE_URL=https://your-dev-project.supabase.co
SUPABASE_KEY=your-dev-anon-key
```

**Production** (set via environment variables, not `.env`):
```bash
export OPENAI_BASE_URL="https://api.openai.com/v1"  # or your provider
export OPENAI_API_KEY="sk-..."
export SUPABASE_URL="https://your-prod-project.supabase.co"
export SUPABASE_KEY="your-prod-anon-key"
```

## 📖 Usage

### Starting the Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload

# Or using uv
uv run uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔌 API Endpoints

### 1. Ask Question Endpoint

**POST** `/ask`

Process a question through the agentic AI system.

**Request Body:**
```json
{
  "question": "What is the current stock price of Apple?"
}
```

**Response:**
```json
{
  "question": "What is the current stock price of Apple?",
  "route": "stock",
  "answer": "Ticker: AAPL\nPrice: 150.25\nPE Ratio: 28.5\nMarket Cap: 2.3T"
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest AI trends?"}'
```

### 2. Upload PDF Endpoint

**POST** `/upload-pdf`

Upload a PDF file for RAG system ingestion.

**Request:**
- File upload (multipart/form-data)

**Response:**
```json
{
  "message": "PDF uploaded successfully"
}
```

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@your-document.pdf"
```

### 3. Health Check Endpoint

**GET** `/`

Check if the API is running.

**Response:**
```json
{
  "message": "Enterprise Intelligence API is running"
}
```

## 📁 Project Structure

```
enterprise_intelligence/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── db.py                   # Shared Supabase client factory
│   ├── state.py                # LangGraph state definitions
│   ├── graph.py                # LangGraph orchestration
│   │
│   ├── agents/                 # Specialized agents
│   │   ├── router.py           # Intelligent query router
│   │   ├── rag_agent.py        # RAG search agent
│   │   ├── web_agent.py        # Web search agent (DuckDuckGo)
│   │   ├── stock_agent.py      # Financial data agent
│   │   └── pdf_agent.py        # PDF processing agent
│   │
│   ├── rag/                    # RAG components
│   │   ├── retriever.py        # Document retrieval from Supabase
│   │   └── uploader.py         # PDF ingestion and chunking
│   │
│   └── mcp_server/
│       └── server.py           # Model Context Protocol server
│
├── schema/
│   └── private_company_details.sql  # Database schema
│
├── uploads/                    # Directory for uploaded PDFs
├── requirements.txt            # Python dependencies
├── pyproject.toml              # UV project configuration
├── .env                        # Environment variables (gitignored)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🤖 Agents Overview

### Router Agent
**Purpose**: Intelligent query routing

**Decision Logic**:
- **PDF/Report** → Routes to PDF Agent
- **Stock/Tesla/Apple** → Routes to Stock Agent
- **News/Politics/Latest** → Routes to Web Agent
- **Default** → Routes to RAG Agent

**Implementation**: [router.py](app/agents/router.py)

### RAG Agent
**Purpose**: Retrieve company-specific information from database

**Features**:
- Full-text search on Supabase
- Returns top 5 matching documents
- Supports custom chunking strategies

**Implementation**: [rag_agent.py](app/agents/rag_agent.py)

### Web Agent
**Purpose**: Real-time web information retrieval

**Features**:
- Uses DuckDuckGo search engine
- Returns 5 most relevant results
- Formats results with title and body

**Implementation**: [web_agent.py](app/agents/web_agent.py)

### Stock Agent
**Purpose**: Financial market data analysis

**Features**:
- Real-time stock data via yfinance
- Current price, PE ratio, market cap
- Supports multiple tickers (extensible)

**Supported Tickers**:
- `AAPL` (Apple) - Default
- `TSLA` (Tesla) - If "tesla" in query

**Implementation**: [stock_agent.py](app/agents/stock_agent.py)

### PDF Agent
**Purpose**: Document generation and processing

**Features**:
- Uses Model Context Protocol (MCP)
- Generates formatted reports
- Async processing

**Implementation**: [pdf_agent.py](app/agents/pdf_agent.py)

## 💾 Database Schema

### Table: `private_company_details`

```sql
CREATE TABLE private_company_details (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  file_name TEXT,
  title TEXT,
  page_number INTEGER,
  chunk_text TEXT NOT NULL,
  category TEXT DEFAULT 'private',
  source TEXT DEFAULT 'uploaded_pdf',
  created_at TIMESTAMP DEFAULT NOW(),
  tsv TSVECTOR
);

-- Create full-text search index
CREATE INDEX idx_private_company_chunk_text
  ON private_company_details USING GIN(tsv);
```

### Document Ingestion

When you upload a PDF:
1. File is saved to `uploads/` directory
2. Content is extracted page by page
3. Text is chunked into 1200-character segments
4. Each chunk is stored with metadata:
   - `file_name`: Original PDF filename
   - `title`: Document title
   - `page_number`: Source page number
   - `chunk_text`: Text chunk content
   - `category`: Document category (default: `private`)
   - `source`: Ingestion source (default: `uploaded_pdf`)
   - `created_at`: Ingestion timestamp

## 🐛 Troubleshooting

### Common Issues

#### 1. "Supabase connection failed"
```
Error: Failed to create Supabase client
```

**Solution**:
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check internet connection
- Ensure Supabase project is active

#### 2. "Ollama not running"
```
Error: Connection refused - localhost:11434
```

**Solution**:
```bash
# Start Ollama
ollama serve

# In another terminal, pull the model
ollama pull qwen3-vl:235b-cloud
```

#### 3. "PDF upload fails"
```
Error: Only PDF files are allowed
```

**Solution**:
- Ensure the file has `.pdf` extension
- Check file permissions
- Verify `uploads/` directory exists

#### 4. "ModuleNotFoundError"
```
Error: No module named 'app'
```

**Solution**:
```bash
# Make sure you're in the project root directory
cd enterprise_intelligence

# Reinstall dependencies
uv pip install -r requirements.txt
```

#### 5. "Port 8000 already in use"
```
Error: Address already in use
```

**Solution**:
```bash
# Use a different port
uvicorn app.main:app --port 8001 --reload
```

## 📚 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | Latest | Web framework |
| `uvicorn` | Latest | ASGI server |
| `langgraph` | Latest | Agent orchestration |
| `openai-agents` | Latest | LLM integration |
| `python-dotenv` | Latest | Environment variables |
| `supabase` | Latest | Database client |
| `mcp` | Latest | Model Context Protocol |
| `reportlab` | Latest | PDF generation |
| `duckduckgo-search` | Latest | Web search |
| `yfinance` | Latest | Stock data |
| `pymupdf` | Latest | PDF processing |
| `python-multipart` | Latest | Form data handling |
| `httpx` | Latest | HTTP client |

## 🔐 Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use environment variables** for sensitive data
3. **Validate file uploads** - Only PDFs allowed
4. **Input validation** - Questions must not be empty
5. **Error handling** - Comprehensive try-catch blocks
6. **Logging** - Track operations without exposing secrets

## 📝 Example Queries

```python
# Example 1: Stock Query
question = "What is the current price of Tesla?"
# Routes to: Stock Agent
# Returns: Current price, PE ratio, market cap

# Example 2: News Query
question = "What are the latest AI news?"
# Routes to: Web Agent
# Returns: Top 5 news articles from web

# Example 3: Company Information
question = "Tell me about our portfolio companies"
# Routes to: RAG Agent
# Returns: Documents from uploaded PDFs

# Example 4: PDF Query
question = "Generate a report on Q3 performance"
# Routes to: PDF Agent
# Returns: Generated PDF document
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Create a feature branch
2. Make your changes
3. Add tests if applicable
4. Commit with clear messages
5. Push and create a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📞 Support

For issues and questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review agent implementation in `app/agents/`
- Check logs in console output

## 🎯 Roadmap

- [ ] Add vector embeddings for enhanced RAG
- [ ] Implement caching layer
- [ ] Add authentication/authorization
- [ ] Create comprehensive test suite
- [ ] Deploy to cloud platforms
- [ ] Add more specialized agents
- [ ] Implement rate limiting

---

**Last Updated**: May 3, 2026
**Version**: 1.0.0
**Status**: Active Development