# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestOutputFunctions(unittest.TestCase):
    def test_print_json(self):
        from cli_anything.wiremock.utils.output import print_json
        import io

        with patch("builtins.print") as mock_print:
            print_json({"key": "value"})
            mock_print.assert_called_once()
            output = mock_print.call_args.args[0]
            parsed = json.loads(output)
            self.assertEqual(parsed["key"], "value")

    def test_success_json_mode(self):
        from cli_anything.wiremock.utils.output import success

        with patch("builtins.print") as mock_print:
            success("All good", data={"result": 1}, json_mode=True)
            mock_print.assert_called_once()
            output = mock_print.call_args.args[0]
            parsed = json.loads(output)
            self.assertEqual(parsed["status"], "ok")
            self.assertEqual(parsed["message"], "All good")
            self.assertEqual(parsed["data"]["result"], 1)

    def test_success_human_mode(self):
        from cli_anything.wiremock.utils.output import success

        with patch("builtins.print") as mock_print:
            success("Done", json_mode=False)
            first_call = mock_print.call_args_list[0].args[0]
            self.assertIn("Done", first_call)

    def test_error_json_mode(self):
        from cli_anything.wiremock.utils.output import error

        with patch("builtins.print") as mock_print:
            with self.assertRaises(SystemExit) as cm:
                error("Something broke", json_mode=True)
            self.assertEqual(cm.exception.code, 1)
            output = mock_print.call_args.args[0]
            parsed = json.loads(output)
            self.assertEqual(parsed["status"], "error")
            self.assertEqual(parsed["message"], "Something broke")

    def test_error_human_mode_exits_1(self):
        from cli_anything.wiremock.utils.output import error

        with self.assertRaises(SystemExit) as cm:
            error("Oops", json_mode=False)
        self.assertEqual(cm.exception.code, 1)
