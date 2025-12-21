import requests
import random


class AIAPIHandler:
    """Handler for various AI API calls"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.failed_keys = set()

    def get_random_api_key(self, api_keys):
        """Get a random API key from available keys"""
        available_keys = [key for key in api_keys if key not in self.failed_keys]
        if available_keys:
            return random.choice(available_keys)
        return None

    def call_gemini_api(self, prompt, model_name, config, api_keys):
        """Call Google Gemini API"""
        api_key = self.get_random_api_key(api_keys)
        if not api_key:
            error_msg = "No available API keys for Gemini"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg

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
            self.main_window.log_message(f"Calling Gemini API with model: {model_name}")
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    self.main_window.log_message("Gemini API call successful")
                    return text, None
                else:
                    error_msg = "No valid response from Gemini API"
                    self.main_window.log_message(f"Error: {error_msg}")
                    return None, error_msg
            else:
                error_msg = f"Gemini API error - Status: {response.status_code}, Response: {response.text}"
                self.main_window.log_message(f"Error: {error_msg}")
                if response.status_code in [401, 403, 429]:
                    self.failed_keys.add(api_key)
                    self.main_window.log_message(f"API key marked as failed: {api_key[:10]}...")
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Gemini API timeout (30s exceeded)"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg
        except Exception as e:
            error_msg = f"Gemini API exception: {str(e)}"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg

    def call_openai_api(self, prompt, model_name, config, api_keys):
        """Call OpenAI ChatGPT API"""
        api_key = self.get_random_api_key(api_keys)
        if not api_key:
            error_msg = "No available API keys for ChatGPT"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg

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
            self.main_window.log_message(f"Calling ChatGPT API with model: {model_name}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and result['choices']:
                    text = result['choices'][0]['message']['content']
                    self.main_window.log_message("ChatGPT API call successful")
                    return text, None
                else:
                    error_msg = "No valid response from ChatGPT API"
                    self.main_window.log_message(f"Error: {error_msg}")
                    return None, error_msg
            else:
                error_msg = f"ChatGPT API error - Status: {response.status_code}, Response: {response.text}"
                self.main_window.log_message(f"Error: {error_msg}")
                if response.status_code in [401, 403, 429]:
                    self.failed_keys.add(api_key)
                    self.main_window.log_message(f"API key marked as failed: {api_key[:10]}...")
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "ChatGPT API timeout (30s exceeded)"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg
        except Exception as e:
            error_msg = f"ChatGPT API exception: {str(e)}"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg

    def call_claude_api(self, prompt, model_name, config, api_keys):
        """Call Anthropic Claude API"""
        api_key = self.get_random_api_key(api_keys)
        if not api_key:
            error_msg = "No available API keys for Claude"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg

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
            self.main_window.log_message(f"Calling Claude API with model: {model_name}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'content' in result and result['content']:
                    text = result['content'][0]['text']
                    self.main_window.log_message("Claude API call successful")
                    return text, None
                else:
                    error_msg = "No valid response from Claude API"
                    self.main_window.log_message(f"Error: {error_msg}")
                    return None, error_msg
            else:
                error_msg = f"Claude API error - Status: {response.status_code}, Response: {response.text}"
                self.main_window.log_message(f"Error: {error_msg}")
                if response.status_code in [401, 403, 429]:
                    self.failed_keys.add(api_key)
                    self.main_window.log_message(f"API key marked as failed: {api_key[:10]}...")
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Claude API timeout (30s exceeded)"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg
        except Exception as e:
            error_msg = f"Claude API exception: {str(e)}"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg

    def call_grok_api(self, prompt, model_name, config, api_keys):
        """Call xAI Grok API"""
        api_key = self.get_random_api_key(api_keys)
        if not api_key:
            error_msg = "No available API keys for Grok"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg

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
            self.main_window.log_message(f"Calling Grok API with model: {model_name}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and result['choices']:
                    text = result['choices'][0]['message']['content']
                    self.main_window.log_message("Grok API call successful")
                    return text, None
                else:
                    error_msg = "No valid response from Grok API"
                    self.main_window.log_message(f"Error: {error_msg}")
                    return None, error_msg
            else:
                error_msg = f"Grok API error - Status: {response.status_code}, Response: {response.text}"
                self.main_window.log_message(f"Error: {error_msg}")
                if response.status_code in [401, 403, 429]:
                    self.failed_keys.add(api_key)
                    self.main_window.log_message(f"API key marked as failed: {api_key[:10]}...")
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Grok API timeout (30s exceeded)"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg
        except Exception as e:
            error_msg = f"Grok API exception: {str(e)}"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg

