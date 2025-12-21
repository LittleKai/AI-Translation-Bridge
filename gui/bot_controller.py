import threading
import pandas as pd
import os
import time
from helper.web_bot_services import WebBotServices


class BotController:
    """Controller for bot automation tasks"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.running = False
        self.bot_thread = None
        self.web_bot_services = WebBotServices(main_window)

    def start(self):
        """Start the bot in a separate thread"""
        if not self.bot_thread or not self.bot_thread.is_alive():
            self.running = True
            self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()

    def stop(self):
        """Stop the bot"""
        self.running = False
        self.web_bot_services.running = False
        if self.bot_thread and self.bot_thread.is_alive():
            self.bot_thread.join(timeout=2)

    def run_web_service(self, service_name):
        """Run bot for specific web service with batch processing"""
        self.main_window.log_message(f"Starting web automation for: {service_name}")

        try:
            # Get settings from tabs
            translation_settings = self.main_window.translation_tab.get_settings()
            processing_settings = self.main_window.processing_tab.get_settings()

            # Get input file
            input_file = translation_settings.get('input_file')
            if not input_file or not os.path.exists(input_file):
                self.main_window.log_message("Error: No valid input file selected")
                self.main_window.root.after(0, self.main_window.stop_bot)
                return

            # Load translation prompt
            prompt_type = processing_settings.get('prompt_type')
            prompt = self.load_translation_prompt(input_file, prompt_type)
            if not prompt:
                self.main_window.log_message("Error: Failed to load translation prompt")
                self.main_window.root.after(0, self.main_window.stop_bot)
                return

            # Read input CSV
            df = pd.read_csv(input_file)
            if 'text' not in df.columns:
                self.main_window.log_message("Error: CSV file must have 'text' column")
                self.main_window.root.after(0, self.main_window.stop_bot)
                return

            # Get batch settings
            batch_size = int(processing_settings.get('batch_size', 10))

            # Process only first batch for testing
            if len(df) > 0:
                batch = df.iloc[0:min(batch_size, len(df))]
                batch_ids = batch['id'].tolist()
                self.main_window.log_message(f"Processing test batch (IDs: {batch_ids[0]}-{batch_ids[-1]}, {len(batch)} rows)")

                # Create batch text
                batch_text = "\n".join([f"{j+1}. {row['text']}" for j, (_, row) in enumerate(batch.iterrows())])

                # Run appropriate bot service
                if service_name == "Perplexity":
                    translations, error = self.web_bot_services.run_perplexity_bot(prompt, batch_text, len(batch))

                    if translations:
                        self.main_window.log_message(f"Successfully processed {len(translations)} translations")
                        # Process results similar to API
                        self.process_batch_results(batch, translations, input_file, prompt_type)
                    else:
                        self.main_window.log_message(f"Failed to get translations: {error}")

                elif service_name == "Gemini":
                    translations, error = self.web_bot_services.run_gemini_bot()
                elif service_name == "ChatGPT":
                    translations, error = self.web_bot_services.run_chatgpt_bot()
                elif service_name == "Claude":
                    translations, error = self.web_bot_services.run_claude_bot()
                elif service_name == "Grok":
                    translations, error = self.web_bot_services.run_grok_bot()
                else:
                    self.main_window.log_message(f"Web automation for {service_name} not yet implemented")

        except Exception as e:
            self.main_window.log_message(f"Web service error: {str(e)}")
        finally:
            self.main_window.root.after(0, self.main_window.stop_bot)

    def load_translation_prompt(self, input_path, prompt_type):
        """Load translation prompt based on detected language and prompt type"""
        input_filename = os.path.basename(input_path)

        # Detect source language from filename
        source_lang = None
        for lang in ['JP', 'EN', 'KR', 'CN', 'VI']:
            if lang in input_filename.upper():
                source_lang = lang
                break

        if not source_lang:
            self.main_window.log_message("Error: Could not detect source language from filename")
            return None

        try:
            prompt_file = "assets/translate_prompt.xlsx"
            if not os.path.exists(prompt_file):
                self.main_window.log_message("Error: Prompt file not found")
                return None

            df = pd.read_excel(prompt_file)

            if 'type' in df.columns and source_lang in df.columns:
                prompt_row = df[df['type'] == prompt_type]
                if not prompt_row.empty:
                    prompt = prompt_row.iloc[0][source_lang]
                    if pd.notna(prompt) and prompt:
                        self.main_window.log_message(f"Loaded prompt for {source_lang}, type: {prompt_type}")
                        return prompt

            return None

        except Exception as e:
            self.main_window.log_message(f"Error loading prompt: {e}")
            return None

    def process_batch_results(self, batch, translations, input_file, prompt_type):
        """Process batch results and save to output file"""
        try:
            # Generate output path
            output_path = self.generate_output_path(input_file, prompt_type)
            self.main_window.log_message(f"Saving results to: {output_path}")

            # Create results
            results = []
            for (idx, row), translation in zip(batch.iterrows(), translations):
                results.append({
                    'id': row['id'],
                    'raw': row['text'],
                    'edit': translation,
                    'status': 'completed' if translation else 'failed'
                })

            # Save to CSV
            if results:
                results_df = pd.DataFrame(results)
                results_df_sorted = results_df.sort_values('id')
                results_df_sorted.to_csv(output_path, index=False)

                completed_count = len([r for r in results if r['status'] == 'completed'])
                self.main_window.log_message(f"Batch completed: {completed_count}/{len(results)} successful")

        except Exception as e:
            self.main_window.log_message(f"Error processing results: {e}")

    def generate_output_path(self, input_path, prompt_type):
        """Generate output path based on input file name and prompt type"""
        input_filename = os.path.basename(input_path)

        # Detect language from filename
        lang_folder = None
        for lang in ['JP', 'EN', 'KR', 'CN', 'VI']:
            if lang in input_filename.upper():
                lang_folder = lang
                break

        if not lang_folder:
            lang_folder = "Other"

        # Create output filename
        filename_without_ext, ext = os.path.splitext(input_filename)
        if prompt_type:
            output_filename = f"{filename_without_ext}_{lang_folder}_{prompt_type}_translated{ext}"
        else:
            output_filename = f"{filename_without_ext}_{lang_folder}_translated{ext}"

        # Create output directory
        output_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "AIBridge",
            "Translated",
            lang_folder
        )
        os.makedirs(output_dir, exist_ok=True)

        return os.path.join(output_dir, output_filename)

    def run_bot(self):
        """Legacy method - redirects to run_web_service"""
        # Get selected service
        processing_settings = self.main_window.processing_tab.get_settings()
        ai_service = processing_settings.get('ai_service', 'Perplexity')
        self.run_web_service(ai_service)