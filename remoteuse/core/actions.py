import time
import base64
import platform
from io import BytesIO
from typing import Optional, Literal, Tuple
from dataclasses import dataclass, field

import mss
import mss.tools
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key


@dataclass
class ActionResult:
    success: bool
    message: str = ""
    data: dict = field(default_factory=dict)
    error: str = None


class DesktopController:
    
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self._screenshot_engine = mss.mss()
        self._os_type = platform.system()
        self._held_keys = set()
        
    def __del__(self):
        self._release_all_held_keys()
        if hasattr(self, '_screenshot_engine'):
            self._screenshot_engine.close()
    
    def _release_all_held_keys(self):
        """Emergency release all held modifier keys"""
        if hasattr(self, '_held_keys') and self._held_keys:
            for key in list(self._held_keys):
                try:
                    self.keyboard.release(key)
                except:
                    pass
            self._held_keys.clear()
    
    def screenshot(self, monitor: Optional[int] = None) -> ActionResult:
        try:
            if monitor is None:
                mon = self._screenshot_engine.monitors[0]
            else:
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
        try:
            self.mouse.position = (x, y)
            time.sleep(0.01)
            
            button_map = {
                "left": Button.left,
                "right": Button.right,
                "middle": Button.middle
            }
            btn = button_map[button]
            
            for _ in range(count):
                self.mouse.click(btn)
                if count > 1:
                    time.sleep(0.05)
            
            return ActionResult(
                success=True,
                message=f"Clicked at ({x}, {y}) with {button} button, {count} time(s)"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def hover_at(self, x: int, y: int, duration_ms: int = 300) -> ActionResult:
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
        try:
            button_map = {
                "left": Button.left,
                "right": Button.right,
                "middle": Button.middle
            }
            btn = button_map[button]
            
            self.mouse.position = (from_x, from_y)
            time.sleep(0.01)
            
            self.mouse.press(btn)
            time.sleep(0.05)
            
            self.mouse.position = (to_x, to_y)
            time.sleep(0.05)
            
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
        try:
            self.mouse.position = (x, y)
            time.sleep(0.01)
            
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
        try:
            self.mouse.position = (x, y)
            return ActionResult(
                success=True,
                message=f"Moved cursor to ({x}, {y})"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def type_text(self, text: str, delay_ms: int = 0) -> ActionResult:
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
        try:
            self.mouse.position = (x, y)
            time.sleep(0.01)
            self.mouse.click(Button.left)
            time.sleep(0.1)
            
            if clear:
                modifier_key = Key.cmd if self._os_type == "Darwin" else Key.ctrl
                self.keyboard.press(modifier_key)
                self.keyboard.press('a')
                self.keyboard.release('a')
                self.keyboard.release(modifier_key)
                time.sleep(0.02)
                self.keyboard.press(Key.backspace)
                self.keyboard.release(Key.backspace)
                time.sleep(0.02)
            
            self.keyboard.type(text)
            time.sleep(0.05)
            
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
        try:
            special_keys = {
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
                "ctrl": Key.ctrl,
                "shift": Key.shift,
                "alt": Key.alt,
                "cmd": Key.cmd,
                "super": Key.cmd,
                "meta": Key.cmd,
            }
            
            key_lower = key.lower()
            if key_lower in special_keys:
                key_obj = special_keys[key_lower]
                self.keyboard.press(key_obj)
                self.keyboard.release(key_obj)
            elif key.startswith('f') and len(key) <= 3:
                try:
                    f_num = int(key[1:])
                    if 1 <= f_num <= 12:
                        key_obj = getattr(Key, f'f{f_num}')
                        self.keyboard.press(key_obj)
                        self.keyboard.release(key_obj)
                    else:
                        raise ValueError(f"Invalid F key: {key}")
                except:
                    self.keyboard.press(key)
                    self.keyboard.release(key)
            else:
                self.keyboard.press(key)
                self.keyboard.release(key)
            
            return ActionResult(success=True, message=f"Pressed key: {key}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def key_combination(self, keys: str) -> ActionResult:
        modifiers = []
        try:
            parts = keys.lower().split('+')
            
            modifier_map = {
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
            
            main_key = None
            
            for part in parts[:-1]:
                if part in modifier_map:
                    modifiers.append(modifier_map[part])
                else:
                    return ActionResult(
                        success=False,
                        error=f"Unknown modifier: {part}"
                    )
            
            main_key = parts[-1]
            
            for mod in modifiers:
                self.keyboard.press(mod)
                time.sleep(0.01)
            
            if main_key in modifier_map:
                self.keyboard.press(modifier_map[main_key])
                self.keyboard.release(modifier_map[main_key])
            else:
                self.keyboard.press(main_key)
                self.keyboard.release(main_key)
            
            time.sleep(0.02)
            
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
                except:
                    pass
    
    def key_hold(self, key: str) -> ActionResult:
        try:
            modifier_map = {
                "ctrl": Key.ctrl,
                "shift": Key.shift,
                "alt": Key.alt,
                "cmd": Key.cmd,
                "super": Key.cmd,
            }
            
            key_lower = key.lower()
            if key_lower not in modifier_map:
                return ActionResult(
                    success=False,
                    error=f"Only modifier keys can be held: {list(modifier_map.keys())}"
                )
            
            key_obj = modifier_map[key_lower]
            self.keyboard.press(key_obj)
            self._held_keys.add(key_obj)
            return ActionResult(success=True, message=f"Holding key: {key}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def key_release(self, key: str) -> ActionResult:
        try:
            modifier_map = {
                "ctrl": Key.ctrl,
                "shift": Key.shift,
                "alt": Key.alt,
                "cmd": Key.cmd,
                "super": Key.cmd,
            }
            
            key_lower = key.lower()
            if key_lower not in modifier_map:
                return ActionResult(
                    success=False,
                    error=f"Only modifier keys can be released: {list(modifier_map.keys())}"
                )
            
            key_obj = modifier_map[key_lower]
            self.keyboard.release(key_obj)
            self._held_keys.discard(key_obj)
            return ActionResult(success=True, message=f"Released key: {key}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    def wait(self, duration_ms: int) -> ActionResult:
        try:
            time.sleep(duration_ms / 1000.0)
            return ActionResult(
                success=True,
                message=f"Waited {duration_ms}ms"
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
