import pytest

from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routes_to_researcher() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    new_state = SupervisorAgent().run(state)
    assert new_state.route_history[-1] == "researcher"
