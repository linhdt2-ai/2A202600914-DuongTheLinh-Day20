"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Flag issues with the final answer."""
        from multi_agent_research_lab.services.llm_client import LLMClient
        
        llm = LLMClient()
        
        system_prompt = "You are a strict critic. Review the final answer against the research notes. If there are hallucinations or missing citations, list them. Otherwise say 'LGTM'."
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\nFinal Answer:\n{state.final_answer}"
        
        response = llm.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        
        state.add_trace_event("critic_run", {
            "feedback": response.content,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens
        })
        
        if "LGTM" not in response.content:
            state.errors.append("Critic found issues: " + response.content)
            state.final_answer = None
            
        return state
