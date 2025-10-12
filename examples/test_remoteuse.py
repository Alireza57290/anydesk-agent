import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from remoteuse.core.actions import DesktopController


def ai_agent_workflow_example():
    controller = DesktopController()
    
    print("1. Taking screenshot...")
    screen = controller.screenshot()
    if screen.success:
        print(f"   Screen size: {screen.data['width']}x{screen.data['height']}")
    
    print("\n2. Clicking Start button...")
    result = controller.click_at(20, 1060)
    print(f"   {result.message}")
    
    controller.wait(500)
    
    print("\n3. Searching for Notepad...")
    result = controller.type_text("notepad")
    print(f"   {result.message}")
    
    controller.wait(500)
    
    result = controller.key_press("enter")
    print(f"   {result.message}")
    
    controller.wait(2000)
    
    print("\n4. Typing in Notepad...")
    result = controller.type_text("Hello from AI agent!", delay_ms=50)
    print(f"   {result.message}")
    
    controller.key_press("enter")
    controller.type_text("RemoteUse is working!")
    
    print("\n5. Saving file...")
    result = controller.key_combination("ctrl+s")
    print(f"   {result.message}")
    
    controller.wait(1000)
    
    result = controller.type_text_at(500, 400, "ai_message.txt", clear=True, submit=True)
    print(f"   {result.message}")
    
    print("\n✅ AI agent successfully automated Notepad!")


def form_filling_example():
    controller = DesktopController()
    
    print("Taking screenshot...")
    controller.screenshot()
    
    print("\nFilling form fields...")
    controller.type_text_at(400, 300, "john@example.com", submit=False)
    controller.type_text_at(400, 400, "John Smith", submit=False)
    controller.type_text_at(400, 500, "Hello AI world", submit=True)
    
    print("✅ Form filled!")


def multi_select_files_example():
    controller = DesktopController()
    
    print("Taking screenshot...")
    controller.screenshot()
    
    print("\nHolding Ctrl for multi-select...")
    controller.key_hold("ctrl")
    
    print("Clicking multiple files...")
    controller.click_at(100, 200)
    controller.click_at(100, 300)
    controller.click_at(100, 400)
    
    print("Releasing Ctrl...")
    controller.key_release("ctrl")
    
    print("Dragging to trash...")
    controller.drag_and_drop(100, 200, 800, 600)
    
    print("✅ Files moved to trash!")


def scroll_example():
    controller = DesktopController()
    
    print("Scrolling down in a window...")
    result = controller.scroll_at(500, 500, direction="down", amount=5)
    print(f"   {result.message}")
    
    controller.wait(1000)
    
    print("Scrolling up...")
    result = controller.scroll_at(500, 500, direction="up", amount=5)
    print(f"   {result.message}")
    
    print("✅ Scroll test complete!")


if __name__ == "__main__":
    print("=" * 60)
    print("RemoteUse Examples")
    print("=" * 60)
    
    print("\nAvailable examples:")
    print("1. AI Agent Workflow (Notepad)")
    print("2. Form Filling")
    print("3. Multi-select Files")
    print("4. Scroll Test")
    
    choice = input("\nSelect example (1-4): ")
    
    if choice == "1":
        ai_agent_workflow_example()
    elif choice == "2":
        form_filling_example()
    elif choice == "3":
        multi_select_files_example()
    elif choice == "4":
        scroll_example()
    else:
        print("Invalid choice!")
