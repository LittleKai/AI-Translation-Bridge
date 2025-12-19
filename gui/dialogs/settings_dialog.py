import tkinter as tk
from tkinter import ttk, messagebox


class SettingsDialog:
    """Settings dialog window"""

    def __init__(self, main_window):
        self.main_window = main_window

        # Create dialog window
        self.window = tk.Toplevel(main_window.root)
        self.window.title("Settings")
        self.window.resizable(False, False)

        # Make dialog modal
        self.window.attributes('-topmost', True)
        self.window.transient(main_window.root)
        self.window.grab_set()

        # Setup UI
        self.setup_ui()

        # Center window
        self.center_window()

        # Bind events
        self.window.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def setup_ui(self):
        """Setup the user interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Application Key section
        key_frame = ttk.LabelFrame(main_frame, text="Application Key", padding="10")
        key_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(key_frame, text="Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.key_entry = ttk.Entry(key_frame, textvariable=self.main_window.app_key_var, width=30)
        self.key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(key_frame, text="Enter your application key",
                  font=("Arial", 9), foreground="gray").grid(row=1, column=1, sticky=tk.W, pady=(5, 0))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side=tk.RIGHT)

    def on_save(self):
        """Save settings and close"""
        # Save settings
        self.main_window.save_settings()

        # Re-validate key
        self.main_window.check_key_validation()

        messagebox.showinfo("Success", "Settings saved successfully!")
        self.window.destroy()

    def on_cancel(self):
        """Close without saving"""
        self.window.destroy()

    def center_window(self):
        """Center the window on parent"""
        self.window.update_idletasks()

        width = 400
        height = 200

        parent_x = self.main_window.root.winfo_x()
        parent_y = self.main_window.root.winfo_y()
        parent_width = self.main_window.root.winfo_width()
        parent_height = self.main_window.root.winfo_height()

        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)

        self.window.geometry(f"{width}x{height}+{x}+{y}")