"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return metrics including cost, quality, and errors."""
    from multi_agent_research_lab.services.llm_client import LLMClient
    import re

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    # Calculate cost from trace
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0
    
    for event in state.trace:
        payload = event.get("payload", {})
        total_input_tokens += payload.get("input_tokens") or 0
        total_output_tokens += payload.get("output_tokens") or 0
        if "cost_usd" in payload and payload["cost_usd"]:
            total_cost += payload["cost_usd"]
            
    # If no cost recorded, do a rough estimation (e.g., gpt-4o-mini rates)
    if total_cost == 0.0 and (total_input_tokens > 0 or total_output_tokens > 0):
        total_cost = (total_input_tokens / 1_000_000) * 0.15 + (total_output_tokens / 1_000_000) * 0.60
        
    # Quality scoring using LLM as a judge
    quality_score = 0.0
    if state.final_answer:
        try:
            llm = LLMClient()
            score_prompt = "You are an evaluator. Rate the quality of the following response to the query on a scale of 0 to 10. Only return the number."
            score_query = f"Query: {query}\nResponse: {state.final_answer}"
            resp = llm.complete(score_prompt, score_query)
            matches = re.findall(r"\d+\.?\d*", resp.content)
            if matches:
                quality_score = min(10.0, max(0.0, float(matches[0])))
        except Exception:
            pass
            
    # Details
    notes = f"Tokens: {total_input_tokens} in / {total_output_tokens} out. "
    if state.errors:
        notes += f"Errors: {len(state.errors)}. "
        
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        query=query,
        output=state.final_answer or "",
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        quality_score=quality_score,
        notes=notes
    )
    return state, metrics
