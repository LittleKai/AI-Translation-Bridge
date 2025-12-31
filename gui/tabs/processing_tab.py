import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import webbrowser
from helper.prompt_helper import PromptHelper
import pyperclip

class ProcessingTab:
    """Processing settings tab"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window

        # Initialize variables
        self.init_variables()

        # Load prompt types
        self.load_prompt_types()

        # Create tab content
        self.create_content()

        # Bind variable changes
        self.bind_variable_changes()

    def init_variables(self):
        """Initialize tab variables"""
        self.batch_size = tk.StringVar(value="10")
        self.prompt_type = tk.StringVar(value="")
        self.ai_service = tk.StringVar(value="Gemini")
        self.ai_model = tk.StringVar(value="")
        self.prompt_types = []

        self.mode_var = tk.StringVar(value="automatic")
        self.current_prompt_text = ""
        self.manual_batch_data = pd.DataFrame()  # Initialize as empty DataFrame instead of None
        self.manual_batch_ids = []
        # API configuration
        self.api_configs = {
            'Gemini API': {
                'models': ['gemini-2.0-flash', 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-2.5-pro',
                           'gemini-2.5-pro', 'gemini-3-flash-preview', 'gemini-3-pro-preview'],
                'default_model': 'gemini-2.5-flash-lite',
                'keys': [],
                'max_tokens': 8192,
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'help_url': 'https://ai.google.dev/models/gemini'
            },
            'ChatGPT API': {
                'models': ['gpt-4o-mini', 'gpt-4o', 'gpt-4.1', 'gpt-5-nano', 'gpt-5-mini', 'gpt-5', 'gpt-5.1',
                           'gpt-5.2'],
                'default_model': 'gpt-4o-mini',
                'keys': [],
                'max_tokens': 4096,
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'help_url': 'https://platform.openai.com/docs/models'
            },
            'Claude API': {
                'models': ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229',
                           'claude-haiku-4-5-20251001','claude-sonnet-4-5-20250929','anthropic.claude-opus-4-5-20251101-v1:0'],
                'default_model': 'claude-3-5-sonnet-20241022',
                'keys': [],
                'max_tokens': 4096,
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'help_url': 'https://platform.claude.com/docs/en/about-claude/models/overview'
            },
            'Grok API': {
                'models': ['grok-3-mini', 'grok-4-fast-non-reasoning', 'grok-4-fast-reasoning','grok-4-1-fast-non-reasoning', 'grok-4-1-fast-reasoning'],
                'default_model': 'grok-3-mini',
                'keys': [],
                'max_tokens': 4096,
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'help_url': 'https://docs.x.ai/docs/models'
            }
        }

    def load_prompt_types(self, keep_empty_type=None):
        """Load prompt types from Excel file and filter by available translations for detected language
        
        Args:
            keep_empty_type: Prompt type name to keep in list even if empty (newly added type)
        """
        try:
            prompt_file = "assets/translate_prompt.xlsx"
            if os.path.exists(prompt_file):
                df = pd.read_excel(prompt_file)
                if 'type' in df.columns:
                    # Get all prompt types
                    all_types = df['type'].unique().tolist()
    
                    # Detect language from input file
                    translation_settings = self.main_window.translation_tab.get_settings() if hasattr(self.main_window, 'translation_tab') else {}
                    input_file = translation_settings.get('input_file', '')
    
                    if input_file and os.path.exists(input_file):
                        from helper.prompt_helper import PromptHelper
                        detected_lang = PromptHelper.detect_language(input_file)
    
                        if detected_lang and detected_lang in df.columns:
                            # Filter prompt types that have non-empty values for this language
                            self.prompt_types = []
                            for ptype in all_types:
                                row = df[df['type'] == ptype]
                                if not row.empty:
                                    prompt_value = row.iloc[0].get(detected_lang, '')
                                    # Include if has content OR if it's the newly added type
                                    if (pd.notna(prompt_value) and str(prompt_value).strip()) or ptype == keep_empty_type:
                                        self.prompt_types.append(ptype)
    
                            self.main_window.log_message(f"Filtered prompt types for {detected_lang}: {len(self.prompt_types)} available")
                        else:
                            self.prompt_types = all_types
                    else:
                        self.prompt_types = all_types
    
                    if self.prompt_types:
                        # Set first available type or keep current if still valid
                        current = self.prompt_type.get()
                        if current not in self.prompt_types:
                            self.prompt_type.set(self.prompt_types[0])
                    else:
                        self.prompt_types = ["Default"]
                        self.prompt_type.set("Default")
        except Exception as e:
            self.main_window.log_message(f"Warning: Could not load prompt types: {e}")
            self.prompt_types = ["Default"]
            self.prompt_type.set("Default")

    def bind_variable_changes(self):
        """Bind variable changes to auto-save"""
        variables = [
            self.batch_size,
            self.prompt_type,
            self.ai_service,
            self.ai_model
        ]

        for var in variables:
            var.trace('w', lambda *args: self.main_window.save_settings())

        # Special handler for AI service change
        self.ai_service.trace('w', self.on_ai_service_change)

        # Update progress and output filename when prompt type changes
        self.prompt_type.trace('w', lambda *args: [
            self.main_window.update_progress_display(),
            self.main_window.translation_tab.update_output_filename() if hasattr(self.main_window, 'translation_tab') else None
        ])

        # Reload prompt types when input file changes (via translation tab)
        if hasattr(self.main_window, 'translation_tab'):
            self.main_window.translation_tab.input_file.trace('w', lambda *args: [
                self.load_prompt_types(),
                self.prompt_dropdown.configure(values=self.prompt_types) if hasattr(self, 'prompt_dropdown') else None
            ])
    def create_content(self):
        """Create tab content"""
        content_frame = ttk.Frame(self.parent, padding="15")
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(1, weight=1)

        # Batch size section
        self.create_batch_section(content_frame, row=0)

        # Prompt section
        self.create_prompt_section(content_frame, row=1)

        # AI service section
        self.create_ai_service_section(content_frame, row=2)

    def create_batch_section(self, parent, row):
        """Create batch size section"""
        batch_frame = ttk.LabelFrame(parent, text="Batch Processing", padding="10")
        batch_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        batch_frame.columnconfigure(1, weight=1)

        ttk.Label(batch_frame, text="Batch Size:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        batch_entry = ttk.Entry(batch_frame, textvariable=self.batch_size, width=10)
        batch_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(batch_frame, text="(Number of csv lines to process at once)",
                  font=("Arial", 9), foreground="gray").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))

    def create_prompt_section(self, parent, row):
        """Create prompt selection section with add button"""
        prompt_frame = ttk.LabelFrame(parent, text="Prompt Configuration", padding="10")
        prompt_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        prompt_frame.columnconfigure(3, weight=1)

        # Edit Prompt button
        ttk.Button(prompt_frame, text="Edit Prompt",
                   command=self.open_prompt_dialog).grid(row=0, column=0, padx=(0, 10))

        # Prompt Type label
        ttk.Label(prompt_frame, text="Prompt Type:").grid(row=0, column=1, sticky=tk.W, padx=(0, 5))

        # Prompt Type dropdown
        self.prompt_dropdown = ttk.Combobox(
            prompt_frame,
            textvariable=self.prompt_type,
            values=self.prompt_types,
            state="readonly",
            width=20
        )
        self.prompt_dropdown.grid(row=0, column=2, sticky=tk.W)

        # Add Prompt Type button with + icon
        ttk.Button(prompt_frame, text="➕ Add",
                   command=self.add_new_prompt_type, width=8).grid(row=0, column=3, padx=(5, 0), sticky=tk.W)


    def add_new_prompt_type(self):
        """Add a new prompt type to the Excel file"""
        try:
            # Create dialog to input new prompt type name
            dialog = tk.Toplevel(self.main_window.root)
            dialog.title("Add New Prompt Type")
            dialog.resizable(False, False)
            dialog.transient(self.main_window.root)
            dialog.grab_set()

            frame = ttk.Frame(dialog, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(frame, text="Enter new prompt type name:", font=("Arial", 10)).pack(pady=(0, 10))

            name_var = tk.StringVar()
            name_entry = ttk.Entry(frame, textvariable=name_var, width=30)
            name_entry.pack(pady=(0, 10))
            name_entry.focus()

            ttk.Label(frame, text="Description (optional):", font=("Arial", 10)).pack(pady=(0, 5))

            desc_var = tk.StringVar()
            desc_entry = ttk.Entry(frame, textvariable=desc_var, width=30)
            desc_entry.pack(pady=(0, 15))

            def save_new_type():
                new_type_name = name_var.get().strip()
                description = desc_var.get().strip()

                if not new_type_name:
                    messagebox.showwarning("Warning", "Please enter a prompt type name")
                    return

                prompt_file = "assets/translate_prompt.xlsx"
                if not os.path.exists(prompt_file):
                    messagebox.showerror("Error", "Prompt file not found")
                    dialog.destroy()
                    return

                try:
                    df = pd.read_excel(prompt_file)

                    # Check if type already exists
                    if 'type' in df.columns and new_type_name in df['type'].values:
                        messagebox.showwarning("Warning", f"Prompt type '{new_type_name}' already exists")
                        return

                    # Create new row with empty values for all language columns
                    new_row = {'type': new_type_name, 'description': description}

                    # Add empty values for all language columns
                    for col in df.columns:
                        if col not in ['type', 'description']:
                            new_row[col] = ''

                    # Append new row
                    new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    new_df.to_excel(prompt_file, index=False)

                    self.main_window.log_message(f"Added new prompt type: {new_type_name}")

                    # Reload prompt types with the new type kept even if empty
                    self.load_prompt_types(keep_empty_type=new_type_name)

                    # Update dropdown with new values
                    if hasattr(self, 'prompt_dropdown'):
                        self.prompt_dropdown['values'] = self.prompt_types
                        self.prompt_dropdown.update()

                    # Set the new type as selected
                    self.prompt_type.set(new_type_name)

                    # Save settings to persist the change
                    self.main_window.save_settings()

                    messagebox.showinfo("Success", f"Prompt type '{new_type_name}' added successfully!\n\nYou can now edit the prompts for each language.")
                    dialog.destroy()

                    # Open prompt dialog automatically to edit
                    self.open_prompt_dialog()

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add prompt type: {str(e)}")
                    self.main_window.log_message(f"Error adding prompt type: {str(e)}")

            btn_frame = ttk.Frame(frame)
            btn_frame.pack()

            ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(btn_frame, text="Add", command=save_new_type).pack(side=tk.LEFT)

            # Bind Enter key to save
            dialog.bind('<Return>', lambda e: save_new_type())

            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open add dialog: {str(e)}")

    def create_ai_service_section(self, parent, row):
        """Create AI service selection section with manual/automatic mode"""
        ai_frame = ttk.LabelFrame(parent, text="AI Service", padding="10")
        ai_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ai_frame.columnconfigure(1, weight=1)

        # Mode selection row
        mode_frame = ttk.Frame(ai_frame)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(mode_frame, text="Automatic",
                        variable=self.mode_var, value="automatic",
                        command=self.on_mode_change).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(mode_frame, text="Manual",
                        variable=self.mode_var, value="manual",
                        command=self.on_mode_change).pack(side=tk.LEFT)

        # Automatic mode frame
        self.auto_frame = ttk.Frame(ai_frame)
        self.auto_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.auto_frame.columnconfigure(1, weight=1)

        # Service selection
        ttk.Label(self.auto_frame, text="Select Service:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        services = ["Gemini", "ChatGPT", "Claude", "Perplexity", "Grok", "Gemini API", "ChatGPT API", "Claude API", "Grok API"]
        self.ai_dropdown = ttk.Combobox(
            self.auto_frame,
            textvariable=self.ai_service,
            values=services,
            state="readonly",
            width=15
        )
        self.ai_dropdown.grid(row=0, column=1, sticky=tk.W)

        # Model configuration row
        self.model_frame = ttk.Frame(self.auto_frame)
        self.model_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.model_frame.columnconfigure(1, weight=1)

        ttk.Label(self.model_frame, text="Model Code:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.model_entry = ttk.Entry(self.model_frame, textvariable=self.ai_model, width=25)
        self.model_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))

        self.settings_button = ttk.Button(self.model_frame, text="⚙ Settings",
                                          command=self.open_api_settings)
        self.settings_button.grid(row=0, column=2, padx=(5, 5))

        self.help_button = ttk.Button(self.model_frame, text="?", width=3,
                                      command=self.open_api_help)
        self.help_button.grid(row=0, column=3)

        # Manual mode frame
        self.manual_frame = ttk.Frame(ai_frame)
        self.manual_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.manual_frame.columnconfigure(0, weight=1)
        self.manual_frame.columnconfigure(1, weight=1)
        self.manual_frame.columnconfigure(2, weight=1)

        # Manual mode buttons
        self.copy_prompt_btn = ttk.Button(self.manual_frame, text="Copy Prompt",
                                          command=self.copy_prompt_manual)
        self.copy_prompt_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))

        self.paste_response_btn = ttk.Button(self.manual_frame, text="Paste Response",
                                             command=self.paste_response_manual,
                                             state="disabled")
        self.paste_response_btn.grid(row=0, column=1, padx=(0, 5), sticky=(tk.W, tk.E))

        self.cancel_btn = ttk.Button(self.manual_frame, text="Cancel",
                                     command=self.cancel_manual,
                                     state="disabled")
        self.cancel_btn.grid(row=0, column=2, sticky=(tk.W, tk.E))

        # Manual mode status label
        self.manual_status_label = ttk.Label(self.manual_frame, text="", foreground="blue")
        self.manual_status_label.grid(row=1, column=0, columnspan=3, pady=(5, 0))

        # Initially hide manual frame and setup based on current mode
        self.on_mode_change()

        # Check initial service selection
        self.on_ai_service_change()

    def on_ai_service_change(self, *args):
        """Handle AI service selection change"""
        service = self.ai_service.get()

        # Show/hide model configuration based on service type
        if "API" in service:
            self.model_frame.grid()

            # Load saved model or use default
            if service in self.api_configs:
                # Check if we have a saved model for this service
                saved_model = self.api_configs[service].get('saved_model', '')
                if saved_model:
                    self.ai_model.set(saved_model)
                else:
                    # Use default model
                    default_model = self.api_configs[service]['default_model']
                    self.ai_model.set(default_model)
        else:
            self.model_frame.grid_remove()
            self.ai_model.set("")  # Clear model name for non-API services

    def open_api_settings(self):
        """Open API settings dialog"""
        service = self.ai_service.get()
        if service in self.api_configs:
            from gui.dialogs.api_settings_dialog import APISettingsDialog
            APISettingsDialog(self.main_window, self, service)
        else:
            messagebox.showinfo("Info", "Please select an API service first")

    def open_api_help(self):
        """Open API documentation in browser"""
        service = self.ai_service.get()
        if service in self.api_configs:
            url = self.api_configs[service]['help_url']
            webbrowser.open(url)
        else:
            messagebox.showinfo("Info", "Please select an API service first")

    def open_prompt_dialog(self):
        """Open prompt editing dialog"""
        from gui.dialogs.prompt_dialog import PromptDialog
        PromptDialog(self.main_window, self)

    def get_settings(self):
        """Get current tab settings"""
        settings = {
            'batch_size': self.batch_size.get(),
            'prompt_type': self.prompt_type.get(),
            'ai_service': self.ai_service.get(),
            'ai_model': self.ai_model.get(),
            'mode': self.mode_var.get()
        }

        # Add API configurations and save current model
        settings['api_configs'] = {}
        for service, config in self.api_configs.items():
            settings['api_configs'][service] = {
                'keys': config['keys'],
                'max_tokens': config['max_tokens'],
                'temperature': config['temperature'],
                'top_p': config['top_p'],
                'top_k': config['top_k'],
                'saved_model': self.ai_model.get() if service == self.ai_service.get() else config.get('saved_model', '')
            }

        return settings

    def load_settings(self, settings):
        """Load settings into tab"""
        try:
            if 'batch_size' in settings:
                self.batch_size.set(settings['batch_size'])
            if 'prompt_type' in settings:
                self.prompt_type.set(settings['prompt_type'])
            if 'ai_service' in settings:
                self.ai_service.set(settings['ai_service'])
            if 'ai_model' in settings:
                self.ai_model.set(settings['ai_model'])
            if 'mode' in settings:
                self.mode_var.set(settings['mode'])
                self.on_mode_change()
            # Load API configurations with saved models
            if 'api_configs' in settings:
                for service, config in settings['api_configs'].items():
                    if service in self.api_configs:
                        self.api_configs[service].update(config)
                        # Store saved model
                        if 'saved_model' in config:
                            self.api_configs[service]['saved_model'] = config['saved_model']

            # Trigger service change handler to show/hide model config
            self.on_ai_service_change()
        except Exception as e:
            print(f"Warning: Could not load processing tab settings: {e}")

    def on_mode_change(self):
        """Handle mode change between automatic and manual"""
        if self.mode_var.get() == "automatic":
            self.auto_frame.grid()
            self.manual_frame.grid_remove()
            self.manual_status_label.config(text="")
            # Reset manual mode state
            self.current_prompt_text = ""
            self.manual_batch_data = None
            self.manual_batch_ids = []
        else:  # manual
            self.auto_frame.grid_remove()
            self.manual_frame.grid()
            # Hide model frame if it was shown
            self.model_frame.grid_remove()

    def copy_prompt_manual(self):
        """Copy prompt to clipboard for manual processing"""
        try:
            # Reset previous batch data
            self.manual_batch_data = None
            self.manual_batch_ids = []

            # Get settings
            translation_settings = self.main_window.translation_tab.get_settings()
            input_file = translation_settings.get('input_file')

            if not input_file or not os.path.exists(input_file):
                messagebox.showwarning("Warning", "Please select a valid input file first")
                return

            # Import PromptHelper
            from helper.prompt_helper import PromptHelper

            # Load prompt using helper
            prompt_type = self.prompt_type.get()
            if not prompt_type:
                messagebox.showwarning("Warning", "Please select a prompt type first")
                return

            prompt_template = PromptHelper.load_translation_prompt(
                input_file,
                prompt_type,
                self.main_window.log_message
            )

            if not prompt_template:
                messagebox.showwarning("Warning", "Failed to load translation prompt")
                return

            # Read input file with proper encoding handling
            try:
                # Check file extension
                _, ext = os.path.splitext(input_file)
                ext = ext.lower()

                if ext in ['.xlsx', '.xls']:
                    # Read Excel file with openpyxl engine
                    df = pd.read_excel(input_file, engine='openpyxl')
                    self.main_window.log_message(f"Loaded {len(df)} rows from Excel file")
                else:
                    # Read CSV with UTF-8 encoding
                    df = pd.read_csv(input_file, encoding='utf-8')
                    self.main_window.log_message(f"Loaded {len(df)} rows from CSV file")

            except UnicodeDecodeError as e:
                messagebox.showerror("Error", f"Encoding error reading file: {str(e)}\nPlease ensure file is saved with UTF-8 encoding")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read input file: {str(e)}")
                return

            # Check required columns
            if 'id' not in df.columns or 'text' not in df.columns:
                messagebox.showerror("Error", "Input file must have 'id' and 'text' columns")
                return

            # Apply filters
            df = PromptHelper.apply_id_filters(
                df,
                translation_settings.get('start_id', ''),
                translation_settings.get('stop_id', '')
            )

            if df.empty:
                messagebox.showinfo("Info", "No data found after applying filters")
                return

            # Get batch size
            try:
                batch_size = int(self.batch_size.get())
                if batch_size <= 0:
                    raise ValueError("Batch size must be positive")
            except ValueError as e:
                messagebox.showwarning("Warning", f"Invalid batch size: {e}")
                return

            # Find next batch to process using helper
            output_path = PromptHelper.generate_output_path(input_file, prompt_type)
            next_batch_df = PromptHelper.find_next_batch(df, output_path, batch_size)

            if next_batch_df is None or next_batch_df.empty:
                messagebox.showinfo("Info", "No more batches to process")
                return

            # Create batch text using helper
            batch_text = PromptHelper.create_batch_text(next_batch_df)

            # Format prompt
            count_info = f"Source text consists of {len(next_batch_df)} numbered lines from 1 to {len(next_batch_df)}."
            full_prompt = prompt_template.format(count_info=count_info, text=batch_text)

            # Copy to clipboard
            pyperclip.copy(full_prompt)

            # Store batch data for later processing
            self.current_prompt_text = full_prompt
            self.manual_batch_data = next_batch_df.copy()
            self.manual_batch_ids = next_batch_df['id'].tolist()

            # Verify data was stored
            self.main_window.log_message(f"Batch data stored: {len(self.manual_batch_data)} rows")

            # Update UI
            self.copy_prompt_btn.config(state="disabled")
            self.paste_response_btn.config(state="normal")
            self.cancel_btn.config(state="normal")

            batch_id_range = f"{min(self.manual_batch_ids)}-{max(self.manual_batch_ids)}"
            self.manual_status_label.config(
                text=f"Prompt copied! Processing batch: IDs {batch_id_range} ({len(next_batch_df)} rows)",
                foreground="green"
            )

            self.main_window.log_message(f"Manual mode: Copied prompt for batch IDs {batch_id_range}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy prompt: {str(e)}")
            self.main_window.log_message(f"Error in copy_prompt_manual: {str(e)}")
            import traceback
            self.main_window.log_message(traceback.format_exc())
            self.reset_manual_mode()

    def paste_response_manual(self):
        """Process pasted response from clipboard"""
        try:
            # Validate that we have batch data
            if self.manual_batch_data is None or self.manual_batch_data.empty:
                messagebox.showwarning("Warning", "No batch data available. Please copy prompt first.")
                return

            # Get response from clipboard
            response_text = pyperclip.paste()

            if not response_text or not response_text.strip():
                messagebox.showwarning("Warning", "Clipboard is empty or contains no text")
                return

            # Get batch size safely
            batch_size = len(self.manual_batch_data) if self.manual_batch_data is not None else 0

            if batch_size == 0:
                messagebox.showwarning("Warning", "Invalid batch data")
                return

            # Parse response
            from helper.translation_processor import TranslationProcessor
            translations = TranslationProcessor.parse_numbered_text(
                response_text,
                batch_size
            )

            # Check if we got valid translations
            if not translations:
                messagebox.showwarning("Warning", "Failed to parse response. Please check the format.")
                return

            # Process and save results
            translation_settings = self.main_window.translation_tab.get_settings()
            input_file = translation_settings.get('input_file')

            if not input_file:
                messagebox.showwarning("Warning", "Input file not found")
                return

            # Import PromptHelper here if not already imported at top
            from helper.prompt_helper import PromptHelper

            output_path = PromptHelper.generate_output_path(input_file, self.prompt_type.get())

            # Load existing results using helper
            existing_results, _, _ = PromptHelper.load_existing_results(output_path)

            # Update with new translations
            successful_count = 0
            for (_, row), translation in zip(self.manual_batch_data.iterrows(), translations):
                existing_results[row['id']] = {
                    'id': row['id'],
                    'raw': row['text'],
                    'edit': translation if translation else '',
                    'status': '' if translation else 'failed'
                }
                if translation:
                    successful_count += 1

            # Save results using helper
            PromptHelper.save_results(existing_results, output_path)

            # Log and update UI
            self.main_window.log_message(
                f"Manual batch processed: {successful_count}/{batch_size} successful"
            )
            self.main_window.log_message(f"Results saved to: {output_path}")

            # Reset UI
            self.reset_manual_mode()

            # Update progress display
            self.main_window.update_progress_display()

            messagebox.showinfo("Success",
                                f"Batch processed successfully!\n"
                                f"Successful: {successful_count}/{batch_size}")

        except AttributeError as e:
            messagebox.showerror("Error", f"Data error: {str(e)}\nPlease copy prompt first.")
            self.main_window.log_message(f"AttributeError in paste_response_manual: {str(e)}")
            self.reset_manual_mode()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process response: {str(e)}")
            self.main_window.log_message(f"Error in paste_response_manual: {str(e)}")
            import traceback
            self.main_window.log_message(traceback.format_exc())
    def cancel_manual(self):
        """Cancel current manual batch processing"""
        self.reset_manual_mode()
        self.manual_status_label.config(text="Batch cancelled", foreground="red")
        self.main_window.log_message("Manual batch processing cancelled")

    def reset_manual_mode(self):
        """Reset manual mode UI and state"""
        self.copy_prompt_btn.config(state="normal")
        self.paste_response_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")
        self.current_prompt_text = ""
        # Don't set to None immediately, just clear the dataframe
        if self.manual_batch_data is not None and not isinstance(self.manual_batch_data, pd.DataFrame):
            self.manual_batch_data = None
        elif isinstance(self.manual_batch_data, pd.DataFrame):
            self.manual_batch_data = pd.DataFrame()  # Empty dataframe instead of None
        self.manual_batch_ids = []
        self.manual_status_label.config(text="")