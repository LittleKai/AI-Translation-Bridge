import tkinter as tk
from tkinter import ttk


class StatusSection:
    """Status monitoring section component"""

    def __init__(self, parent, main_window, row=0):
        self.parent = parent
        self.main_window = main_window
        self.row = row

        self.create_section()

    def create_section(self):
        """Create the status section"""
        self.frame = ttk.LabelFrame(self.parent, text="Status", padding="10")
        self.frame.grid(row=self.row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # Bot Status
        ttk.Label(self.frame, text="Bot Status:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=3)
        self.status_label = ttk.Label(self.frame, text="Stopped", foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=3)

        # Key Status
        ttk.Label(self.frame, text="Key Status:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=3)
        self.key_status_label = ttk.Label(self.frame, text="Checking...", foreground="orange")
        self.key_status_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=3)

    def set_bot_status(self, status, color):
        """Update bot status display"""
        self.status_label.config(text=status, foreground=color)

    def update_key_status(self, is_valid, message):
        """Update key validation status display"""
        if is_valid:
            self.key_status_label.config(text="Valid ✓", foreground="green")
        else:
            self.key_status_label.config(text="Invalid ✗", foreground="red")
