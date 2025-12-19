
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
import os
import json

from gui.window_manager import WindowManager
from gui.components.status_section import StatusSection
from gui.components.log_section import LogSection
from gui.tabs.translation_tab import TranslationTab
from gui.tabs.processing_tab import ProcessingTab
from gui.dialogs.prompt_dialog import PromptDialog
from key_validator import validate_application_key


class AITranslationBridgeGUI:
    """Main GUI application for AI Translation Bridge"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Translation Bridge")

        # Initialize variables
        self.init_variables()

        # Initialize managers
        self.window_manager = WindowManager(self)

        # Load initial settings
        self.window_manager.load_initial_settings()

        # Setup GUI
        self.setup_gui()

        # Setup events
        self.setup_events()

        # Check key validation
        self.check_key_validation()

        # Compact mode flag
        self.compact_mode = False

    def init_variables(self):
        """Initialize all GUI variables"""
        self.is_running = False
        self.key_valid = False
        self.initial_key_validation_done = False

    def setup_gui(self):
        """Setup the main GUI interface"""
        # Setup window from loaded settings
        self.window_manager.setup_window()

        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create content
        self.create_content(self.main_container)

        # Load tab settings after GUI is created
        self.window_manager.load_tab_settings()

    def create_content(self, parent):
        """Create main content area"""
        # Main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(0, weight=1)

        # Create sections
        self.create_header_section(self.main_frame, row=0)
        self.status_section = StatusSection(self.main_frame, self, row=1)
        self.create_tabbed_section(self.main_frame, row=2)
        self.create_control_section(self.main_frame, row=3)
        self.log_section = LogSection(self.main_frame, self, row=4)


    def create_header_section(self, parent, row):
        """Create header section with title and settings button"""
        self.header_frame = ttk.Frame(parent)
        self.header_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.header_frame.columnconfigure(0, weight=1)

        # Title
        self.title_label = ttk.Label(self.header_frame, text="AI Translation Bridge",
                                     font=("Arial", 14, "bold"))
        self.title_label.pack(side=tk.LEFT)

        # Settings button
        self.settings_button = ttk.Button(self.header_frame, text="⚙ Settings",
                                          command=self.open_settings)
        self.settings_button.pack(side=tk.RIGHT)

    def create_tabbed_section(self, parent, row):
        """Create tabbed section"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Translation tab
        translation_frame = ttk.Frame(self.notebook)
        self.notebook.add(translation_frame, text="Translation")
        self.translation_tab = TranslationTab(translation_frame, self)

        # Processing tab
        processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(processing_frame, text="Processing")
        self.processing_tab = ProcessingTab(processing_frame, self)

    def create_control_section(self, parent, row):
        """Create bot control buttons section"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        # Start button
        self.start_button = ttk.Button(
            control_frame,
            text="Start (F1)",
            # command=self.start_bot
        )
        self.start_button.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E), ipady=5)

        # Stop button
        self.stop_button = ttk.Button(
            control_frame,
            text="Stop (F3)",
            # command=self.stop_bot,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E), ipady=5)


    def setup_events(self):
        """Setup event handlers"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        try:
            import keyboard
            keyboard.add_hotkey('f1', self.toggle_compact_mode)
        except Exception as e:
            self.log_message(f"Warning: Could not setup keyboard shortcuts: {e}")

    def toggle_compact_mode(self):
        """Toggle compact mode (F1 key)"""
        self.compact_mode = not self.compact_mode

        if self.compact_mode:
            # Hide header and tabs
            self.header_frame.grid_forget()
            self.notebook.grid_forget()

            # Keep window on top
            self.root.attributes('-topmost', True)

            # Resize window to compact size
            self.root.geometry("600x400")
        else:
            # Show header and tabs
            self.header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
            self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

            # Remove always on top
            self.root.attributes('-topmost', False)

            # Restore window size
            self.window_manager.setup_window()

    def check_key_validation(self):
        """Check key validation status"""
        def check_in_background():
            try:
                is_valid, message = validate_application_key()
                self.key_valid = is_valid
                self.initial_key_validation_done = True
                self.root.after(0, self.status_section.update_key_status, is_valid, message)
            except Exception as e:
                self.initial_key_validation_done = True
                self.root.after(0, self.status_section.update_key_status, False, f"Validation error: {e}")

        threading.Thread(target=check_in_background, daemon=True).start()

    def open_settings(self):
        """Open settings window"""
        messagebox.showinfo("Settings", "Settings dialog will be implemented")

    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.root.after(0, self.log_section.add_message, formatted_message)

    def save_settings(self):
        """Save all settings to file"""
        self.window_manager.save_settings()

    def load_settings(self):
        """Load settings from file"""
        self.window_manager.load_settings()

    def on_closing(self):
        """Handle window close event"""
        self.save_settings()

        try:
            import keyboard
            keyboard.unhook_all()
        except:
            pass

        self.root.destroy()

    def get_current_settings(self):
        """Get current settings from all tabs"""
        return {
            'translation': self.translation_tab.get_settings(),
            'processing': self.processing_tab.get_settings()
        }

    def run(self):
        """Start the GUI application"""
        self.log_message("AI Translation Bridge initialized.")
        self.log_message("Press F1 to toggle compact mode.")
        self.root.mainloop()