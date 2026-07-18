"""Provider-neutral text completion contracts and the local demo provider."""

from dataclasses import dataclass
from typing import Protocol

from engine.errors import ProviderError


@dataclass(frozen=True)
class ProviderReply:
    """The provider-neutral result of one model call."""

    text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float = 0.0
    cost_is_estimate: bool = True


class TextProvider(Protocol):
    """The smallest interface the orchestration layer needs from a provider."""

    name: str

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
    ) -> ProviderReply:
        """Generate one text response."""


class MockProvider:
    """A deterministic provider for local development and the demo fixture."""

    name = "mock"

    def __init__(self) -> None:
        self.calls: list[dict[str, str | float]] = []

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
    ) -> ProviderReply:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "model": model,
                "temperature": temperature,
            }
        )
        if "Variant:" in user_prompt:
            variant = _prompt_value(user_prompt, "Variant") or "default"
            goal = _prompt_value(user_prompt, "Goal") or "the requested task"
            material = _prompt_value(user_prompt, "Material") or "the supplied material"
            text = f"{variant.title()} draft for {goal}: {material}"
        elif "agent plan" in user_prompt.lower():
            text = "Use the specialist to create two drafts, then send both to the reviewer."
        elif "review" in system_prompt.lower() or "Drafts:" in user_prompt:
            text = "Review: the drafts are grounded in the supplied material and ready for human approval."
        else:
            text = f"Mock response for {model}: {user_prompt}"

        return ProviderReply(
            text=text,
            input_tokens=max(1, len(system_prompt + user_prompt) // 4),
            output_tokens=max(1, len(text) // 4),
        )


def _prompt_value(prompt: str, label: str) -> str | None:
    prefix = f"{label}:"
    for line in prompt.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def get_provider(name: str) -> TextProvider:
    """Resolve one configured provider without exposing SDK details upstream."""
    if name == "mock":
        return MockProvider()
    raise ProviderError(
        f"provider '{name}' is not available yet; use ORQ_PROVIDER=mock"
    )
