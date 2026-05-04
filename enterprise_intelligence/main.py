"""
Convenience entry point for running the server.

Usage:
    python main.py
    # or
    uv run python main.py
"""

import uvicorn


def main():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )


if __name__ == "__main__":
    main()
