import time
import pyautogui
import pyperclip
import re
from helper.recognizer import find_template_position
from helper.click_handler import find_and_click


class WebBotServices:
    """Web automation services for various AI platforms"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.running = False

    def run_perplexity_bot(self, prompt, batch_text, batch_size):
        """Run bot specifically for Perplexity web interface with batch processing"""
        try:
            # Get all coordinates including center
            box_coords = find_template_position(
                "assets/Perplexity/text_input_box.png",
                threshold=0.85,
                return_center=True
            )

            if not box_coords:
                self.main_window.log_message("Error: Perplexity input box not found!")
                self.main_window.log_message("Make sure Perplexity website is open and visible")
                return None, "Input box not found"

            # Extract coordinates
            left, top, right, bottom, center_x, center_y = box_coords

            # Calculate click position
            click_x = center_x
            click_y = center_y - 20

            # Click on the input box
            pyautogui.click(click_x, click_y)
            time.sleep(0.5)

            # Clear existing text and paste prompt with batch content
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)

            # Combine prompt with batch text
            full_text = prompt.format(count_info=f"Source text consists of {batch_size} numbered lines from 1 to {batch_size}.",
                                      text=batch_text)

            # Copy to clipboard and paste
            pyperclip.copy(full_text)
            pyautogui.hotkey('ctrl', 'v')
            self.main_window.log_message(f"Pasted prompt with {batch_size} lines of batch text")
            time.sleep(0.5)

            # Find and click send button
            send_btn_coords = find_template_position(
                "assets/Perplexity/send_btn.png",
                threshold=0.85,
                return_center=True
            )

            if send_btn_coords:
                left, top, right, bottom, center_x, center_y = send_btn_coords
                pyautogui.click(center_x, center_y)
            else:
                self.main_window.log_message("Send button not found, trying Enter key")
                pyautogui.press('enter')

            # Wait for processing to complete
            screen_width, screen_height = pyautogui.size()
            processing_region = (0, screen_height - 300, screen_width, 300)  # Bottom 300px of screen

            is_processing = True
            attempt_count = 0
            max_wait_attempts = 20

            while is_processing and attempt_count < max_wait_attempts:
                processing_icon = find_and_click(
                    "assets/Perplexity/is_processing.png",
                    region=processing_region,
                    click=False,
                    max_attempts=1,
                    confidence=0.85,
                    log_func=self.main_window.log_message
                )

                if processing_icon:
                    time.sleep(5.0)
                    attempt_count += 1
                else:
                    is_processing = False

            screen_width, screen_height = pyautogui.size()
            for i in range(2):
                pyautogui.click(screen_width // 2, screen_height // 2)
                time.sleep(0.5)
                pyautogui.press('end')
                time.sleep(0.5)

            # Look for action icons to find copy button
            action_icons = find_template_position(
                "assets/Perplexity/action_icons.png",
                threshold=0.85,
                return_center=False
            )

            if action_icons:
                # Define region around action icons for copy button
                left, top, right, bottom = action_icons
                action_region = (left - 50, top - 50, right - left + 100, bottom - top + 100)

                copy_result = find_and_click(
                    "assets/Perplexity/copy_btn.png",
                    region=action_region,
                    click=True,
                    max_attempts=3,
                    delay_between=1.0,
                    confidence=0.85,
                    log_func=self.main_window.log_message
                )

                if copy_result:
                    time.sleep(0.5)

                    # Get response from clipboard
                    response_text = pyperclip.paste()

                    # Parse the response similar to API response parsing
                    translated_lines = self.parse_numbered_text(response_text, batch_size)

                    # Clean up chat
                    self.cleanup_perplexity_chat()

                    return translated_lines, None
                else:
                    self.main_window.log_message("Failed to find copy button")
            else:
                self.main_window.log_message("Action icons not found")

            # Clean up even if failed
            self.cleanup_perplexity_chat()

            return None, "Failed to get response"

        except Exception as e:
            self.main_window.log_message(f"Perplexity bot error: {str(e)}")
            return None, str(e)

    def cleanup_perplexity_chat(self):
        """Clean up Perplexity chat by deleting the conversation"""
        try:
            self.main_window.log_message("Cleaning up chat...")

            # Find chat option region at top of screen
            screen_width, _ = pyautogui.size()
            top_region = (screen_width/2, 0, screen_width, 300)  # Top 300px of screen

            more_clicked = find_and_click(
                "assets/Perplexity/more_btn.png",
                region=top_region,
                click=True,
                max_attempts=3,
                delay_between=1.0,
                confidence=0.85,
                log_func=self.main_window.log_message
            )

            if more_clicked:
                time.sleep(0.5)

                # Click delete button
                delete_clicked = find_and_click(
                    "assets/Perplexity/delete_btn.png",
                    click=True,
                    max_attempts=3,
                    delay_between=1.0,
                    confidence=0.85,
                    log_func=self.main_window.log_message
                )

                if delete_clicked:
                    time.sleep(0.5)

                    # Click confirm button
                    confirm_clicked = find_and_click(
                        "assets/Perplexity/confirm_btn.png",
                        click=True,
                        max_attempts=3,
                        delay_between=1.0,
                        confidence=0.85,
                        log_func=self.main_window.log_message
                    )

                    if confirm_clicked:
                        self.main_window.log_message("Chat deleted successfully")
                    else:
                        self.main_window.log_message("Failed to confirm deletion")
                else:
                    self.main_window.log_message("Failed to click delete button")
            else:
                self.main_window.log_message("Failed to click more button")

        except Exception as e:
            self.main_window.log_message(f"Cleanup error: {str(e)}")

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

    def run_gemini_bot(self):
        """Run bot specifically for Gemini web interface"""
        try:
            # self.main_window.log_message("Starting Gemini web automation...")
            # self.main_window.log_message("Gemini web automation is under development")
            #
            # # TODO: Implement Gemini web interface automation
            # # This would involve:
            # # 1. Finding Gemini input field
            # # 2. Typing translation prompt
            # # 3. Sending the prompt
            # # 4. Extracting the response
            #
            # self.main_window.log_message("Gemini web automation not yet fully implemented")
            # return None, "Not implemented"
            self.cleanup_perplexity_chat()

        except Exception as e:
            self.main_window.log_message(f"Gemini bot error: {str(e)}")
            return None, str(e)

    def run_chatgpt_bot(self):
        """Run bot specifically for ChatGPT web interface"""
        try:
            self.main_window.log_message("Starting ChatGPT web automation...")
            self.main_window.log_message("ChatGPT web automation is under development")

            # TODO: Implement ChatGPT web interface automation

            self.main_window.log_message("ChatGPT web automation not yet fully implemented")
            return None, "Not implemented"

        except Exception as e:
            self.main_window.log_message(f"ChatGPT bot error: {str(e)}")
            return None, str(e)

    def run_claude_bot(self):
        """Run bot specifically for Claude web interface"""
        try:
            self.main_window.log_message("Starting Claude web automation...")
            self.main_window.log_message("Claude web automation is under development")

            # TODO: Implement Claude web interface automation

            self.main_window.log_message("Claude web automation not yet fully implemented")
            return None, "Not implemented"

        except Exception as e:
            self.main_window.log_message(f"Claude bot error: {str(e)}")
            return None, str(e)

    def run_grok_bot(self):
        """Run bot specifically for Grok web interface"""
        try:
            self.main_window.log_message("Starting Grok web automation...")
            self.main_window.log_message("Grok web automation is under development")

            # TODO: Implement Grok web interface automation

            self.main_window.log_message("Grok web automation not yet fully implemented")
            return None, "Not implemented"

        except Exception as e:
            self.main_window.log_message(f"Grok bot error: {str(e)}")
            return None, str(e)