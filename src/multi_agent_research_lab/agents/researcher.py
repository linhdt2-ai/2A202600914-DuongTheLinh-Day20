"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        from multi_agent_research_lab.services.llm_client import LLMClient
        from multi_agent_research_lab.services.search_client import SearchClient
        
        search_client = SearchClient()
        llm = LLMClient()
        
        # 1. Search for sources
        sources = search_client.search(state.request.query, state.request.max_sources)
        state.sources.extend(sources)
        
        # 2. Generate research notes using LLM
        sources_text = "\n".join([f"- [{s.title}]({s.url}): {s.snippet}" for s in state.sources])
        system_prompt = "You are a researcher. Summarize the following sources into structured research notes."
        user_prompt = f"Query: {state.request.query}\n\nSources:\n{sources_text}"
        
        response = llm.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        state.research_notes = response.content
        
        state.add_trace_event("researcher_run", {
            "query": state.request.query,
            "num_sources": len(sources),
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens
        })
        
        return state
