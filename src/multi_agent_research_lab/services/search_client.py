"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        
        # Simple local mock implementation
        return [
            SourceDocument(
                title=f"Mock result {i+1} for: {query}",
                url=f"https://mock.example.com/result-{i+1}",
                snippet=f"This is a mock search result snippet containing relevant information about {query}.",
            )
            for i in range(max_results)
        ]
