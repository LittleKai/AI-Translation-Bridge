import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os


class PromptDialog:
    """Dialog for editing translation prompts"""

    def __init__(self, main_window, processing_tab):
        self.main_window = main_window
        self.processing_tab = processing_tab

        # Create dialog window
        self.window = tk.Toplevel(main_window.root)
        self.window.title("Edit Prompt")
        self.window.resizable(True, True)

        # Make dialog modal
        self.window.attributes('-topmost', True)
        self.window.transient(main_window.root)
        self.window.grab_set()

        # Initialize variables
        self.current_prompt = tk.StringVar(value="")

        # Load current prompt
        self.load_current_prompt()

        # Setup UI
        self.setup_ui()

        # Bind events
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.center_window()

    def load_current_prompt(self):
        """Load current prompt from Excel file"""
        try:
            prompt_file = "assets/translate_prompt.xlsx"
            if os.path.exists(prompt_file):
                df = pd.read_excel(prompt_file)
                prompt_type = self.processing_tab.prompt_type.get()

                # Get prompt for current type (example using English column)
                if prompt_type in df['type'].values:
                    row = df[df['type'] == prompt_type].iloc[0]
                    self.current_prompt.set(row.get('EN', ''))
        except Exception as e:
            self.main_window.log_message(f"Error loading prompt: {e}")

    def setup_ui(self):
        """Setup the user interface"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text=f"Edit Prompt: {self.processing_tab.prompt_type.get()}",
                                font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Prompt text area
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.prompt_text = tk.Text(text_frame, width=60, height=20, wrap=tk.WORD)
        self.prompt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, command=self.prompt_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.prompt_text.configure(yscrollcommand=scrollbar.set)

        # Insert current prompt
        self.prompt_text.insert(1.0, self.current_prompt.get())

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Cancel", command=self.on_closing).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Save", command=self.save_prompt).pack(side=tk.RIGHT)

    def save_prompt(self):
        """Save the edited prompt"""
        try:
            prompt_file = "assets/translate_prompt.xlsx"
            new_prompt = self.prompt_text.get(1.0, tk.END).strip()

            if os.path.exists(prompt_file):
                df = pd.read_excel(prompt_file)
                prompt_type = self.processing_tab.prompt_type.get()

                # Update prompt in dataframe
                if prompt_type in df['type'].values:
                    df.loc[df['type'] == prompt_type, 'EN'] = new_prompt
                    df.to_excel(prompt_file, index=False)

                    self.main_window.log_message(f"Prompt saved for: {prompt_type}")
                    messagebox.showinfo("Success", "Prompt saved successfully!")
                    self.window.destroy()
                else:
                    messagebox.showerror("Error", f"Prompt type '{prompt_type}' not found")
            else:
                messagebox.showerror("Error", "Prompt file not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save prompt: {e}")

    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()

        width = 600
        height = 500

        parent_x = self.main_window.root.winfo_x()
        parent_y = self.main_window.root.winfo_y()
        parent_width = self.main_window.root.winfo_width()
        parent_height = self.main_window.root.winfo_height()

        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)

        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def on_closing(self):
        """Handle window closing"""
        self.window.destroy()
