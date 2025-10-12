import time
import base64
import platform
import logging
from typing import Optional, Literal
from dataclasses import dataclass, field

import mss
import mss.tools
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key


@dataclass
class TimingConfig:
    """Configuration for timing delays in desktop automation."""
    mouse_move_delay: float = 0.01
    mouse_click_delay: float = 0.05
    focus_delay: float = 0.1
    key_press_delay: float = 0.01
    key_release_delay: float = 0.02
    
    @classmethod
    def default(cls) -> 'TimingConfig':
        return cls()
    
    @classmethod
    def fast(cls) -> 'TimingConfig':
        return cls(
            mouse_move_delay=0.005,
            mouse_click_delay=0.02,
            focus_delay=0.05,
            key_press_delay=0.005,
            key_release_delay=0.01
        )
    
    @classmethod
    def slow(cls) -> 'TimingConfig':
        return cls(
            mouse_move_delay=0.02,
            mouse_click_delay=0.1,
            focus_delay=0.2,
            key_press_delay=0.02,
            key_release_delay=0.05
        )


@dataclass
class ActionResult:
    success: bool
    message: str = ""
    data: dict = field(default_factory=dict)
    error: Optional[str] = None
    error_code: Optional[str] = None


class DesktopController:
    """Desktop automation controller for mouse, keyboard, and screen capture."""
    
    # Button mappings
    _BUTTON_MAP = {
        "left": Button.left,
        "right": Button.right,
        "middle": Button.middle
    }
    
    # Modifier key mappings
    _MODIFIER_MAP = {
        "ctrl": Key.ctrl,
        "control": Key.ctrl,
        "shift": Key.shift,
        "alt": Key.alt,
        "option": Key.alt,
        "cmd": Key.cmd,
        "command": Key.cmd,
        "super": Key.cmd,
        "meta": Key.cmd,
        "win": Key.cmd,
        "windows": Key.cmd,
    }
    
    # Special key mappings
    _SPECIAL_KEYS = {
        "enter": Key.enter,
        "return": Key.enter,
        "escape": Key.esc,
        "esc": Key.esc,
        "tab": Key.tab,
        "space": Key.space,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "home": Key.home,
        "end": Key.end,
        "pageup": Key.page_up,
        "pagedown": Key.page_down,
    }
    
    def __init__(self, timing_config: Optional[TimingConfig] = None, enable_logging: bool = True):
        """Initialize the desktop controller.
        
        Args:
            timing_config: Optional timing configuration (defaults to TimingConfig.default())
            enable_logging: Whether to enable logging (default: True)
        """
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self._screenshot_engine = mss.mss()
        self._os_type = platform.system()
        self._held_keys = set()
        self._timing = timing_config or TimingConfig.default()
        
        self._logger = logging.getLogger(__name__) if enable_logging else None
        if self._logger:
            self._logger.debug(f"DesktopController initialized for {self._os_type}")
        
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self._cleanup()
        return False
    
    def __del__(self):
        """Destructor with cleanup."""
        self._cleanup()
    
    def _cleanup(self):
        """Centralized cleanup of resources."""
        if hasattr(self, '_held_keys'):
            self._release_all_held_keys()
        if hasattr(self, '_screenshot_engine'):
            try:
                self._screenshot_engine.close()
            except Exception:
                pass
    
    def _release_all_held_keys(self):
        """Emergency release all held modifier keys."""
        if hasattr(self, '_held_keys') and self._held_keys:
            for key in list(self._held_keys):
                try:
                    self.keyboard.release(key)
                except Exception:
                    pass
            self._held_keys.clear()
    
    def screenshot(self, monitor: Optional[int] = None) -> ActionResult:
        """
        Capture a screenshot of the specified monitor.
        
        Args:
            monitor: Monitor index (None for primary monitor)
            
        Returns:
            ActionResult with image data including base64 encoded PNG,
            dimensions, cursor position, and timestamp
        """
        try:
            if monitor is None:
                mon = self._screenshot_engine.monitors[0]
            else:
                if monitor < 0 or monitor >= len(self._screenshot_engine.monitors):
                    return ActionResult(
                        success=False,
                        error=f"Invalid monitor index {monitor}. Available: 0-{len(self._screenshot_engine.monitors)-1}"
                    )
                mon = self._screenshot_engine.monitors[monitor]
            
            sct_img = self._screenshot_engine.grab(mon)
            
            img_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)
            
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            cursor_pos = self.mouse.position
            
            return ActionResult(
                success=True,
                data={
                    "image_base64": img_base64,
                    "width": sct_img.width,
                    "height": sct_img.height,
                    "cursor_position": {"x": cursor_pos[0], "y": cursor_pos[1]},
                    "timestamp": time.time()
                }
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def click_at(
        self,
        x: int,
        y: int,
        button: Literal["left", "right", "middle"] = "left",
        count: int = 1
    ) -> ActionResult:
        """
        Click at screen coordinates.
        
        Args:
            x: X coordinate in pixels (must be >= 0)
            y: Y coordinate in pixels (must be >= 0)
            button: Mouse button to click (left/right/middle)
            count: Number of clicks (1=single, 2=double, 3=triple)
            
        Returns:
            ActionResult with success status and message
        """
        if x < 0 or y < 0:
            return ActionResult(
                success=False,
                error=f"Coordinates must be non-negative: ({x}, {y})"
            )
        
        if count < 1:
            return ActionResult(
                success=False,
                error=f"Count must be >= 1, got {count}"
            )
        
        try:
            self.mouse.position = (x, y)
            time.sleep(self._timing.mouse_move_delay)
            
            btn = self._BUTTON_MAP[button]
            
            for _ in range(count):
                self.mouse.click(btn)
                if count > 1:
                    time.sleep(self._timing.mouse_click_delay)
            
            return ActionResult(
                success=True,
                message=f"Clicked at ({x}, {y}) with {button} button, {count} time(s)"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def hover_at(self, x: int, y: int, duration_ms: int = 300) -> ActionResult:
        """
        Move mouse to coordinates and hover for specified duration.
        
        Args:
            x: X coordinate in pixels (must be >= 0)
            y: Y coordinate in pixels (must be >= 0)
            duration_ms: Hover duration in milliseconds
            
        Returns:
            ActionResult with success status and message
        """
        if x < 0 or y < 0:
            return ActionResult(
                success=False,
                error=f"Coordinates must be non-negative: ({x}, {y})"
            )
        
        if duration_ms < 0:
            return ActionResult(
                success=False,
                error=f"Duration must be >= 0, got {duration_ms}"
            )
        
        try:
            self.mouse.position = (x, y)
            time.sleep(duration_ms / 1000.0)
            
            return ActionResult(
                success=True,
                message=f"Hovered at ({x}, {y}) for {duration_ms}ms"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def drag_and_drop(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        button: Literal["left", "right", "middle"] = "left"
    ) -> ActionResult:
        """
        Drag from one location to another.
        
        Args:
            from_x: Starting X coordinate (must be >= 0)
            from_y: Starting Y coordinate (must be >= 0)
            to_x: Ending X coordinate (must be >= 0)
            to_y: Ending Y coordinate (must be >= 0)
            button: Mouse button to use for dragging
            
        Returns:
            ActionResult with success status and message
        """
        if from_x < 0 or from_y < 0 or to_x < 0 or to_y < 0:
            return ActionResult(
                success=False,
                error=f"All coordinates must be non-negative: from ({from_x}, {from_y}) to ({to_x}, {to_y})"
            )
        
        try:
            btn = self._BUTTON_MAP[button]
            
            self.mouse.position = (from_x, from_y)
            time.sleep(self._timing.mouse_move_delay)
            
            self.mouse.press(btn)
            time.sleep(self._timing.mouse_click_delay)
            
            self.mouse.position = (to_x, to_y)
            time.sleep(self._timing.mouse_click_delay)
            
            self.mouse.release(btn)
            
            return ActionResult(
                success=True,
                message=f"Dragged from ({from_x}, {from_y}) to ({to_x}, {to_y})"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def scroll_at(
        self,
        x: int,
        y: int,
        direction: Literal["up", "down", "left", "right"] = "down",
        amount: int = 3
    ) -> ActionResult:
        """
        Scroll at specified coordinates.
        
        Args:
            x: X coordinate in pixels (must be >= 0)
            y: Y coordinate in pixels (must be >= 0)
            direction: Scroll direction (up/down/left/right)
            amount: Scroll amount (positive integer)
            
        Returns:
            ActionResult with success status and message
        """
        if x < 0 or y < 0:
            return ActionResult(
                success=False,
                error=f"Coordinates must be non-negative: ({x}, {y})"
            )
        
        if amount < 0:
            return ActionResult(
                success=False,
                error=f"Amount must be >= 0, got {amount}"
            )
        
        try:
            self.mouse.position = (x, y)
            time.sleep(self._timing.mouse_move_delay)
            
            scroll_map = {
                "up": (0, amount),
                "down": (0, -amount),
                "left": (-amount, 0),
                "right": (amount, 0)
            }
            dx, dy = scroll_map[direction]
            
            self.mouse.scroll(dx, dy)
            
            return ActionResult(
                success=True,
                message=f"Scrolled {direction} by {amount} at ({x}, {y})"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def mouse_move(self, x: int, y: int) -> ActionResult:
        """
        Move mouse cursor to coordinates.
        
        Args:
            x: X coordinate in pixels (must be >= 0)
            y: Y coordinate in pixels (must be >= 0)
            
        Returns:
            ActionResult with success status and message
        """
        if x < 0 or y < 0:
            return ActionResult(
                success=False,
                error=f"Coordinates must be non-negative: ({x}, {y})"
            )
        
        try:
            self.mouse.position = (x, y)
            return ActionResult(
                success=True,
                message=f"Moved cursor to ({x}, {y})"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def type_text(self, text: str, delay_ms: int = 0) -> ActionResult:
        """
        Type text at current cursor position.
        
        Args:
            text: Text to type
            delay_ms: Delay between keystrokes in milliseconds
            
        Returns:
            ActionResult with success status and message
        """
        if delay_ms < 0:
            return ActionResult(
                success=False,
                error=f"Delay must be >= 0, got {delay_ms}"
            )
        
        try:
            for char in text:
                self.keyboard.type(char)
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
            
            return ActionResult(
                success=True,
                message=f"Typed: {text[:50]}..." if len(text) > 50 else f"Typed: {text}"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def type_text_at(
        self,
        x: int,
        y: int,
        text: str,
        clear: bool = True,
        submit: bool = False
    ) -> ActionResult:
        """
        Click at coordinates, optionally clear field, type text, and optionally submit.
        
        Args:
            x: X coordinate in pixels (must be >= 0)
            y: Y coordinate in pixels (must be >= 0)
            text: Text to type
            clear: Whether to clear existing text (Ctrl+A, Backspace)
            submit: Whether to press Enter after typing
            
        Returns:
            ActionResult with success status and message
        """
        if x < 0 or y < 0:
            return ActionResult(
                success=False,
                error=f"Coordinates must be non-negative: ({x}, {y})"
            )
        
        try:
            self.mouse.position = (x, y)
            time.sleep(self._timing.mouse_move_delay)
            self.mouse.click(Button.left)
            time.sleep(self._timing.focus_delay)
            
            if clear:
                modifier_key = Key.cmd if self._os_type == "Darwin" else Key.ctrl
                try:
                    self.keyboard.press(modifier_key)
                    self.keyboard.press('a')
                    self.keyboard.release('a')
                finally:
                    self.keyboard.release(modifier_key)
                time.sleep(self._timing.key_release_delay)
                self.keyboard.press(Key.backspace)
                self.keyboard.release(Key.backspace)
                time.sleep(self._timing.key_release_delay)
            
            self.keyboard.type(text)
            time.sleep(self._timing.mouse_click_delay)
            
            if submit:
                self.keyboard.press(Key.enter)
                self.keyboard.release(Key.enter)
            
            return ActionResult(
                success=True,
                message=f"Filled field at ({x}, {y}) with text"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def key_press(self, key: str) -> ActionResult:
        """
        Press and release a single key.
        
        Args:
            key: Key name (e.g., 'a', 'enter', 'f5', 'escape')
            
        Returns:
            ActionResult with success status and message
        """
        try:
            key_lower = key.lower()
            
            # Check special keys
            if key_lower in self._SPECIAL_KEYS:
                key_obj = self._SPECIAL_KEYS[key_lower]
                self.keyboard.press(key_obj)
                self.keyboard.release(key_obj)
            # Check modifier keys
            elif key_lower in self._MODIFIER_MAP:
                key_obj = self._MODIFIER_MAP[key_lower]
                self.keyboard.press(key_obj)
                self.keyboard.release(key_obj)
            # Check function keys (F1-F12)
            elif key_lower.startswith('f'):
                try:
                    f_num = int(key_lower[1:])
                    if 1 <= f_num <= 12:
                        key_obj = getattr(Key, f'f{f_num}')
                        self.keyboard.press(key_obj)
                        self.keyboard.release(key_obj)
                    else:
                        return ActionResult(
                            success=False,
                            error=f"Invalid F key: {key}. Valid range: F1-F12"
                        )
                except (ValueError, AttributeError):
                    # Not a valid F-key, treat as regular character
                    self.keyboard.press(key)
                    self.keyboard.release(key)
            else:
                self.keyboard.press(key)
                self.keyboard.release(key)
            
            return ActionResult(success=True, message=f"Pressed key: {key}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def key_combination(self, keys: str) -> ActionResult:
        """
        Press a key combination (e.g., 'ctrl+c', 'alt+f4').
        
        Args:
            keys: Key combination string separated by '+' (e.g., 'ctrl+shift+a')
            
        Returns:
            ActionResult with success status and message
        """
        modifiers = []
        try:
            parts = keys.lower().split('+')
            
            if len(parts) < 2:
                return ActionResult(
                    success=False,
                    error=f"Key combination must have at least 2 parts separated by '+', got: {keys}"
                )
            
            main_key = None
            
            for part in parts[:-1]:
                if part in self._MODIFIER_MAP:
                    modifiers.append(self._MODIFIER_MAP[part])
                else:
                    return ActionResult(
                        success=False,
                        error=f"Unknown modifier: {part}"
                    )
            
            main_key = parts[-1]
            
            for mod in modifiers:
                self.keyboard.press(mod)
                time.sleep(self._timing.key_press_delay)
            
            if main_key in self._MODIFIER_MAP:
                self.keyboard.press(self._MODIFIER_MAP[main_key])
                self.keyboard.release(self._MODIFIER_MAP[main_key])
            else:
                self.keyboard.press(main_key)
                self.keyboard.release(main_key)
            
            time.sleep(self._timing.key_release_delay)
            
            return ActionResult(
                success=True,
                message=f"Pressed combination: {keys}"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
        finally:
            for mod in reversed(modifiers):
                try:
                    self.keyboard.release(mod)
                except Exception:
                    pass
    
    def key_hold(self, key: str) -> ActionResult:
        """
        Hold down a modifier key.
        
        Args:
            key: Modifier key name (ctrl, shift, alt, cmd, super)
            
        Returns:
            ActionResult with success status and message
        """
        try:
            key_lower = key.lower()
            if key_lower not in self._MODIFIER_MAP:
                return ActionResult(
                    success=False,
                    error=f"Only modifier keys can be held: {list(self._MODIFIER_MAP.keys())}"
                )
            
            key_obj = self._MODIFIER_MAP[key_lower]
            self.keyboard.press(key_obj)
            self._held_keys.add(key_obj)
            return ActionResult(success=True, message=f"Holding key: {key}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def key_release(self, key: str) -> ActionResult:
        """
        Release a held modifier key.
        
        Args:
            key: Modifier key name (ctrl, shift, alt, cmd, super)
            
        Returns:
            ActionResult with success status and message
        """
        try:
            key_lower = key.lower()
            if key_lower not in self._MODIFIER_MAP:
                return ActionResult(
                    success=False,
                    error=f"Only modifier keys can be released: {list(self._MODIFIER_MAP.keys())}"
                )
            
            key_obj = self._MODIFIER_MAP[key_lower]
            self.keyboard.release(key_obj)
            self._held_keys.discard(key_obj)
            return ActionResult(success=True, message=f"Released key: {key}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def wait(self, duration_ms: int) -> ActionResult:
        """
        Wait for specified duration.
        
        Args:
            duration_ms: Duration to wait in milliseconds
            
        Returns:
            ActionResult with success status and message
        """
        if duration_ms < 0:
            return ActionResult(
                success=False,
                error=f"Duration must be >= 0, got {duration_ms}"
            )
        
        try:
            time.sleep(duration_ms / 1000.0)
            return ActionResult(
                success=True,
                message=f"Waited {duration_ms}ms"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
