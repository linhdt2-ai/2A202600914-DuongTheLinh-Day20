"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        from multi_agent_research_lab.services.llm_client import LLMClient
        
        llm = LLMClient()
        
        system_prompt = f"You are a technical writer. Write a comprehensive final response to the user's query. Target audience: {state.request.audience}. Use the provided research and analysis notes. Include citations."
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\nAnalysis Notes:\n{state.analysis_notes}"
        
        response = llm.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        state.final_answer = response.content
        
        state.add_trace_event("writer_run", {
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens
        })
        
        return state
