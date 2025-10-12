"""
Emergency Key Release Utility

Run this script if any keys are stuck after testing or using RemoteUse.
This will attempt to release all common modifier keys.
"""

from pynput.keyboard import Controller, Key
import time

def release_all_modifiers():
    """Release all common modifier keys"""
    keyboard = Controller()
    
    modifier_keys = [
        Key.ctrl,
        Key.shift,
        Key.alt,
        # Key.cmd,  # COMMENTED: Can trigger Windows UI (minimize, etc.)
    ]
    
    print("🔓 Emergency key release started...")
    print("   Releasing all modifier keys...")
    
    for key in modifier_keys:
        try:
            keyboard.release(key)
            time.sleep(0.1)
        except Exception as e:
            pass
    
    print("✅ All modifier keys released!")
    print("   If keys are still stuck, try pressing them manually once.")

if __name__ == "__main__":
    release_all_modifiers()
