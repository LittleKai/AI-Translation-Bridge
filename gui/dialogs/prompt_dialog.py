import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import re


class PromptDialog:
    """Dialog for editing translation prompts"""

    def __init__(self, main_window, processing_tab):
        self.main_window = main_window
        self.processing_tab = processing_tab

        # Check if input file is selected and valid
        translation_settings = main_window.translation_tab.get_settings()
        input_file = translation_settings.get('input_file', '')

        if not input_file:
            messagebox.showwarning("Warning", "Please select an input CSV file first")
            return

        # Get the full path for input file
        input_directory = translation_settings.get('output_directory', '')
        if input_directory and not os.path.isabs(input_file):

            check_path = os.path.join(input_directory, input_file)
            if os.path.exists(check_path):
                full_path = check_path
            else:
                full_path = input_file

            if not full_path:
                full_path = input_file
        else:
            full_path = input_file

        # Detect language from input file path
        self.detected_language = self.detect_language_from_path(full_path)

        if not self.detected_language:
            messagebox.showwarning("Warning",
                                   "Could not detect language from input file path.\n"
                                   "Please ensure the filename contains language code (CN, JP, EN, KR, VI)")
            return

        # Create dialog window
        self.window = tk.Toplevel(main_window.root)
        self.window.title(f"Edit Prompt - {processing_tab.prompt_type.get()}")
        self.window.resizable(True, True)

        # Make dialog modal
        self.window.attributes('-topmost', True)
        self.window.transient(main_window.root)
        self.window.grab_set()

        # Initialize variables
        self.current_prompt = tk.StringVar(value="")
        self.description_text = ""

        # Load current prompt and description for detected language
        self.load_current_prompt()

        # Setup UI
        self.setup_ui()

        # Bind events
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.center_window()

    def detect_language_from_path(self, input_path):
        """Detect language from input file path or name"""
        # Convert to string if needed
        input_path = str(input_path)

        # Try to detect from filename as fallback
        filename = os.path.basename(input_path)

        # Check for language codes in filename (case insensitive)
        for lang in ['JP', 'EN', 'KR', 'CN', 'VI']:
            # Look for language code with word boundaries or separators
            patterns = [
                f'[_-]{lang}[_-]',  # _CN_ or -CN-
                f'^{lang}[_-]',      # CN_ at start
                f'[_-]{lang}$',      # _CN at end
                f'^{lang}$',         # Just CN
                f'[_-]{lang}\\.',    # _CN. before extension
            ]

            for pattern in patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    return lang

        return None

    def load_current_prompt(self):
        """Load current prompt and description from Excel file based on detected language"""
        try:
            prompt_file = "assets/translate_prompt.xlsx"
            if os.path.exists(prompt_file):
                df = pd.read_excel(prompt_file)
                prompt_type = self.processing_tab.prompt_type.get()

                # Check if language column exists
                if self.detected_language not in df.columns:
                    self.main_window.log_message(f"Warning: Language column '{self.detected_language}' not found in prompt file")
                    available_cols = [col for col in df.columns if col not in ['type', 'description']]
                    self.main_window.log_message(f"Available language columns: {', '.join(available_cols)}")
                    return

                # Get prompt for current type and detected language
                if prompt_type and prompt_type in df['type'].values:
                    row = df[df['type'] == prompt_type].iloc[0]

                    # Load prompt text
                    prompt_text = row.get(self.detected_language, '')
                    if pd.notna(prompt_text):
                        self.current_prompt.set(prompt_text)
                        self.main_window.log_message(f"Loaded prompt for {self.detected_language}, type: {prompt_type}")
                    else:
                        self.main_window.log_message(f"Prompt for {self.detected_language}, type: {prompt_type} is empty")

                    # Load description
                    description = row.get('description', '')
                    if pd.notna(description):
                        self.description_text = str(description)
                    else:
                        self.description_text = "No description available"

                elif not prompt_type:
                    if not df.empty:
                        first_row = df.iloc[0]
                        prompt_text = first_row.get(self.detected_language, '')
                        if pd.notna(prompt_text):
                            self.current_prompt.set(prompt_text)
                            self.main_window.log_message(f"Loaded default prompt for {self.detected_language}")

                        description = first_row.get('description', '')
                        if pd.notna(description):
                            self.description_text = str(description)
                        else:
                            self.description_text = "No description available"
                else:
                    self.main_window.log_message(f"Prompt type '{prompt_type}' not found in file")
                    available_types = df['type'].tolist()
                    self.main_window.log_message(f"Available prompt types: {', '.join(available_types)}")
            else:
                self.main_window.log_message(f"Prompt file not found: {prompt_file}")
        except Exception as e:
            self.main_window.log_message(f"Error loading prompt: {e}")

    def setup_ui(self):
        """Setup the user interface"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title with prompt type
        title_text = f"Edit Prompt: {self.processing_tab.prompt_type.get()} - Editing Language: {self.detected_language}"
        title_label = ttk.Label(main_frame, text=title_text, font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Description frame
        desc_frame = ttk.LabelFrame(main_frame, text="Description", padding="10")
        desc_frame.pack(fill=tk.X, pady=(0, 10))

        desc_label = ttk.Label(desc_frame, text=self.description_text,
                               font=("Arial", 9), foreground="blue", wraplength=650)
        desc_label.pack(anchor=tk.W)

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

        # Add reload button to refresh from file
        ttk.Button(button_frame, text="Reload from File", command=self.reload_prompt).pack(side=tk.LEFT)

    def reload_prompt(self):
        """Reload prompt and description from Excel file"""
        self.load_current_prompt()
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.insert(1.0, self.current_prompt.get())

        # Update description label
        for widget in self.window.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Description":
                        for label in child.winfo_children():
                            if isinstance(label, ttk.Label):
                                label.config(text=self.description_text)
                                break
                        break

        self.main_window.log_message("Prompt and description reloaded from file")

    def save_prompt(self):
        """Save the edited prompt"""
        try:
            prompt_file = "assets/translate_prompt.xlsx"
            new_prompt = self.prompt_text.get(1.0, tk.END).strip()

            if os.path.exists(prompt_file):
                df = pd.read_excel(prompt_file)
                prompt_type = self.processing_tab.prompt_type.get()

                # Update prompt in dataframe for the detected language
                if prompt_type in df['type'].values:
                    df.loc[df['type'] == prompt_type, self.detected_language] = new_prompt
                    df.to_excel(prompt_file, index=False)

                    self.main_window.log_message(f"Prompt saved for: {prompt_type}, Language: {self.detected_language}")
                    messagebox.showinfo("Success", f"Prompt saved successfully!\nLanguage: {self.detected_language}\nType: {prompt_type}")
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

        width = 700
        height = 550

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