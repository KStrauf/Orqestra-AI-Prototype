from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import json
from urllib.error import URLError

from engine.cli import cmd_ping
from engine.errors import ProviderError
from engine.providers import MockProvider, OllamaProvider, get_provider, resolve_model


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
            get_provider("openai")

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


if __name__ == "__main__":
    unittest.main()
