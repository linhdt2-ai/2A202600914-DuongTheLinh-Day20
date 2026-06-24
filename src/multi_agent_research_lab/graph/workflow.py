"""LangGraph workflow skeleton."""

from typing import Any, cast

from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def build(self) -> Any:
        """Create a LangGraph graph."""
        from langgraph.graph import END, START, StateGraph

        from multi_agent_research_lab.agents.analyst import AnalystAgent
        from multi_agent_research_lab.agents.critic import CriticAgent
        from multi_agent_research_lab.agents.researcher import ResearcherAgent
        from multi_agent_research_lab.agents.supervisor import SupervisorAgent
        from multi_agent_research_lab.agents.writer import WriterAgent

        workflow = StateGraph(ResearchState)

        supervisor = SupervisorAgent()
        researcher = ResearcherAgent()
        analyst = AnalystAgent()
        writer = WriterAgent()
        critic = CriticAgent()

        workflow.add_node("supervisor", supervisor.run)
        workflow.add_node("researcher", researcher.run)
        workflow.add_node("analyst", analyst.run)
        workflow.add_node("writer", writer.run)
        workflow.add_node("critic", critic.run)

        def router(state: ResearchState) -> str:
            return state.route_history[-1] if state.route_history else "done"

        workflow.add_edge(START, "supervisor")
        workflow.add_conditional_edges(
            "supervisor",
            router,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "critic": "critic",
                "done": END,
            }
        )

        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        workflow.add_edge("critic", "supervisor")

        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        graph = self.build()
        result = graph.invoke(state)
        
        if isinstance(result, dict):
            # In case langgraph returns a dict representing the final state
            return ResearchState.model_validate(result)
        return cast(ResearchState, result)
