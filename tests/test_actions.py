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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
