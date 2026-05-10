"""
Run async MCP client code from **synchronous** Agent SDK tool functions.

The OpenAI Agents SDK invokes tools synchronously by default; the MCP Python
client is async. We run one event loop per tool call on a short-lived worker
thread so we never call ``asyncio.run`` from within an already-running loop.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import Coroutine
from queue import Queue
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def run_mcp_coro(coro: Coroutine[Any, Any, T], *, timeout: float) -> T:
    """
    Execute *coro* on a fresh event loop in a daemon thread; enforce *timeout*.

    Raises:
        TimeoutError: If the thread does not finish within *timeout* seconds.
        Exception: Any exception raised inside *coro* / ``asyncio.run``.
    """
    result_queue: Queue = Queue()

    def _worker() -> None:
        try:
            result_queue.put(asyncio.run(coro))
        except Exception as exc:
            result_queue.put(exc)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        raise TimeoutError(f"MCP client timed out after {timeout:.1f}s")

    out = result_queue.get_nowait()
    if isinstance(out, Exception):
        logger.error("MCP coroutine failed: %s", out, exc_info=out)
        raise out
    return out
