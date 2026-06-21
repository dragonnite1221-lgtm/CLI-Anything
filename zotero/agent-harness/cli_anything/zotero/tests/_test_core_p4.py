# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class OpenAIUtilityTests(unittest.TestCase):
    def test_extract_text_from_response_payload(self):
        payload = {
            "id": "resp_1",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": "Hello world"},
                    ],
                }
            ],
        }
        result = openai_api._extract_text(payload)
        self.assertEqual(result, "Hello world")
