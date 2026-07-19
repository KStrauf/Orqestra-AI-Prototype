import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import json
from types import SimpleNamespace
from urllib.error import URLError

from engine.cli import cmd_ping
from engine.config import load_settings
from engine.errors import ProviderError
from engine.providers import (
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
    get_provider,
    resolve_model,
)
from studio.workflow import ContentWorkflowRequest, run_content_workflow


class ProviderTests(unittest.TestCase):
    def test_mock_provider_returns_provider_neutral_reply(self) -> None:
        provider = MockProvider()

        reply = provider.complete(
            system_prompt="System",
            user_prompt="Say hello",
            model="demo-model",
            temperature=0.0,
        )

        self.assertEqual(provider.name, "mock")
        self.assertIn("Mock response for demo-model", reply.text)
        self.assertGreater(reply.input_tokens, 0)
        self.assertGreater(reply.output_tokens, 0)

    def test_unknown_provider_is_a_clean_error(self) -> None:
        with self.assertRaisesRegex(ProviderError, "not available"):
            get_provider("future-provider")

    def test_provider_and_model_are_selected_from_environment(self) -> None:
        with patch.dict(
            os.environ,
            {"ORQ_PROVIDER": "openai", "ORQ_MODEL": "gpt-5.6"},
            clear=False,
        ):
            provider = get_provider()

        self.assertIsInstance(provider, OpenAIProvider)
        self.assertEqual(provider.default_model, "gpt-5.6")

    def test_settings_normalize_provider_and_expose_model_selection(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ORQ_PROVIDER": "OLLAMA",
                "ORQ_MODEL": "qwen3:8b",
                "ORQ_OLLAMA_MODEL": "qwen3:1.7b",
                "ORQ_OPENAI_MODEL": "gpt-5.6",
            },
            clear=False,
        ):
            settings = load_settings()

        self.assertEqual(settings.provider, "ollama")
        self.assertEqual(settings.model, "qwen3:8b")
        self.assertEqual(settings.ollama_model, "qwen3:1.7b")
        self.assertEqual(settings.openai_model, "gpt-5.6")

    def test_ping_uses_configured_provider_boundary(self) -> None:
        with TemporaryDirectory() as temporary:
            class Settings:
                provider = "mock"
                runs_dir = Path(temporary) / "runs"

            with patch("builtins.print") as print_mock:
                exit_code = cmd_ping(Settings(), "demo-model", "Say hello")

        self.assertEqual(exit_code, 0)
        rendered = "\n".join(str(call.args[0]) for call in print_mock.call_args_list)
        self.assertIn("provider mock", rendered)
        self.assertIn("model    demo-model", rendered)
        self.assertIn("Mock response for demo-model", rendered)

    def test_ollama_provider_posts_concise_non_thinking_chat_request(self) -> None:
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def read(self) -> bytes:
                return json.dumps(
                    {
                        "message": {"content": "Short local answer."},
                        "prompt_eval_count": 12,
                        "eval_count": 6,
                    }
                ).encode("utf-8")

        provider = OllamaProvider(
            host="http://localhost:11434",
            default_model="qwen3:1.7b",
            num_predict=120,
            think=False,
        )
        with patch("engine.providers.text.urlopen", return_value=FakeResponse()) as open_url:
            reply = provider.complete(
                system_prompt="Be concise.",
                user_prompt="Say hello.",
                model="qwen3:1.7b",
                temperature=0.2,
            )

        request = open_url.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "http://localhost:11434/api/chat")
        self.assertEqual(payload["model"], "qwen3:1.7b")
        self.assertFalse(payload["think"])
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["options"], {"temperature": 0.2, "num_predict": 120})
        self.assertEqual(reply.text, "Short local answer.")
        self.assertEqual(reply.input_tokens, 12)
        self.assertEqual(reply.output_tokens, 6)
        self.assertEqual(reply.cost_usd, 0.0)
        self.assertFalse(reply.cost_is_estimate)

    def test_ollama_connection_failure_is_a_clean_provider_error(self) -> None:
        provider = OllamaProvider()
        with patch(
            "engine.providers.text.urlopen",
            side_effect=URLError("connection refused"),
        ):
            with self.assertRaisesRegex(ProviderError, "cannot reach Ollama"):
                provider.complete(
                    system_prompt="System",
                    user_prompt="Hello",
                    model="qwen3:1.7b",
                    temperature=0.2,
                )

    def test_ollama_provider_resolves_manifest_models_to_local_default(self) -> None:
        provider = get_provider("ollama", ollama_model="qwen3:1.7b")

        self.assertEqual(resolve_model(provider, "gpt-5.6"), "qwen3:1.7b")

    def test_ollama_provider_accepts_generic_model_override(self) -> None:
        provider = get_provider(
            "ollama",
            model="qwen3:8b",
            ollama_model="qwen3:1.7b",
        )

        self.assertEqual(resolve_model(provider, "gpt-5.6"), "qwen3:8b")

    def test_openai_provider_uses_the_same_text_contract(self) -> None:
        class FakeCompletions:
            def __init__(self) -> None:
                self.kwargs = None

            def create(self, **kwargs):
                self.kwargs = kwargs
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content="OpenAI answer.")
                        )
                    ],
                    usage=SimpleNamespace(prompt_tokens=11, completion_tokens=7),
                )

        completions = FakeCompletions()
        client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
        provider = OpenAIProvider(
            api_key="test-key",
            default_model="gpt-5.6",
            client=client,
        )

        reply = provider.complete(
            system_prompt="Be concise.",
            user_prompt="Say hello.",
            model="",
            temperature=0.2,
        )

        self.assertEqual(provider.name, "openai")
        self.assertEqual(provider.default_model, "gpt-5.6")
        self.assertEqual(reply.text, "OpenAI answer.")
        self.assertEqual(reply.input_tokens, 11)
        self.assertEqual(reply.output_tokens, 7)
        self.assertTrue(reply.cost_is_estimate)
        self.assertEqual(completions.kwargs["model"], "gpt-5.6")
        self.assertEqual(completions.kwargs["temperature"], 0.2)
        self.assertEqual(
            completions.kwargs["messages"],
            [
                {"role": "system", "content": "Be concise."},
                {"role": "user", "content": "Say hello."},
            ],
        )

    def test_openai_provider_requires_key_only_when_completion_runs(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            provider = OpenAIProvider()

        with self.assertRaisesRegex(ProviderError, "OPENAI_API_KEY"):
            provider.complete(
                system_prompt="System",
                user_prompt="Hello",
                model="gpt-5.6",
                temperature=0.0,
            )

    def test_workflow_records_provider_and_resolved_model_metadata(self) -> None:
        class FakeCompletions:
            def create(self, **kwargs):
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content="Provider draft.")
                        )
                    ],
                    usage=SimpleNamespace(prompt_tokens=3, completion_tokens=2),
                )

        provider = OpenAIProvider(
            default_model="gpt-5.6",
            client=SimpleNamespace(
                chat=SimpleNamespace(completions=FakeCompletions())
            ),
        )
        with TemporaryDirectory() as temporary:
            result = run_content_workflow(
                Path(temporary) / "runs",
                ContentWorkflowRequest(
                    goal="Write a provider test",
                    material="Provider metadata must be traceable.",
                ),
                provider=provider,
            )

        self.assertEqual(result.record.provider, "openai")
        self.assertEqual(result.record.model, "gpt-5.6")


if __name__ == "__main__":
    unittest.main()
