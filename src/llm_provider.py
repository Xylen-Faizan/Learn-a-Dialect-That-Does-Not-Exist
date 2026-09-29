from typing import Protocol
from src.budget import BudgetTracker


class LLMProvider(Protocol):
    """Abstract interface for language model providers."""

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        ...


class MockLLMProvider:
    """Deterministic offline provider for evaluation without API keys."""

    def __init__(self, budget_tracker: BudgetTracker):
        self.budget = budget_tracker

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.budget.record_model_call()
        # Mock answers simulating structured model outputs
        if "came back, elder brother" in user_prompt.lower():
            return "tal-vok, dura-sh?"
        if "secret" in user_prompt.lower():
            return "[UNSUPPORTED:secret]"
        if "leave now" in user_prompt.lower():
            return "[UNSUPPORTED:we] [UNSUPPORTED:must] tra nuna."
        return "aba kor-te pel-sh."


class LiveOpenAIProvider:
    """Live provider executing against hosted models with budget guards."""

    def __init__(
        self,
        api_key: str,
        budget_tracker: BudgetTracker,
        model: str = "gpt-4o-mini",
    ):
        self.api_key = api_key
        self.budget = budget_tracker
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.budget.record_model_call()
        # Clean isolation: instructions are isolated from untrusted input
        # to defend against prompt injection
        import openai

        client = openai.OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content or ""
