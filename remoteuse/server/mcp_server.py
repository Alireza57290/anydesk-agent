from fastmcp import FastMCP
from typing import Optional, Literal
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from remoteuse.core.actions import DesktopController

mcp = FastMCP(
    name="RemoteUse"
)

controller = DesktopController()


@mcp.tool()
def screenshot(monitor: Optional[int] = None) -> dict:
    result = controller.screenshot(monitor)
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
    result = controller.click_at(x, y, button, count)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def hover_at(x: int, y: int, duration_ms: int = 300) -> str:
    result = controller.hover_at(x, y, duration_ms)
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
    result = controller.drag_and_drop(from_x, from_y, to_x, to_y, button)
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
    result = controller.scroll_at(x, y, direction, amount)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def mouse_move(x: int, y: int) -> str:
    result = controller.mouse_move(x, y)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def type_text(text: str, delay_ms: int = 0) -> str:
    result = controller.type_text(text, delay_ms)
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
    result = controller.type_text_at(x, y, text, clear, submit)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def key_press(key: str) -> str:
    result = controller.key_press(key)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def key_combination(keys: str) -> str:
    result = controller.key_combination(keys)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def key_hold(key: str) -> str:
    result = controller.key_hold(key)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def key_release(key: str) -> str:
    result = controller.key_release(key)
    if result.success:
        return result.message
    else:
        raise Exception(result.error)


@mcp.tool()
def wait(duration_ms: int) -> str:
    result = controller.wait(duration_ms)
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
