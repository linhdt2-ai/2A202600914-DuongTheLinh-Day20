"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""
    
    def __init__(self) -> None:
        from openai import OpenAI

        from multi_agent_research_lab.core.config import get_settings
        
        self.settings = get_settings()
        # Initialize OpenAI client. If API key is not in settings, OpenAI SDK will try to read OPENAI_API_KEY from environment
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.openai_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            timeout=self.settings.timeout_seconds,
        )
        
        content = response.choices[0].message.content or ""
        
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else None
        output_tokens = usage.completion_tokens if usage else None
        cost_usd = None
        
        # Simple rough cost calculation
        if input_tokens is not None and output_tokens is not None:
            if self.model == "gpt-4o-mini":
                cost_usd = (input_tokens / 1_000_000) * 0.15 + (output_tokens / 1_000_000) * 0.60
            elif self.model == "gpt-4o":
                cost_usd = (input_tokens / 1_000_000) * 5.00 + (output_tokens / 1_000_000) * 15.00

        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )
