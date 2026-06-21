# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestActionsModule:
    @patch("cli_anything.renderdoc.core.actions.rd")
    def test_decode_flags(self, mock_rd):
        # Patch the flag values
        mock_rd.ActionFlags = MockActionFlags
        from cli_anything.renderdoc.core.actions import _decode_flags

        result = _decode_flags(0x0002)  # Drawcall
        assert "Drawcall" in result

    @patch("cli_anything.renderdoc.core.actions.rd")
    def test_decode_flags_multiple(self, mock_rd):
        mock_rd.ActionFlags = MockActionFlags
        from cli_anything.renderdoc.core.actions import _decode_flags

        result = _decode_flags(0x0002 | 0x2000)  # Drawcall + Indexed
        assert "Drawcall" in result
        assert "Indexed" in result

    @patch("cli_anything.renderdoc.core.actions.rd")
    def test_action_to_dict(self, mock_rd):
        mock_rd.ActionFlags = MockActionFlags
        from cli_anything.renderdoc.core.actions import _action_to_dict

        action = _make_mock_action(1, "Draw Triangle", 0x0002)
        d = _action_to_dict(action, None)
        assert d["eventId"] == 1
        assert d["name"] == "Draw Triangle"
        assert "Drawcall" in d["flags"]

    @patch("cli_anything.renderdoc.core.actions.rd")
    def test_list_actions_flat(self, mock_rd):
        mock_rd.ActionFlags = MockActionFlags
        from cli_anything.renderdoc.core.actions import list_actions

        child = _make_mock_action(2, "DrawIndexed", 0x0002)
        root = _make_mock_action(1, "RenderPass", 0x0020, children=[child])

        controller = MagicMock()
        controller.GetRootActions.return_value = [root]
        controller.GetStructuredFile.return_value = MagicMock()

        result = list_actions(controller, flat=True)
        assert len(result) == 2
        assert result[0]["eventId"] == 1
        assert result[1]["eventId"] == 2
        assert result[1]["depth"] == 1

    @patch("cli_anything.renderdoc.core.actions.rd")
    def test_list_actions_root_only(self, mock_rd):
        mock_rd.ActionFlags = MockActionFlags
        from cli_anything.renderdoc.core.actions import list_actions

        child = _make_mock_action(2, "DrawIndexed")
        root = _make_mock_action(1, "RenderPass", 0x0020, children=[child])

        controller = MagicMock()
        controller.GetRootActions.return_value = [root]
        controller.GetStructuredFile.return_value = MagicMock()

        result = list_actions(controller, flat=False)
        assert len(result) == 1

    @patch("cli_anything.renderdoc.core.actions.rd")
    def test_find_actions_by_name(self, mock_rd):
        mock_rd.ActionFlags = MockActionFlags
        from cli_anything.renderdoc.core.actions import find_actions_by_name

        a1 = _make_mock_action(1, "Clear RenderTarget", 0x0001)
        a2 = _make_mock_action(2, "DrawIndexed(100)", 0x0002)
        a3 = _make_mock_action(3, "DrawIndexed(200)", 0x0002)

        controller = MagicMock()
        controller.GetRootActions.return_value = [a1, a2, a3]
        controller.GetStructuredFile.return_value = MagicMock()

        result = find_actions_by_name(controller, "drawindex")
        assert len(result) == 2

    @patch("cli_anything.renderdoc.core.actions.rd")
    def test_find_action_by_event(self, mock_rd):
        mock_rd.ActionFlags = MockActionFlags
        from cli_anything.renderdoc.core.actions import find_action_by_event

        a1 = _make_mock_action(10, "Draw", 0x0002)
        controller = MagicMock()
        controller.GetRootActions.return_value = [a1]
        controller.GetStructuredFile.return_value = MagicMock()

        result = find_action_by_event(controller, 10)
        assert result is not None
        assert result["eventId"] == 10

        result = find_action_by_event(controller, 999)
        assert result is None

    @patch("cli_anything.renderdoc.core.actions.rd")
    def test_get_drawcalls_only(self, mock_rd):
        mock_rd.ActionFlags = MockActionFlags
        from cli_anything.renderdoc.core.actions import get_drawcalls_only

        a1 = _make_mock_action(1, "Clear", 0x0001)  # Clear
        a2 = _make_mock_action(2, "Draw", 0x0002)  # Drawcall
        a3 = _make_mock_action(3, "Marker", 0x0020)  # PushMarker

        controller = MagicMock()
        controller.GetRootActions.return_value = [a1, a2, a3]
        controller.GetStructuredFile.return_value = MagicMock()

        result = get_drawcalls_only(controller)
        assert len(result) == 1
        assert result[0]["name"] == "Draw"

    @patch("cli_anything.renderdoc.core.actions.rd")
    def test_action_summary(self, mock_rd):
        mock_rd.ActionFlags = MockActionFlags
        from cli_anything.renderdoc.core.actions import action_summary

        actions = [
            _make_mock_action(1, "Clear", 0x0001),
            _make_mock_action(2, "Draw1", 0x0002),
            _make_mock_action(3, "Draw2", 0x0002),
            _make_mock_action(4, "Dispatch", 0x0004),
            _make_mock_action(5, "Copy", 0x0200),
            _make_mock_action(6, "Marker", 0x0020),
            _make_mock_action(7, "Present", 0x0080),
        ]
        controller = MagicMock()
        controller.GetRootActions.return_value = actions
        controller.GetStructuredFile.return_value = MagicMock()

        result = action_summary(controller)
        assert result["total_actions"] == 7
        assert result["drawcalls"] == 2
        assert result["clears"] == 1
        assert result["dispatches"] == 1
        assert result["copies"] == 1
        assert result["markers"] == 1
        assert result["presents"] == 1
