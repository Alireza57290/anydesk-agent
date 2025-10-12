"""RemoteUse MCP Server - Desktop automation for AI agents."""

from fastmcp import FastMCP
from typing import Optional, Literal

from remoteuse.core.actions import DesktopController

mcp = FastMCP(name="RemoteUse")

# Singleton controller instance
_controller: Optional[DesktopController] = None


def get_controller() -> DesktopController:
    """Get or create the desktop controller instance."""
    global _controller
    if _controller is None:
        _controller = DesktopController()
    return _controller


@mcp.tool()
def screenshot(monitor: Optional[int] = None) -> dict:
    """Capture a screenshot of the specified monitor."""
    result = get_controller().screenshot(monitor)
    if result.success:
        return result.data
    else:
        raise Exception(result.error)


@mcp.tool()
def click_at(
    x: int,
    y: int,
    button: Literal["left", "right", "middle"] = "left",
    count: int = 1
) -> str:
    """Click at screen coordinates."""
    result = get_controller().click_at(x, y, button, count)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def hover_at(x: int, y: int, duration_ms: int = 300) -> str:
    """Hover mouse at coordinates for specified duration."""
    result = get_controller().hover_at(x, y, duration_ms)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def drag_and_drop(
    from_x: int,
    from_y: int,
    to_x: int,
    to_y: int,
    button: Literal["left", "right", "middle"] = "left"
) -> str:
    """Drag from one location to another."""
    result = get_controller().drag_and_drop(from_x, from_y, to_x, to_y, button)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def scroll_at(
    x: int,
    y: int,
    direction: Literal["up", "down", "left", "right"] = "down",
    amount: int = 3
) -> str:
    """Scroll at specified coordinates."""
    result = get_controller().scroll_at(x, y, direction, amount)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def mouse_move(x: int, y: int) -> str:
    """Move mouse cursor to coordinates."""
    result = get_controller().mouse_move(x, y)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def type_text(text: str, delay_ms: int = 0) -> str:
    """Type text at current cursor position."""
    result = get_controller().type_text(text, delay_ms)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def type_text_at(
    x: int,
    y: int,
    text: str,
    clear: bool = True,
    submit: bool = False
) -> str:
    """Click at coordinates, optionally clear, type text, and optionally submit."""
    result = get_controller().type_text_at(x, y, text, clear, submit)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def key_press(key: str) -> str:
    """Press and release a single key."""
    result = get_controller().key_press(key)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def key_combination(keys: str) -> str:
    """Press a key combination (e.g., 'ctrl+c')."""
    result = get_controller().key_combination(keys)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def key_hold(key: str) -> str:
    """Hold down a modifier key."""
    result = get_controller().key_hold(key)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def key_release(key: str) -> str:
    """Release a held modifier key."""
    result = get_controller().key_release(key)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def wait(duration_ms: int) -> str:
    """Wait for specified duration in milliseconds."""
    result = get_controller().wait(duration_ms)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


def main():
    print("🚀 RemoteUse MCP Server starting...")
    print("📱 AI agents can now control this desktop!")
    print("=" * 60)
    mcp.run()


if __name__ == "__main__":
    main()
