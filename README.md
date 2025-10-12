# RemoteUse 🚀

Remote desktop control for AI agents using vision-based primitives.

## What is RemoteUse?

An MCP server that lets AI agents control your desktop through 12 simple actions. Perfect for AI automation, testing, and remote support.

## Features

✅ **12 semantic actions** - click_at, hover_at, drag_and_drop, scroll_at, type_text_at, etc.  
✅ **Vision-first design** - AI sees screen, decides actions  
✅ **Cross-platform** - Windows, macOS, Linux  
✅ **MCP native** - Works with Claude Desktop, any MCP client  
✅ **Ultra-fast screenshots** - 16-47ms using mss library  
✅ **Safety mechanisms** - Auto-releases stuck keys, emergency cleanup  
✅ **Zero-config** - Install, run, connect

## ⚠️ Safety Warning

**RemoteUse controls your desktop directly.** Keys pressed will execute on your system. The code includes:
- **Automatic key release** - All held modifiers are released when controller is destroyed
- **Emergency cleanup** - Run `python emergency_release.py` if keys get stuck
- **Try-finally blocks** - Key combinations always release modifiers even on error

**If keys get stuck:** Run the emergency release script immediately:
```bash
python emergency_release.py
```  

## Installation

### Install dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Run RemoteUse Server

```bash
python -m remoteuse.server.mcp_server
```

### 2. Configure Claude Desktop

Add to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "remoteuse": {
      "command": "python",
      "args": ["-m", "remoteuse.server.mcp_server"]
    }
  }
}
```

### 3. Use from Claude

```
Me: "Screenshot my desktop"
Claude: *calls screenshot() tool*
Claude: "I can see your desktop. You have Chrome and VS Code open."

Me: "Open Notepad and type 'Hello AI'"
Claude: *calls click_at(), type_text(), etc.*
Claude: "Done! I opened Notepad and typed the message."
```

## Available Actions

### Observation
- **`screenshot(monitor)`** - Capture screen as base64-encoded PNG
  - Returns: image_base64, width, height, cursor_position, timestamp

### Mouse Actions
- **`click_at(x, y, button, count)`** - Click at coordinates
  - button: "left", "right", "middle"
  - count: 1 (single), 2 (double), 3 (triple)
  
- **`hover_at(x, y, duration_ms)`** - Hover to reveal menus/tooltips
  
- **`drag_and_drop(from_x, from_y, to_x, to_y, button)`** - Drag operation
  
- **`scroll_at(x, y, direction, amount)`** - Scroll at position
  - direction: "up", "down", "left", "right"
  
- **`mouse_move(x, y)`** - Move cursor (low-level control)

### Keyboard Actions
- **`type_text(text, delay_ms)`** - Type string at cursor
  
- **`type_text_at(x, y, text, clear, submit)`** - **BEST for forms!**
  - Click field, optionally clear, type, optionally submit
  
- **`key_press(key)`** - Press single key
  - Examples: "enter", "escape", "tab", "f5", "a"
  
- **`key_combination(keys)`** - Key combos
  - Examples: "ctrl+c", "alt+f4", "cmd+space", "ctrl+shift+t"
  
- **`key_hold(key)` / `key_release(key)`** - Hold modifiers
  - For multi-select: Ctrl+click, Shift+click

### Timing
- **`wait(duration_ms)`** - Pause execution

## Use Cases

1. **Customer Support** - AI troubleshoots user issues remotely
2. **Data Entry** - Automate form filling across any application
3. **QA Testing** - Test desktop applications automatically
4. **Personal Automation** - "Organize my desktop files", "Check my email"
5. **Remote Work** - Control office computer from home

## Architecture

```
┌─────────────────┐
│  AI Agent       │  Claude/GPT/Qwen analyzes screenshots
│ (Vision Model)  │  Decides what actions to take
└────────┬────────┘
         │ MCP Protocol
┌────────▼────────┐
│  RemoteUse      │  FastMCP server exposes 12 tools
│  MCP Server     │  Routes commands to desktop
└────────┬────────┘
         │
┌────────▼────────┐
│ Desktop Agent   │  Executes on physical laptop
│ (Your Laptop)   │  mss (screenshots) + pynput (input)
└─────────────────┘
```

## Why RemoteUse?

**Vision models are getting AMAZING** (Gemini 2.5, Qwen3-VL, Claude 3.5). They can:
- See screens perfectly
- Read text (OCR built-in)
- Understand UI layouts
- Navigate complex apps

**But they need primitives** - basic mouse/keyboard actions to execute their vision.

**RemoteUse provides those primitives** in the cleanest possible API.

## Examples

### Example 1: Open Notepad and Type

```python
from remoteuse.core.actions import DesktopController

controller = DesktopController()

controller.screenshot()
controller.click_at(20, 1060)
controller.wait(500)
controller.type_text("notepad")
controller.key_press("enter")
controller.wait(2000)
controller.type_text("Hello from AI!")
```

### Example 2: Fill Web Form

```python
controller.type_text_at(400, 300, "john@example.com", submit=False)
controller.type_text_at(400, 400, "John Smith", submit=False)
controller.type_text_at(400, 500, "My message", submit=True)
```

### Example 3: Multi-select Files

```python
controller.key_hold("ctrl")
controller.click_at(100, 200)
controller.click_at(100, 300)
controller.click_at(100, 400)
controller.key_release("ctrl")
controller.drag_and_drop(100, 200, 800, 600)
```

## Requirements

- Python 3.9+
- Windows, macOS, or Linux
- Dependencies: fastmcp, mss, pynput

## Roadmap

- [x] Core 12 primitives
- [x] MCP server
- [x] Cross-platform support
- [ ] WebRTC P2P (no port forwarding needed)
- [ ] Multi-session support
- [ ] Session recording/replay
- [ ] Browser integration for cloud deployment
- [ ] Mobile apps (Android/iOS)

## Security Notes

⚠️ **Important**: RemoteUse gives AI agents direct control over your desktop. Only use with trusted AI agents and secure your MCP server appropriately.

## License

MIT

## Credits

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [mss](https://github.com/BoboTiG/python-mss) - Ultra-fast screenshots
- [pynput](https://github.com/moses-palmer/pynput) - Cross-platform input control

Inspired by Browserbase, E2B, and the amazing AI agent community.