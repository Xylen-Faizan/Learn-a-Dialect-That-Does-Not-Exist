class BudgetExceededError(Exception):
    """Raised when pipeline exceeds model or tool call ceilings."""
    pass


class BudgetTracker:
    """Enforces the brief's limits: max 25 model calls, 50 tool calls."""

    def __init__(self, max_model_calls: int = 25, max_tool_calls: int = 50):
        self.max_model_calls = max_model_calls
        self.max_tool_calls = max_tool_calls
        self.model_calls = 0
        self.tool_calls = 0

    def record_model_call(self):
        if self.model_calls >= self.max_model_calls:
            raise BudgetExceededError(
                f"Model call budget of {self.max_model_calls} exceeded."
            )
        self.model_calls += 1

    def record_tool_call(self):
        if self.tool_calls >= self.max_tool_calls:
            raise BudgetExceededError(
                f"Tool call budget of {self.max_tool_calls} exceeded."
            )
        self.tool_calls += 1

    def get_summary(self) -> dict:
        return {
            "model_calls_used": f"{self.model_calls}/{self.max_model_calls}",
            "tool_calls_used": f"{self.tool_calls}/{self.max_tool_calls}",
        }
