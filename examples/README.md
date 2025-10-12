# RemoteUse Examples

This directory contains example scripts demonstrating RemoteUse capabilities.

## Running Examples

```bash
python examples/test_remoteuse.py
```

Then select an example:

1. **AI Agent Workflow** - Demonstrates opening Notepad and typing
2. **Form Filling** - Shows how to fill web forms
3. **Multi-select Files** - File selection with Ctrl+click
4. **Scroll Test** - Scrolling demonstration

## Claude Desktop Configuration

The `claude_desktop_config.json` file shows how to configure Claude Desktop to use RemoteUse:

**Windows:** Copy to `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** Copy to `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux:** Copy to `~/.config/Claude/claude_desktop_config.json`

## Example Workflows

### Basic Screenshot

```python
from remoteuse.core.actions import DesktopController

controller = DesktopController()
result = controller.screenshot()

if result.success:
    print(f"Screenshot captured: {result.data['width']}x{result.data['height']}")
```

### Click and Type

```python
controller.click_at(100, 200)
controller.wait(500)
controller.type_text("Hello World!")
```

### Form Filling (Best Practice)

```python
controller.type_text_at(300, 200, "user@example.com", clear=True, submit=False)
controller.type_text_at(300, 250, "password123", clear=True, submit=True)
```

### Keyboard Shortcuts

```python
controller.key_combination("ctrl+c")
controller.key_combination("ctrl+v")
controller.key_combination("alt+tab")
```

### Drag and Drop

```python
controller.drag_and_drop(100, 200, 500, 600)
```

## Creating Your Own Examples

1. Import the controller:
   ```python
   from remoteuse.core.actions import DesktopController
   ```

2. Create an instance:
   ```python
   controller = DesktopController()
   ```

3. Use any of the 12 primitives:
   - screenshot()
   - click_at()
   - hover_at()
   - drag_and_drop()
   - scroll_at()
   - mouse_move()
   - type_text()
   - type_text_at()
   - key_press()
   - key_combination()
   - key_hold() / key_release()
   - wait()

## Tips

- Always add `wait()` after actions that trigger UI changes
- Use `type_text_at()` for form fields (it clicks, clears, types, and optionally submits)
- Take screenshots frequently to let the AI "see" the current state
- Use `hover_at()` to reveal tooltips and dropdown menus
- Platform differences: Use "cmd" on macOS, "ctrl" on Windows/Linux
