# Enterprise Intelligence Application

This is an agentic AI system built with LangGraph that provides enterprise intelligence capabilities including RAG, web search, stock analysis, and PDF processing.

## Features

- Router agent for directing queries to appropriate specialized agents
- RAG agent for retrieval-augmented generation tasks
- Web agent for real-time web information retrieval
- Stock agent for financial data analysis
- PDF agent for document processing

## Architecture

The application follows a modular architecture with:
- `app/main.py`: Entry point
- `app/config.py`: Configuration management
- `app/state.py`: Application state management
- `app/graph.py`: LangGraph orchestration
- `app/agents/`: Specialized agents
- `app/rag/`: Retrieval-augmented generation components
- `app/mcp_server/`: Model Context Protocol server implementation
- `schema/`: Database schemas
- `uploads/`: Directory for uploaded files

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`

3. Run the application:
```bash
python app/main.py
```