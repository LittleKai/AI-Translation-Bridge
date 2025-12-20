import pandas as pd
import requests
import json
import time
import os
import re
import random
from datetime import datetime


class TranslationProcessor:
    """Handles translation processing using various AI APIs"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.is_running = False
        self.current_api_keys = []
        self.failed_keys = set()

    def start_processing(self):
        """Start the translation processing"""
        self.is_running = True

        try:
            # Get settings from tabs
            translation_settings = self.main_window.translation_tab.get_settings()
            processing_settings = self.main_window.processing_tab.get_settings()

            # Get input file (now contains full path)
            input_file = translation_settings.get('input_file')
            if not input_file:
                self.main_window.log_message("Error: No input file selected")
                return

            # Check if input file exists
            if not os.path.exists(input_file):
                self.main_window.log_message(f"Error: Input file does not exist: {input_file}")
                return

            self.main_window.log_message(f"Processing file: {os.path.basename(input_file)}")
            self.main_window.log_message(f"Full path: {input_file}")

            # Generate output path based on input file
            output_path = self.generate_output_path(input_file, processing_settings.get('prompt_type'))
            self.main_window.log_message(f"Output will be saved to: {output_path}")

            # Load API configuration
            ai_service = processing_settings.get('ai_service')
            if "API" in ai_service:
                api_config = processing_settings['api_configs'].get(ai_service, {})
                self.current_api_keys = api_config.get('keys', [])

                if not self.current_api_keys:
                    self.main_window.log_message(f"Error: No API keys configured for {ai_service}")
                    return

                # Process with API
                self.process_with_api(
                    input_file,
                    output_path,
                    ai_service,
                    processing_settings.get('ai_model'),
                    api_config,
                    int(processing_settings.get('batch_size', 10)),
                    processing_settings.get('prompt_type'),
                    translation_settings.get('start_id'),
                    translation_settings.get('stop_id')
                )
            else:
                # Process with web interface (existing functionality)
                self.main_window.log_message(f"Web interface mode for {ai_service} not yet implemented")

        except Exception as e:
            self.main_window.log_message(f"Error during processing: {e}")
            import traceback
            self.main_window.log_message(traceback.format_exc())
        finally:
            self.is_running = False

    def generate_output_path(self, input_path, version_suffix=""):
        """Generate output path based on input file and detected language"""
        # Get absolute path to work with
        input_path = os.path.abspath(input_path)
        input_filename = os.path.basename(input_path)
        input_dirname = os.path.dirname(input_path)

        # Detect language from folder name or file path
        lang_match = re.search(r'Raw_(JP|EN|KR|CN|VI)', input_dirname)

        if not lang_match:
            # Try to detect from filename
            for lang in ['JP', 'EN', 'KR', 'CN', 'VI']:
                if lang.lower() in input_filename.lower():
                    lang_folder = lang
                    break
            else:
                lang_folder = "Other"
                self.main_window.log_message(f"Warning: Could not detect language, using 'Other' folder")
        else:
            lang_folder = lang_match.group(1)
            self.main_window.log_message(f"Detected output language folder: {lang_folder}")

        # Create output filename
        filename_without_ext, ext = os.path.splitext(input_filename)

        if version_suffix:
            output_filename = f"{filename_without_ext}_{version_suffix}_translated{ext}"
        else:
            output_filename = f"{filename_without_ext}_translated{ext}"

        # Create output directory
        output_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "AIBridge",
            "Translated",
            lang_folder
        )

        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)

        return os.path.join(output_dir, output_filename)

    def load_translation_prompt(self, input_path, prompt_type):
        """Load translation prompt based on detected language and prompt type"""
        # Get absolute path
        input_path = os.path.abspath(input_path)

        # Detect source language
        lang_match = re.search(r'Raw_(JP|EN|KR|CN|VI)', input_path)

        if not lang_match:
            # Try filename detection
            filename = os.path.basename(input_path)
            for lang in ['JP', 'EN', 'KR', 'CN', 'VI']:
                if lang.lower() in filename.lower():
                    source_lang = lang
                    break
            else:
                self.main_window.log_message("Error: Could not detect source language from path")
                self.main_window.log_message("Path should contain a folder like 'Raw_CN' or filename with language code")
                return None
        else:
            source_lang = lang_match.group(1)

        self.main_window.log_message(f"Detected source language: {source_lang}")

        # Load prompt from Excel file
        try:
            prompt_file = "assets/translate_prompt.xlsx"
            if not os.path.exists(prompt_file):
                self.main_window.log_message("Error: Prompt file not found")
                return None

            df = pd.read_excel(prompt_file)

            # Find prompt for the specified type and language
            if 'type' in df.columns and source_lang in df.columns:
                prompt_row = df[df['type'] == prompt_type]
                if not prompt_row.empty:
                    prompt = prompt_row.iloc[0][source_lang]
                    if pd.notna(prompt) and prompt:
                        self.main_window.log_message(f"Loaded prompt for {source_lang}, type: {prompt_type}")
                        return prompt

            self.main_window.log_message(f"Error: Could not find prompt for {source_lang}, type: {prompt_type}")
            return None

        except Exception as e:
            self.main_window.log_message(f"Error loading prompt: {e}")
            return None

    def process_with_api(self, input_file, output_file, ai_service, model_name, api_config,
                         batch_size, prompt_type, start_id, stop_id):
        """Process translation using AI API"""

        # Load translation prompt
        prompt_template = self.load_translation_prompt(input_file, prompt_type)
        if not prompt_template:
            return

        # Read input CSV
        try:
            df = pd.read_csv(input_file)
            self.main_window.log_message(f"Loaded {len(df)} rows from input file")
        except Exception as e:
            self.main_window.log_message(f"Error reading input file: {e}")
            return

        # Filter by ID range
        try:
            start_id = int(start_id) if start_id else None
            stop_id = int(stop_id) if stop_id else None

            if start_id:
                df = df[df['id'] >= start_id]
            if stop_id:
                df = df[df['id'] <= stop_id]

            self.main_window.log_message(f"Processing {len(df)} rows after filtering")
        except:
            pass

        # Process in batches
        batch_size = int(batch_size) if batch_size else 10
        results = []

        for i in range(0, len(df), batch_size):
            if not self.is_running:
                self.main_window.log_message("Processing stopped by user")
                break

            batch = df.iloc[i:i+batch_size]
            self.main_window.log_message(f"Processing batch {i//batch_size + 1}/{(len(df)-1)//batch_size + 1}")

            # Create batch text
            batch_text = "\n".join([f"{j+1}. {row['text']}" for j, row in batch.iterrows()])

            # Format prompt
            count_info = f"Source text consists of {len(batch)} numbered lines from 1 to {len(batch)}."
            prompt = prompt_template.format(count_info=count_info, text=batch_text)

            # Call appropriate API
            translated_text = None

            if ai_service == "Gemini API":
                translated_text = self.call_gemini_api(prompt, model_name, api_config)
            elif ai_service == "ChatGPT API":
                translated_text = self.call_openai_api(prompt, model_name, api_config)
            elif ai_service == "Claude API":
                translated_text = self.call_claude_api(prompt, model_name, api_config)
            elif ai_service == "Grok API":
                translated_text = self.call_grok_api(prompt, model_name, api_config)
            elif ai_service == "Perplexity API":
                translated_text = self.call_perplexity_api(prompt, model_name, api_config)

            if translated_text:
                # Parse translated text
                translations = self.parse_numbered_text(translated_text, len(batch))

                # Add to results
                for (idx, row), translation in zip(batch.iterrows(), translations):
                    results.append({
                        'id': row['id'],
                        'cn': row['text'],
                        'edit': translation,
                        'status': 'completed' if translation else 'failed'
                    })
            else:
                # Mark batch as failed
                for idx, row in batch.iterrows():
                    results.append({
                        'id': row['id'],
                        'cn': row['text'],
                        'edit': '',
                        'status': 'failed'
                    })

            # Small delay between batches
            time.sleep(2)

        # Save results
        if results:
            results_df = pd.DataFrame(results)
            results_df.to_csv(output_file, index=False)
            self.main_window.log_message(f"Saved {len(results)} translations to {output_file}")

            # Sort by ID
            results_df_sorted = results_df.sort_values('id')
            results_df_sorted.to_csv(output_file, index=False)
            self.main_window.log_message("Output file sorted by ID")

    def get_random_api_key(self):
        """Get a random API key from the available keys"""
        available_keys = [key for key in self.current_api_keys if key not in self.failed_keys]
        if available_keys:
            return random.choice(available_keys)
        return None

    def call_gemini_api(self, prompt, model_name, config):
        """Call Google Gemini API"""
        api_key = self.get_random_api_key()
        if not api_key:
            self.main_window.log_message("No available API keys for Gemini")
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": config.get('temperature', 1.0),
                "maxOutputTokens": config.get('max_tokens', 8192),
                "topP": config.get('top_p', 0.95),
                "topK": config.get('top_k', 40)
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                self.main_window.log_message(f"Gemini API error: {response.status_code}")
                if response.status_code in [401, 403, 429]:
                    self.failed_keys.add(api_key)
        except Exception as e:
            self.main_window.log_message(f"Gemini API exception: {e}")

        return None

    def call_openai_api(self, prompt, model_name, config):
        """Call OpenAI ChatGPT API"""
        api_key = self.get_random_api_key()
        if not api_key:
            self.main_window.log_message("No available API keys for ChatGPT")
            return None

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get('max_tokens', 4096),
            "temperature": config.get('temperature', 1.0),
            "top_p": config.get('top_p', 1.0)
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                self.main_window.log_message(f"ChatGPT API error: {response.status_code}")
                if response.status_code in [401, 403, 429]:
                    self.failed_keys.add(api_key)
        except Exception as e:
            self.main_window.log_message(f"ChatGPT API exception: {e}")

        return None

    def call_claude_api(self, prompt, model_name, config):
        """Call Anthropic Claude API"""
        api_key = self.get_random_api_key()
        if not api_key:
            self.main_window.log_message("No available API keys for Claude")
            return None

        url = "https://api.anthropic.com/v1/messages"

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get('max_tokens', 4096),
            "temperature": config.get('temperature', 1.0),
            "top_p": config.get('top_p', 1.0)
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                self.main_window.log_message(f"Claude API error: {response.status_code}")
                if response.status_code in [401, 403, 429]:
                    self.failed_keys.add(api_key)
        except Exception as e:
            self.main_window.log_message(f"Claude API exception: {e}")

        return None

    def call_grok_api(self, prompt, model_name, config):
        """Call xAI Grok API"""
        api_key = self.get_random_api_key()
        if not api_key:
            self.main_window.log_message("No available API keys for Grok")
            return None

        url = "https://api.x.ai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get('max_tokens', 4096),
            "temperature": config.get('temperature', 1.0),
            "top_p": config.get('top_p', 1.0)
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                self.main_window.log_message(f"Grok API error: {response.status_code}")
                if response.status_code in [401, 403, 429]:
                    self.failed_keys.add(api_key)
        except Exception as e:
            self.main_window.log_message(f"Grok API exception: {e}")

        return None

    def call_perplexity_api(self, prompt, model_name, config):
        """Call Perplexity API"""
        api_key = self.get_random_api_key()
        if not api_key:
            self.main_window.log_message("No available API keys for Perplexity")
            return None

        url = "https://api.perplexity.ai/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get('max_tokens', 4096),
            "temperature": config.get('temperature', 1.0),
            "top_p": config.get('top_p', 1.0)
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                self.main_window.log_message(f"Perplexity API error: {response.status_code}")
                if response.status_code in [401, 403, 429]:
                    self.failed_keys.add(api_key)
        except Exception as e:
            self.main_window.log_message(f"Perplexity API exception: {e}")

        return None

    def parse_numbered_text(self, text, expected_count):
        """Parse numbered text into list of translations"""
        lines = []

        # Find lines with pattern "number. text"
        pattern = r'(\d+)\.\s*(.*?)(?=\n\d+\.|$)'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            # Create dictionary with line number as key
            numbered_lines = {int(num): content.strip() for num, content in matches}

            # Fill in all lines
            for i in range(1, expected_count + 1):
                if i in numbered_lines:
                    lines.append(numbered_lines[i])
                else:
                    lines.append("")  # Missing line
        else:
            # Fallback: split by newline
            text_lines = text.strip().split('\n')
            for line in text_lines[:expected_count]:
                cleaned = re.sub(r'^\d+\.\s*', '', line).strip()
                lines.append(cleaned)

            # Pad with empty strings if needed
            while len(lines) < expected_count:
                lines.append("")

        return lines