"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context augmented with LangSmith tracing if available."""
    from multi_agent_research_lab.core.config import get_settings
    import contextlib
    
    settings = get_settings()
    
    # Initialize Langsmith traceable if API key is present
    cm = contextlib.nullcontext()
    if settings.langsmith_api_key:
        try:
            from langsmith import trace
            cm = trace(name=name, metadata=attributes or {}, project_name=settings.langsmith_project)
        except ImportError:
            pass
            
    with cm:
        started = perf_counter()
        span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
        try:
            yield span
        finally:
            span["duration_seconds"] = perf_counter() - started
