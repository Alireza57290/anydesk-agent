
# RemoteUse 🚀

Remote desktop control for AI agents using vision-based primitives.

## What is RemoteUse?

An MCP server that lets AI agents control your desktop through 12 simple actions. Perfect for AI automation, testing, and remote support.

## Features

✅ **12 semantic actions** - click_at, hover_at, drag_and_drop, scroll_at, type_text_at  
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

```
pip install -r requirements.txt
```

## Quick Start

### 1. Run Server

```
python -m remoteuse.server.mcp_server
```

### 2. Configure Claude Desktop

Add to your config (`~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

```
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
Claude: "I can see Chrome and VS Code open."

Me: "Open Notepad and type 'Hello AI'"
Claude: *calls click_at(), type_text(), etc.*
Claude: "Done!"
```

## Available Actions

### Observation
- `screenshot(monitor)` - Capture screen as base64 PNG

### Mouse
- `click_at(x, y, button, count)` - Click (single/double/triple, left/right/middle)
- `hover_at(x, y, duration_ms)` - Hover to reveal menus
- `drag_and_drop(from_x, from_y, to_x, to_y, button)` - Drag operation
- `scroll_at(x, y, direction, amount)` - Scroll up/down/left/right
- `mouse_move(x, y)` - Move cursor

### Keyboard
- `type_text(text, delay_ms)` - Type string
- `type_text_at(x, y, text, clear, submit)` - **BEST for forms!**
- `key_press(key)` - Single key ("enter", "escape", "f5", "a")
- `key_combination(keys)` - Combos ("ctrl+c", "cmd+space")
- `key_hold(key)` / `key_release(key)` - Hold modifiers

### Timing
- `wait(duration_ms)` - Pause execution

## Use Cases

1. **Customer Support** - AI troubleshoots user issues
2. **Data Entry** - Automate form filling
3. **QA Testing** - Test desktop apps
4. **Personal Automation** - "Organize my desktop files"
5. **Remote Work** - Control office computer from home

## Architecture

```
AI Agent (Claude/GPT/Qwen)
    ↓ MCP Protocol
RemoteUse MCP Server
    ↓
Desktop Controller (mss + pynput)
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


## Roadmap

### v1.0 (Current) ✅
- [x] Core 12 primitives
- [x] MCP server implementation
- [x] Cross-platform support (Windows/Mac/Linux)
- [x] Safety mechanisms (auto-release keys, cleanup)
- [x] Timing configurations (fast/default/slow)

### v1.1 - Performance 🚀
- [ ] Local lightweight vision model (Florence-2/Qwen2.5-VL-7B)
- [ ] Video streaming at 30-60 FPS (vs discrete screenshots)
- [ ] FP8 quantization for 3x speedup
- [ ] 50-200ms latency (10-40x faster than cloud LLMs)

### v1.2 - Multi-User 🔐
- [ ] Session management (multiple desktops)
- [ ] WebSocket broker for remote connections
- [ ] Authentication & authorization
- [ ] Session recording/replay

### v1.3 - Cloud Ready ☁️
- [ ] WebRTC P2P (no port forwarding)
- [ ] Hosted version (like Browserbase/E2B)
- [ ] Pay-per-hour pricing model
- [ ] API rate limiting & quotas

### v2.0 - Enterprise 🏢
- [ ] Multi-monitor optimization
- [ ] Distributed deployment (control 100+ desktops)
- [ ] Audit logging & compliance
- [ ] Docker/Kubernetes deployment
- [ ] Mobile apps (Android/iOS)

## ⚠️ Safety

**RemoteUse controls your desktop directly.** The code includes:
- Auto-release held modifiers on cleanup
- Try-finally blocks in key combinations
- Emergency release script: `python emergency_release.py`

Only use with trusted AI agents!

## License

MIT

## Credits

Built with [FastMCP](https://github.com/jlowin/fastmcp), [mss](https://github.com/BoboTiG/python-mss), [pynput](https://github.com/moses-palmer/pynput).