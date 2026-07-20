"""Provider-neutral text completion contracts and provider adapters."""

from dataclasses import dataclass
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any, Protocol

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
    default_model: str

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
    default_model = ""

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
            platform = _prompt_value(user_prompt, "Platform") or "the selected platform"
            audience = _prompt_value(user_prompt, "Audience") or "the audience"
            outcome = _prompt_value(user_prompt, "Desired outcome") or "give the audience a useful next step"
            hook = _prompt_value(user_prompt, "Hook direction") or "Start with the clearest useful point."
            text = _demo_draft(
                goal=goal,
                material=material,
                variant=variant,
                platform=platform,
                audience=audience,
                outcome=outcome,
                hook=hook,
            )
        elif "agent plan" in user_prompt.lower():
            text = "Use the specialist to create distinct drafts, then send them to the reviewer."
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


class OpenAIProvider:
    """A lazy OpenAI Chat Completions adapter using the shared text contract.

    The SDK client is created only when the first completion is requested. That
    keeps mock and Ollama development keyless and makes this adapter testable
    with an injected client without making a network call during construction.
    """

    name = "openai"

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "gpt-5.6",
        base_url: str | None = None,
        timeout_seconds: float = 180.0,
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.default_model = default_model
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.timeout_seconds = timeout_seconds
        self._client = client

    def _client_or_raise(self) -> Any:
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise ProviderError(
                "OpenAI provider requires OPENAI_API_KEY before a completion can run"
            )
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ProviderError(
                "OpenAI provider requires the openai package to be installed"
            ) from error

        options: dict[str, Any] = {
            "api_key": self.api_key,
            "timeout": self.timeout_seconds,
        }
        if self.base_url:
            options["base_url"] = self.base_url
        self._client = OpenAI(**options)
        return self._client

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
    ) -> ProviderReply:
        selected_model = model or self.default_model
        try:
            response = self._client_or_raise().chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
        except ProviderError:
            raise
        except Exception as error:
            raise ProviderError("OpenAI completion failed") from error

        try:
            text = response.choices[0].message.content
            if not isinstance(text, str):
                raise TypeError("message content was not text")
            usage = response.usage
            input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
            output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        except (AttributeError, IndexError, TypeError, ValueError) as error:
            raise ProviderError("OpenAI returned an invalid chat response") from error

        return ProviderReply(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=0.0,
            cost_is_estimate=True,
        )


def _prompt_value(prompt: str, label: str) -> str | None:
    prefix = f"{label}:"
    for line in prompt.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _demo_draft(
    *,
    goal: str,
    material: str,
    variant: str,
    platform: str,
    audience: str,
    outcome: str,
    hook: str,
) -> str:
    """Create a useful offline draft with visible editorial transformation.

    Demo mode must show more than an echo of the request. This small composer
    adds a hook, structure, audience framing, and a next action while keeping
    supplied material clearly separate from generated connective language.
    """
    clean_goal = " ".join(goal.strip().split()).rstrip("?.!")
    topic = clean_goal
    lowered = clean_goal.lower()
    for prefix in ("how do i ", "how to ", "write a post about ", "create a post about "):
        if lowered.startswith(prefix):
            topic = clean_goal[len(prefix):].strip()
            break
    source = " ".join(material.strip().split())
    if source.startswith("(No source material supplied"):
        source = "No source material supplied. Add one fact or example from your experience before approval."
    source = source.rstrip(". ")
    audience_text = audience.strip()
    if audience_text.lower().startswith("not specified"):
        audience_text = "the people you want to reach"
    audience_text = audience_text.rstrip(". ")
    outcome_text = outcome.strip()
    if outcome_text.lower().startswith("teach or help"):
        outcome_text = "help the audience understand something useful"
    outcome_text = outcome_text.rstrip(". ")
    hook = hook.replace("Not specified; infer a reasonable audience from the idea.", audience_text)
    variant_key = variant.lower()
    label = f"{variant.title()} draft for {goal}"

    if variant_key == "reflective":
        body = (
            f"{hook}\n\n"
            f"The useful lesson in {topic.lower()} is to make the first step concrete for {audience_text}. "
            f"Use this context as your starting point: {source}.\n\n"
            f"Then ask what would make the next step easier for someone else. "
            f"That keeps the post focused on {outcome_text.lower()} instead of repeating the idea."
        )
    elif variant_key == "educational":
        body = (
            f"How to approach {topic.lower()}:\n\n"
            f"1. Start with the problem or question your audience has.\n"
            f"2. Use this supplied context: {source}.\n"
            f"3. End with one action that helps {audience_text} move forward.\n\n"
            f"The goal is to {outcome_text.lower()} without asking the reader to fill in the missing steps."
        )
    elif variant_key == "contrarian":
        body = (
            f"The obvious way to talk about {topic.lower()} is to list the answer. "
            f"A more useful post starts with the decision behind it.\n\n"
            f"Use this grounded detail: {source}. Then explain what you would do first and why. "
            f"Give {audience_text} a practical way to respond or try it."
        )
    else:
        body = (
            f"Trying to {topic.lower()}? Start with the clearest useful step.\n\n"
            f"Here is the context to work from: {source}. "
            f"Turn it into one concrete recommendation for {audience_text}, then tell the reader what to do next.\n\n"
            f"Next step: {outcome_text}."
        )

    return f"{label}\n\n{body}\n\nPlatform: {platform}."


def resolve_model(provider: TextProvider, requested_model: str) -> str:
    """Use a provider-specific model when the manifest is provider-neutral."""
    return getattr(provider, "default_model", "") or requested_model


def get_provider(
    name: str | None = None,
    *,
    model: str | None = None,
    ollama_host: str = "http://localhost:11434",
    ollama_model: str = "qwen3:1.7b",
    ollama_num_predict: int = 120,
    ollama_think: bool = False,
    openai_api_key: str | None = None,
    openai_model: str | None = None,
    openai_base_url: str | None = None,
) -> TextProvider:
    """Resolve one configured provider from explicit args or environment."""
    provider_name = (name or os.getenv("ORQ_PROVIDER", "mock")).strip().lower()
    selected_model = model or os.getenv("ORQ_MODEL")
    if provider_name == "mock":
        return MockProvider()
    if provider_name == "ollama":
        return OllamaProvider(
            host=ollama_host,
            default_model=selected_model or ollama_model,
            num_predict=ollama_num_predict,
            think=ollama_think,
        )
    if provider_name == "openai":
        return OpenAIProvider(
            api_key=openai_api_key,
            default_model=(
                selected_model
                or openai_model
                or os.getenv("ORQ_OPENAI_MODEL")
                or "gpt-5.6"
            ),
            base_url=openai_base_url,
        )
    raise ProviderError(
        f"provider '{provider_name}' is not available; use ORQ_PROVIDER=mock, ollama, or openai"
    )
