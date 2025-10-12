import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from remoteuse.core.actions import DesktopController, ActionResult


@pytest.fixture
def controller():
    return DesktopController()


class TestActionResult:
    def test_success_result(self):
        result = ActionResult(success=True, message="Test message")
        assert result.success is True
        assert result.message == "Test message"
        assert result.error is None
    
    def test_error_result(self):
        result = ActionResult(success=False, error="Test error")
        assert result.success is False
        assert result.error == "Test error"


class TestScreenshotAction:
    def test_screenshot_returns_data(self, controller):
        result = controller.screenshot()
        assert result.success is True
        assert "image_base64" in result.data
        assert "width" in result.data
        assert "height" in result.data
        assert "cursor_position" in result.data
        assert "timestamp" in result.data
    
    def test_screenshot_image_format(self, controller):
        result = controller.screenshot()
        assert result.success is True
        assert isinstance(result.data["image_base64"], str)
        assert len(result.data["image_base64"]) > 0
    
    def test_screenshot_dimensions(self, controller):
        result = controller.screenshot()
        assert result.success is True
        assert result.data["width"] > 0
        assert result.data["height"] > 0


class TestMouseActions:
    def test_click_at_success(self, controller):
        result = controller.click_at(500, 500)
        assert result.success is True
        assert "500, 500" in result.message
    
    def test_click_at_with_button(self, controller):
        result = controller.click_at(500, 500, button="right")
        assert result.success is True
        assert "right" in result.message
    
    def test_click_at_double_click(self, controller):
        result = controller.click_at(500, 500, count=2)
        assert result.success is True
        assert "2" in result.message
    
    def test_hover_at(self, controller):
        result = controller.hover_at(500, 500, duration_ms=100)
        assert result.success is True
        assert "500, 500" in result.message
    
    def test_drag_and_drop(self, controller):
        result = controller.drag_and_drop(100, 100, 200, 200)
        assert result.success is True
        assert "100, 100" in result.message
        assert "200, 200" in result.message
    
    def test_scroll_at(self, controller):
        result = controller.scroll_at(500, 500, direction="down", amount=3)
        assert result.success is True
        assert "down" in result.message
    
    def test_mouse_move(self, controller):
        result = controller.mouse_move(300, 300)
        assert result.success is True
        assert "300, 300" in result.message


class TestKeyboardActions:
    def test_type_text(self, controller):
        result = controller.type_text(" ")
        assert result.success is True
    
    def test_type_text_with_delay(self, controller):
        result = controller.type_text(" ", delay_ms=10)
        assert result.success is True
    
    def test_type_text_at(self, controller):
        result = controller.type_text_at(9999, 9999, " ")
        assert result.success is True
    
    def test_key_press_special_keys(self, controller):
        result = controller.key_press("escape")
        assert result.success is True
    
    def test_key_press_function_keys(self, controller):
        result = controller.key_press("f12")
        assert result.success is True
    
    def test_key_combination_safe(self, controller):
        result = controller.key_combination("shift+a")
        assert result.success is True
        assert "shift+a" in result.message
    
    def test_key_combination_multiple_modifiers(self, controller):
        result = controller.key_combination("ctrl+alt+a")
        assert result.success is True
    
    def test_key_hold_and_release(self, controller):
        hold_result = controller.key_hold("shift")
        assert hold_result.success is True
        
        release_result = controller.key_release("shift")
        assert release_result.success is True
    
    def test_held_keys_cleanup(self, controller):
        controller.key_hold("shift")
        controller._release_all_held_keys()
        assert len(controller._held_keys) == 0


class TestTimingActions:
    def test_wait(self, controller):
        result = controller.wait(100)
        assert result.success is True
        assert "100" in result.message


class TestErrorHandling:
    def test_invalid_button(self, controller):
        result = controller.click_at(500, 500, button="invalid")
        assert result.success is False
        assert result.error is not None
    
    def test_invalid_direction(self, controller):
        result = controller.scroll_at(500, 500, direction="invalid")
        assert result.success is False
        assert result.error is not None
    
    def test_negative_coordinates_click(self, controller):
        result = controller.click_at(-10, 100)
        assert result.success is False
        assert "non-negative" in result.error.lower()
    
    def test_negative_coordinates_hover(self, controller):
        result = controller.hover_at(100, -10)
        assert result.success is False
        assert "non-negative" in result.error.lower()
    
    def test_negative_count(self, controller):
        result = controller.click_at(100, 100, count=0)
        assert result.success is False
        assert "must be >= 1" in result.error
    
    def test_negative_duration(self, controller):
        result = controller.hover_at(100, 100, duration_ms=-100)
        assert result.success is False
        assert "must be >= 0" in result.error
    
    def test_invalid_monitor_index(self, controller):
        result = controller.screenshot(monitor=999)
        assert result.success is False
        assert "Invalid monitor" in result.error
    
    def test_key_combination_single_key(self, controller):
        result = controller.key_combination("a")
        assert result.success is False
        assert "at least 2 parts" in result.error
    
    def test_key_combination_invalid_modifier(self, controller):
        result = controller.key_combination("invalid+a")
        assert result.success is False
        assert "Unknown modifier" in result.error
    
    def test_key_hold_non_modifier(self, controller):
        result = controller.key_hold("a")
        assert result.success is False
        assert "modifier keys" in result.error.lower()


class TestContextManager:
    def test_context_manager_usage(self):
        with DesktopController() as controller:
            result = controller.wait(10)
            assert result.success is True
    
    def test_context_manager_cleanup(self):
        from remoteuse.core.actions import TimingConfig
        with DesktopController(timing_config=TimingConfig.fast()) as controller:
            controller.key_hold("shift")
            assert len(controller._held_keys) > 0
        


class TestTimingConfiguration:
    def test_default_timing(self):
        from remoteuse.core.actions import TimingConfig
        config = TimingConfig.default()
        assert config.mouse_move_delay == 0.01
        assert config.mouse_click_delay == 0.05
    
    def test_fast_timing(self):
        from remoteuse.core.actions import TimingConfig
        config = TimingConfig.fast()
        assert config.mouse_move_delay < 0.01
        assert config.mouse_click_delay < 0.05
    
    def test_slow_timing(self):
        from remoteuse.core.actions import TimingConfig
        config = TimingConfig.slow()
        assert config.mouse_move_delay > 0.01
        assert config.mouse_click_delay > 0.05
    
    def test_custom_timing(self):
        from remoteuse.core.actions import TimingConfig
        controller = DesktopController(timing_config=TimingConfig.fast())
        assert controller._timing.mouse_move_delay < 0.01
    
    def test_logging_disabled(self):
        controller = DesktopController(enable_logging=False)
        assert controller._logger is None


class TestActionResultFields:
    def test_action_result_with_error_code(self):
        result = ActionResult(
            success=False,
            error="Test error",
            error_code="TEST_ERROR"
        )
        assert result.success is False
        assert result.error == "Test error"
        assert result.error_code == "TEST_ERROR"
    
    def test_action_result_with_data(self):
        result = ActionResult(
            success=True,
            message="Success",
            data={"key": "value"}
        )
        assert result.success is True
        assert result.data["key"] == "value"


class TestResourceCleanup:
    def test_cleanup_method(self, controller):
        controller.key_hold("shift")
        assert len(controller._held_keys) > 0
        controller._cleanup()
        assert len(controller._held_keys) == 0
    
    def test_held_keys_tracking(self, controller):
        initial_count = len(controller._held_keys)
        controller.key_hold("shift")
        assert len(controller._held_keys) == initial_count + 1
        controller.key_release("shift")
        assert len(controller._held_keys) == initial_count


class TestCoordinateValidation:
    def test_drag_negative_from_coords(self, controller):
        result = controller.drag_and_drop(-10, 100, 200, 200)
        assert result.success is False
        assert "non-negative" in result.error.lower()
    
    def test_drag_negative_to_coords(self, controller):
        result = controller.drag_and_drop(100, 100, 200, -10)
        assert result.success is False
        assert "non-negative" in result.error.lower()
    
    def test_scroll_negative_amount(self, controller):
        result = controller.scroll_at(100, 100, amount=-5)
        assert result.success is False
        assert "must be >= 0" in result.error
    
    def test_type_text_negative_delay(self, controller):
        result = controller.type_text("test", delay_ms=-10)
        assert result.success is False
        assert "must be >= 0" in result.error
    
    def test_wait_negative_duration(self, controller):
        result = controller.wait(-100)
        assert result.success is False
        assert "must be >= 0" in result.error


class TestKeyboardSpecialKeys:
    def test_all_special_keys_exist(self, controller):
        special_keys = ["enter", "escape", "tab", "space", "backspace", "delete"]
        for key in special_keys:
            result = controller.key_press(key)
            assert result.success is True
    
    def test_arrow_keys(self, controller):
        arrow_keys = ["up", "down", "left", "right"]
        for key in arrow_keys:
            result = controller.key_press(key)
            assert result.success is True
    
    def test_navigation_keys(self, controller):
        nav_keys = ["home", "end", "pageup", "pagedown"]
        for key in nav_keys:
            result = controller.key_press(key)
            assert result.success is True
    
    def test_function_keys_range(self, controller):
        for i in range(1, 13):
            result = controller.key_press(f"f{i}")
            assert result.success is True
    
    def test_invalid_function_key(self, controller):
        result = controller.key_press("f99")
        assert result.success is False


class TestMouseButtonTypes:
    def test_left_button(self, controller):
        result = controller.click_at(500, 500, button="left")
        assert result.success is True
        assert "left" in result.message
    
    def test_right_button(self, controller):
        result = controller.click_at(500, 500, button="right")
        assert result.success is True
        assert "right" in result.message
    
    def test_middle_button(self, controller):
        result = controller.click_at(500, 500, button="middle")
        assert result.success is True
        assert "middle" in result.message
    
    def test_drag_with_different_buttons(self, controller):
        for button in ["left", "right", "middle"]:
            result = controller.drag_and_drop(100, 100, 200, 200, button=button)
            assert result.success is True


class TestScrollDirections:
    def test_all_scroll_directions(self, controller):
        directions = ["up", "down", "left", "right"]
        for direction in directions:
            result = controller.scroll_at(500, 500, direction=direction, amount=1)
            assert result.success is True
            assert direction in result.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
