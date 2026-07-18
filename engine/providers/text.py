"""Provider-neutral text completion contracts and the local demo provider."""

from dataclasses import dataclass
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
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


class OllamaProvider:
    """A small adapter for Ollama's local, non-streaming chat endpoint."""

    name = "ollama"

    def __init__(
        self,
        host: str = "http://localhost:11434",
        default_model: str = "qwen3:1.7b",
        num_predict: int = 120,
        think: bool = False,
        timeout_seconds: float = 180.0,
    ) -> None:
        self.host = host.rstrip("/")
        self.default_model = default_model
        self.num_predict = num_predict
        self.think = think
        self.timeout_seconds = timeout_seconds

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
    ) -> ProviderReply:
        payload = {
            "model": model or self.default_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": self.think,
            "options": {
                "temperature": temperature,
                "num_predict": self.num_predict,
            },
        }
        request = Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise ProviderError(f"Ollama returned HTTP {error.code}: {detail}") from error
        except (URLError, TimeoutError, OSError) as error:
            raise ProviderError(
                f"cannot reach Ollama at {self.host}: {error}"
            ) from error

        try:
            result = json.loads(raw)
            text = result["message"]["content"]
        except (KeyError, TypeError, ValueError) as error:
            raise ProviderError("Ollama returned an invalid chat response") from error

        return ProviderReply(
            text=text,
            input_tokens=int(result.get("prompt_eval_count", 0)),
            output_tokens=int(result.get("eval_count", 0)),
            cost_usd=0.0,
            cost_is_estimate=False,
        )


def _prompt_value(prompt: str, label: str) -> str | None:
    prefix = f"{label}:"
    for line in prompt.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def resolve_model(provider: TextProvider, requested_model: str) -> str:
    """Use a provider-specific model when the manifest is provider-neutral."""
    return getattr(provider, "default_model", requested_model)


def get_provider(
    name: str,
    *,
    ollama_host: str = "http://localhost:11434",
    ollama_model: str = "qwen3:1.7b",
    ollama_num_predict: int = 120,
    ollama_think: bool = False,
) -> TextProvider:
    """Resolve one configured provider without exposing SDK details upstream."""
    if name == "mock":
        return MockProvider()
    if name == "ollama":
        return OllamaProvider(
            host=ollama_host,
            default_model=ollama_model,
            num_predict=ollama_num_predict,
            think=ollama_think,
        )
    raise ProviderError(
        f"provider '{name}' is not available; use ORQ_PROVIDER=mock or ollama"
    )
