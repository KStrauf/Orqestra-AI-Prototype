from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine.cli import cmd_ping
from engine.errors import ProviderError
from engine.providers import MockProvider, get_provider


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
        with self.assertRaisesRegex(ProviderError, "not available yet"):
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


if __name__ == "__main__":
    unittest.main()
