"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        from multi_agent_research_lab.services.llm_client import LLMClient
        
        llm = LLMClient()
        
        system_prompt = "You are an analyst. Review the research notes, extract key claims, compare viewpoints, and flag weak evidence."
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}"
        
        response = llm.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        state.analysis_notes = response.content
        
        state.add_trace_event("analyst_run", {
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens
        })
        
        return state
