"""Command-line entrypoint for the lab starter."""

from typing import Annotated
import time

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    start_time = time.time()
    llm = LLMClient()
    system_prompt = "You are a helpful research assistant. Please provide a comprehensive and accurate answer to the user's query."
    
    try:
        response = llm.complete(system_prompt=system_prompt, user_prompt=query)
        latency = time.time() - start_time
        
        state.final_answer = response.content
        
        # Record metrics
        state.add_trace_event("baseline_metrics", {
            "latency_seconds": latency,
            "cost_usd": response.cost_usd,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "quality": None,  # Quality might require an evaluator
        })
    except Exception as exc:
        state.final_answer = f"Error during baseline execution: {exc}"
        state.errors.append(str(exc))
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


@app.command("benchmark")
def run_benchmarks(
    config_path: str = typer.Option("configs/lab_default.yaml", help="Path to config file"),
) -> None:
    """Run benchmark for baseline vs multi-agent and output reports."""
    import yaml
    import os
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    from multi_agent_research_lab.evaluation.report import render_markdown_report, render_html_report

    _init()
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    queries = config.get("benchmark", {}).get("queries", [])
    metrics_list = []
    
    for i, query in enumerate(queries):
        console.print(f"\n[bold blue]🚀 Running benchmark for query {i+1}: {query}[/bold blue]")
        
        # Run baseline
        def run_baseline(q: str) -> ResearchState:
            req = ResearchQuery(query=q)
            state = ResearchState(request=req)
            start_time = time.time()
            llm = LLMClient()
            system_prompt = "You are a helpful research assistant. Please provide a comprehensive and accurate answer to the user's query."
            try:
                resp = llm.complete(system_prompt=system_prompt, user_prompt=q)
                latency = time.time() - start_time
                state.final_answer = resp.content
                state.add_trace_event("baseline_run", {"input_tokens": resp.input_tokens, "output_tokens": resp.output_tokens, "cost_usd": resp.cost_usd})
            except Exception as e:
                state.errors.append(str(e))
            return state
            
        console.print("[dim]⏳ Running Single-Agent Baseline...[/dim]")
        _, b_metrics = run_benchmark(f"Q{i+1}-Baseline", query, run_baseline)
        metrics_list.append(b_metrics)
        
        # Run multi-agent
        def run_multi_agent(q: str) -> ResearchState:
            req = ResearchQuery(query=q)
            state = ResearchState(request=req)
            workflow = MultiAgentWorkflow()
            return workflow.run(state)
            
        console.print("[dim]⏳ Running Multi-Agent Workflow...[/dim]")
        _, m_metrics = run_benchmark(f"Q{i+1}-MultiAgent", query, run_multi_agent)
        metrics_list.append(m_metrics)
        
    os.makedirs("reports", exist_ok=True)
    
    md_report = render_markdown_report(metrics_list)
    with open("reports/benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(md_report)
        
    html_report = render_html_report(metrics_list)
    with open("reports/benchmark_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)
        
    console.print(f"\n[bold green]✅ Benchmark completed! Reports saved to 'reports/benchmark_report.md' and 'reports/benchmark_report.html'.[/bold green]")


if __name__ == "__main__":
    app()
