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

    def run_bot(self):
        """Main bot execution logic"""
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
                self.main_window.log_message("Error: Input box not found!")
                self.main_window.root.after(0, self.main_window.stop_bot)
                return

            # Extract coordinates
            left, top, right, bottom, center_x, center_y = box_coords

            # Calculate click position (left + 40, center_x)
            click_x = center_x  # x is center point
            click_y = center_y - 20

            self.main_window.log_message(f"Input box found: left={left}, top={top}, right={right}, bottom={bottom}")
            self.main_window.log_message(f"Center point: ({center_x}, {center_y})")
            self.main_window.log_message(f"Clicking at ({click_x}, {click_y})")

            # Click on the input box
            pyautogui.click(click_x, click_y)
            time.sleep(0.5)

            # Type 'test'
            pyautogui.typewrite('test')
            self.main_window.log_message("Typed 'test' in input box")
            time.sleep(0.5)

            # Find send button
            self.main_window.log_message("Searching for send button...")
            send_btn_coords = find_template_position(
                "assets/Perplexity/send_btn.png",
                threshold=0.85,
                return_center=True
            )

            if send_btn_coords:
                if len(send_btn_coords) == 6:
                    left, top, right, bottom, center_x, center_y = send_btn_coords
                    self.main_window.log_message(f"Send button found at center: ({center_x}, {center_y})")
                else:
                    left, top, right, bottom = send_btn_coords
                    self.main_window.log_message(f"Send button found at: ({left}, {top}, {right}, {bottom})")
            else:
                self.main_window.log_message("Send button not found")

        except Exception as e:
            self.main_window.log_message(f"Bot error: {str(e)}")
            self.main_window.root.after(0, self.main_window.stop_bot)