import threading
import time
import pyautogui
from helper.recognizer import find_template_position


class BotController:
    """Controller for bot automation tasks"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.running = False
        self.bot_thread = None

    def start(self):
        """Start the bot in a separate thread"""
        if not self.bot_thread or not self.bot_thread.is_alive():
            self.running = True
            self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()

    def stop(self):
        """Stop the bot"""
        self.running = False
        if self.bot_thread and self.bot_thread.is_alive():
            self.bot_thread.join(timeout=2)

    def run_web_service(self, service_name):
        """Run bot for specific web service"""
        self.main_window.log_message(f"Starting web automation for: {service_name}")

        if service_name == "Perplexity":
            self.run_perplexity_bot()
        elif service_name == "Gemini":
            self.run_gemini_bot()
        elif service_name == "ChatGPT":
            self.run_chatgpt_bot()
        elif service_name == "Claude":
            self.run_claude_bot()
        elif service_name == "Grok":
            self.run_grok_bot()
        else:
            self.main_window.log_message(f"Web automation for {service_name} not yet implemented")
            self.main_window.root.after(0, self.main_window.stop_bot)

    def run_perplexity_bot(self):
        """Run bot specifically for Perplexity web interface"""
        try:
            # Find text input box
            self.main_window.log_message("Searching for Perplexity input box...")

            # Get all coordinates including center
            box_coords = find_template_position(
                "assets/Perplexity/text_input_box.png",
                threshold=0.85,
                return_center=True
            )

            if not box_coords:
                self.main_window.log_message("Error: Perplexity input box not found!")
                self.main_window.log_message("Make sure Perplexity website is open and visible")
                self.main_window.root.after(0, self.main_window.stop_bot)
                return

            # Extract coordinates
            left, top, right, bottom, center_x, center_y = box_coords

            # Calculate click position
            click_x = center_x
            click_y = center_y - 20

            self.main_window.log_message(f"Input box found at: ({center_x}, {center_y})")
            self.main_window.log_message(f"Clicking at ({click_x}, {click_y})")

            # Click on the input box
            pyautogui.click(click_x, click_y)
            time.sleep(0.5)

            # Type test message
            test_message = "test translation"
            pyautogui.typewrite(test_message)
            self.main_window.log_message(f"Typed '{test_message}' in input box")
            time.sleep(0.5)

            # Find send button
            self.main_window.log_message("Searching for send button...")
            send_btn_coords = find_template_position(
                "assets/Perplexity/send_btn.png",
                threshold=0.85,
                return_center=True
            )

            if send_btn_coords:
                left, top, right, bottom, center_x, center_y = send_btn_coords
                self.main_window.log_message(f"Send button found at: ({center_x}, {center_y})")
                pyautogui.click(center_x, center_y)
                self.main_window.log_message("Clicked send button")
            else:
                self.main_window.log_message("Send button not found, trying Enter key")
                pyautogui.press('enter')

            self.main_window.log_message("Perplexity bot task completed")

        except Exception as e:
            self.main_window.log_message(f"Perplexity bot error: {str(e)}")
            self.main_window.root.after(0, self.main_window.stop_bot)

    def run_gemini_bot(self):
        """Run bot specifically for Gemini web interface"""
        try:
            self.main_window.log_message("Starting Gemini web automation...")
            self.main_window.log_message("Gemini web automation is under development")

            # TODO: Implement Gemini web interface automation
            # This would involve:
            # 1. Finding Gemini input field
            # 2. Typing translation prompt
            # 3. Sending the prompt
            # 4. Extracting the response

            self.main_window.log_message("Gemini web automation not yet fully implemented")

        except Exception as e:
            self.main_window.log_message(f"Gemini bot error: {str(e)}")
        finally:
            self.main_window.root.after(0, self.main_window.stop_bot)

    def run_chatgpt_bot(self):
        """Run bot specifically for ChatGPT web interface"""
        try:
            self.main_window.log_message("Starting ChatGPT web automation...")
            self.main_window.log_message("ChatGPT web automation is under development")

            # TODO: Implement ChatGPT web interface automation

            self.main_window.log_message("ChatGPT web automation not yet fully implemented")

        except Exception as e:
            self.main_window.log_message(f"ChatGPT bot error: {str(e)}")
        finally:
            self.main_window.root.after(0, self.main_window.stop_bot)

    def run_claude_bot(self):
        """Run bot specifically for Claude web interface"""
        try:
            self.main_window.log_message("Starting Claude web automation...")
            self.main_window.log_message("Claude web automation is under development")

            # TODO: Implement Claude web interface automation

            self.main_window.log_message("Claude web automation not yet fully implemented")

        except Exception as e:
            self.main_window.log_message(f"Claude bot error: {str(e)}")
        finally:
            self.main_window.root.after(0, self.main_window.stop_bot)

    def run_grok_bot(self):
        """Run bot specifically for Grok web interface"""
        try:
            self.main_window.log_message("Starting Grok web automation...")
            self.main_window.log_message("Grok web automation is under development")

            # TODO: Implement Grok web interface automation

            self.main_window.log_message("Grok web automation not yet fully implemented")

        except Exception as e:
            self.main_window.log_message(f"Grok bot error: {str(e)}")
        finally:
            self.main_window.root.after(0, self.main_window.stop_bot)

    def run_bot(self):
        """Legacy method - redirects to Perplexity bot"""
        self.run_perplexity_bot()