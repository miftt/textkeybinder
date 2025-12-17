"""
Text Macro Keybinder - Main Entry Point
A modern keybind manager for text macros with glassmorphism UI.
"""
from utils.single_instance import check_and_exit_if_running
from core.keybind_manager import ModernKeybindManager

if __name__ == "__main__":
    # Check for single instance
    check_and_exit_if_running()
    
    # Start application
    app = ModernKeybindManager()
    app.run()
