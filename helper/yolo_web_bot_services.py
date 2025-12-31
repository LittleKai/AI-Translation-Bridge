"""
YOLO-based Web Bot Services
Replacement for template matching with YOLO Nano object detection
"""

import time
import pyautogui
import pyperclip
import numpy as np
from PIL import ImageGrab
import cv2
from ultralytics import YOLO
from helper.translation_processor import TranslationProcessor


class YOLOWebBotServices:
    """Web automation services using YOLO Nano for UI element detection"""

    def __init__(self, main_window, model_path="models/yolo_nano_ui.pt"):
        self.main_window = main_window
        self.running = False
        self.model = None
        self.model_path = model_path
        self.load_model()
        
        # Service-specific class mappings
        self.service_classes = {
            'Perplexity': {
                'input_box': 0,
                'send_btn': 1,
                'processing_indicator': 2,
                'action_icons': 3,
                'copy_btn': 4,
                'more_btn': 5,
                'delete_btn': 6,
                'confirm_btn': 7
            },
            'Gemini': {
                'input_box': 8,
                'send_btn': 9,
                'processing_indicator': 10,
                'action_icons': 11,
                'copy_btn': 12,
                'more_btn': 13,
                'delete_btn': 14,
                'confirm_btn': 15
            },
            'ChatGPT': {
                'input_box': 16,
                'send_btn': 17,
                'processing_indicator': 18,
                'action_icons': 19,
                'copy_btn': 20,
                'more_btn': 21,
                'delete_btn': 22,
                'confirm_btn': 23
            },
            'Claude': {
                'input_box': 24,
                'send_btn': 25,
                'processing_indicator': 26,
                'action_icons': 27,
                'copy_btn': 28,
                'more_btn': 29,
                'delete_btn': 30,
                'confirm_btn': 31
            },
            'Grok': {
                'input_box': 32,
                'send_btn': 33,
                'processing_indicator': 34,
                'action_icons': 35,
                'copy_btn': 36,
                'more_btn': 37,
                'delete_btn': 38,
                'confirm_btn': 39
            }
        }
        
        # Input click offset configurations
        self.input_offsets = {
            'Perplexity': -20,
            'Gemini': 0,
            'ChatGPT': 0,
            'Claude': 0,
            'Grok': 0
        }

    def load_model(self):
        """Load YOLO Nano model for UI detection"""
        try:
            self.model = YOLO(self.model_path)
            self.main_window.log_message(f"YOLO model loaded: {self.model_path}")
        except Exception as e:
            self.main_window.log_message(f"Error loading YOLO model: {e}")
            self.main_window.log_message("Please train and save model first")

    def get_screen_region(self, region_ratio=None):
        """
        Convert region ratio to absolute coordinates
        
        Args:
            region_ratio: Tuple of (left_ratio, top_ratio, width_ratio, height_ratio)
                         where each value is 0.0 to 1.0 representing percentage of screen
                         None means full screen
        
        Returns:
            Tuple of (left, top, right, bottom) in pixels
        """
        screen_width, screen_height = pyautogui.size()
        
        if region_ratio is None:
            return (0, 0, screen_width, screen_height)
        
        left_ratio, top_ratio, width_ratio, height_ratio = region_ratio
        
        left = int(screen_width * left_ratio)
        top = int(screen_height * top_ratio)
        width = int(screen_width * width_ratio)
        height = int(screen_height * height_ratio)
        
        right = left + width
        bottom = top + height
        
        return (left, top, right, bottom)

    def detect_element(self, class_id, region_ratio=None, confidence=0.5, max_attempts=5, delay_between=2.0):
        """
        Detect UI element using YOLO
        
        Args:
            class_id: YOLO class ID for the element
            region_ratio: Screen region ratio (left, top, width, height) as 0.0-1.0
            confidence: Detection confidence threshold
            max_attempts: Maximum detection attempts
            delay_between: Delay between attempts in seconds
            
        Returns:
            Tuple of (center_x, center_y, box_width, box_height) or None if not found
        """
        if self.model is None:
            self.main_window.log_message("Error: YOLO model not loaded")
            return None
        
        # Get absolute screen region
        left, top, right, bottom = self.get_screen_region(region_ratio)
        
        for attempt in range(max_attempts):
            try:
                # Capture screen region
                screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
                img_array = np.array(screenshot)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Run YOLO detection
                results = self.model(img_bgr, verbose=False)
                
                # Parse detections
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        # Check class ID and confidence
                        if int(box.cls[0]) == class_id and float(box.conf[0]) >= confidence:
                            # Get bounding box coordinates (relative to region)
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            
                            # Calculate absolute screen coordinates
                            abs_x1 = left + x1
                            abs_y1 = top + y1
                            abs_x2 = left + x2
                            abs_y2 = top + y2
                            
                            # Calculate center and dimensions
                            center_x = (abs_x1 + abs_x2) / 2
                            center_y = (abs_y1 + abs_y2) / 2
                            box_width = abs_x2 - abs_x1
                            box_height = abs_y2 - abs_y1
                            
                            return (int(center_x), int(center_y), int(box_width), int(box_height))
                
            except Exception as e:
                self.main_window.log_message(f"Detection error: {e}")
            
            # Wait before retry
            if attempt < max_attempts - 1:
                time.sleep(delay_between)
        
        return None

    def click_element(self, class_id, region_ratio=None, confidence=0.5, offset_y=0):
        """
        Detect and click UI element
        
        Args:
            class_id: YOLO class ID
            region_ratio: Screen region ratio
            confidence: Detection confidence
            offset_y: Y-axis offset for click position
            
        Returns:
            True if clicked successfully, False otherwise
        """
        detection = self.detect_element(class_id, region_ratio, confidence)
        
        if detection:
            center_x, center_y, width, height = detection
            click_y = center_y + offset_y
            
            pyautogui.click(center_x, click_y)
            return True
        
        return False

    def run_generic_bot(self, service_name, prompt, batch_text, batch_size):
        """
        Generic bot runner using YOLO detection
        
        Args:
            service_name: AI service name (Perplexity, Gemini, etc.)
            prompt: Translation prompt template
            batch_text: Batch text to process
            batch_size: Number of lines in batch
            
        Returns:
            Tuple of (translations_list, error_message)
        """
        try:
            self.running = True
            
            if service_name not in self.service_classes:
                error_msg = f"Error: Service {service_name} not configured"
                self.main_window.log_message(error_msg)
                return None, error_msg
            
            classes = self.service_classes[service_name]
            input_offset = self.input_offsets.get(service_name, 0)
            
            # Step 1: Find and click input box
            self.main_window.log_message(f"Looking for {service_name} input box...")
            
            detection = self.detect_element(
                classes['input_box'],
                region_ratio=None,
                confidence=0.7,
                max_attempts=5,
                delay_between=2.0
            )
            
            if not detection:
                error_msg = f"Critical: {service_name} input box not found! Stopping bot."
                self.main_window.log_message(error_msg)
                return None, error_msg
            
            center_x, center_y, width, height = detection
            click_y = center_y + input_offset
            
            # Click input box
            pyautogui.click(center_x, click_y)
            time.sleep(0.5)
            
            # Step 2: Clear and input text
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            
            # Prepare full prompt
            full_text = prompt.format(
                count_info=f"Source text consists of {batch_size} numbered lines from 1 to {batch_size}.",
                text=batch_text
            )
            
            # Copy and paste
            pyperclip.copy(full_text)
            pyautogui.hotkey('ctrl', 'v')
            self.main_window.log_message(f"Pasted prompt with {batch_size} lines to {service_name}")
            time.sleep(0.5)
            
            # Step 3: Click send button
            self.main_window.log_message("Clicking send button...")
            
            if not self.click_element(classes['send_btn'], confidence=0.7):
                error_msg = f"Critical: {service_name} send button not found! Stopping bot."
                self.main_window.log_message(error_msg)
                return None, error_msg
            
            self.main_window.log_message("Send button clicked")
            time.sleep(3)
            
            # Step 4: Wait for processing
            self.main_window.log_message(f"Waiting for {service_name} to process...")
            self.wait_for_processing(classes['processing_indicator'])
            
            # Step 5: Scroll to bottom and find action icons
            action_coords = self.ensure_scroll_to_bottom(classes['action_icons'])
            
            if not action_coords:
                error_msg = f"Critical: {service_name} action icons not found! Stopping bot."
                self.main_window.log_message(error_msg)
                self.cleanup_chat(service_name, classes)
                return None, error_msg
            
            action_x, action_y, _, _ = action_coords
            
            # Step 6: Click copy button (search near action icons)
            # Define region around action icons (±100px)
            screen_width, screen_height = pyautogui.size()
            copy_region = (
                max(0, (action_x - 100) / screen_width),
                max(0, (action_y - 100) / screen_height),
                min(1.0, 200 / screen_width),
                min(1.0, 200 / screen_height)
            )
            
            copy_detection = self.detect_element(
                classes['copy_btn'],
                region_ratio=copy_region,
                confidence=0.7,
                max_attempts=3
            )
            
            if not copy_detection:
                error_msg = f"Critical: {service_name} copy button not found! Stopping bot."
                self.main_window.log_message(error_msg)
                self.cleanup_chat(service_name, classes)
                return None, error_msg
            
            # Click copy button
            copy_x, copy_y, _, _ = copy_detection
            pyautogui.click(copy_x, copy_y)
            time.sleep(0.5)
            
            # Get response from clipboard
            response_text = pyperclip.paste()
            
            # Parse response
            translated_lines = TranslationProcessor.parse_numbered_text(response_text, batch_size)
            
            # Cleanup
            self.cleanup_chat(service_name, classes)
            
            return translated_lines, None
            
        except Exception as e:
            error_msg = f"{service_name} bot error: {str(e)}"
            self.main_window.log_message(error_msg)
            return None, error_msg

    def wait_for_processing(self, processing_class_id, max_wait_time=300):
        """
        Wait for AI processing to complete
        
        Args:
            processing_class_id: YOLO class ID for processing indicator
            max_wait_time: Maximum wait time in seconds
        """
        screen_width, screen_height = pyautogui.size()
        
        # Check bottom 200px of screen
        processing_region = (
            0.5,  # left: 50% of screen
            (screen_height - 200) / screen_height,  # top: last 200px
            0.25,  # width: 25% of screen
            200 / screen_height  # height: 200px
        )
        
        elapsed_time = 0
        check_interval = 5
        
        while elapsed_time < max_wait_time:
            detection = self.detect_element(
                processing_class_id,
                region_ratio=processing_region,
                confidence=0.6,
                max_attempts=1,
                delay_between=0
            )
            
            if not detection:
                self.main_window.log_message("Processing completed")
                return True
            
            time.sleep(check_interval)
            elapsed_time += check_interval
            
            if elapsed_time % 30 == 0:
                self.main_window.log_message(f"Still processing... ({elapsed_time} seconds elapsed)")
        
        self.main_window.log_message("Warning: Maximum wait time reached")
        return False

    def ensure_scroll_to_bottom(self, action_icons_class_id, max_attempts=5):
        """
        Scroll to bottom and detect action icons
        
        Args:
            action_icons_class_id: YOLO class ID for action icons
            max_attempts: Maximum scroll attempts
            
        Returns:
            Detection result or None
        """
        screen_width, screen_height = pyautogui.size()
        
        for attempt in range(max_attempts):
            if not self.running:
                return None
            
            # Different focus strategies
            if attempt == 0:
                pyautogui.click(screen_width // 2, screen_height // 2)
            elif attempt == 1:
                pyautogui.click(screen_width // 2, screen_height * 2 // 3)
            elif attempt == 2:
                pyautogui.click(screen_width // 3, screen_height // 2)
            elif attempt == 3:
                pyautogui.doubleClick(screen_width // 2, screen_height // 2)
            else:
                pyautogui.click(screen_width // 2, screen_height // 2)
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'end')
                time.sleep(0.5)
            
            # Try scrolling
            if attempt < 4:
                time.sleep(0.3)
                pyautogui.press('end')
                time.sleep(0.5)
                pyautogui.press('end')
                time.sleep(0.5)
            
            # Check for action icons
            detection = self.detect_element(
                action_icons_class_id,
                region_ratio=None,
                confidence=0.6,
                max_attempts=2,
                delay_between=0.5
            )
            
            if detection:
                self.main_window.log_message(f"Scroll successful (attempt {attempt + 1})")
                return detection
            
            time.sleep(0.3)
        
        self.main_window.log_message(f"Failed to scroll to bottom after {max_attempts} attempts")
        return None

    def cleanup_chat(self, service_name, classes):
        """
        Cleanup chat after processing
        
        Args:
            service_name: AI service name
            classes: Class ID mapping for the service
        """
        try:
            self.main_window.log_message(f"Cleaning up {service_name} chat...")
            
            screen_width, screen_height = pyautogui.size()
            
            # Define top region for more button
            if service_name == "Perplexity":
                top_region = (0.5, 0, 0.5, 150 / screen_height)
            else:
                top_region = (0, 0, 0.5, 150 / screen_height)
            
            # Click more button
            more_detection = self.detect_element(
                classes['more_btn'],
                region_ratio=top_region,
                confidence=0.7,
                max_attempts=3
            )
            
            if more_detection:
                more_x, more_y, _, _ = more_detection
                pyautogui.click(more_x, more_y)
                time.sleep(0.5)
                
                # Click delete button
                delete_detection = self.detect_element(
                    classes['delete_btn'],
                    confidence=0.7,
                    max_attempts=3
                )
                
                if delete_detection:
                    delete_x, delete_y, _, _ = delete_detection
                    pyautogui.click(delete_x, delete_y)
                    time.sleep(0.5)
                    
                    # Click confirm button
                    confirm_detection = self.detect_element(
                        classes['confirm_btn'],
                        confidence=0.7,
                        max_attempts=3
                    )
                    
                    if confirm_detection:
                        confirm_x, confirm_y, _, _ = confirm_detection
                        pyautogui.click(confirm_x, confirm_y)
                        self.main_window.log_message(f"{service_name} chat deleted successfully")
                    else:
                        self.main_window.log_message("Failed to confirm deletion")
                else:
                    self.main_window.log_message("Failed to click delete button")
            else:
                self.main_window.log_message("Failed to click more button")
                
        except Exception as e:
            self.main_window.log_message(f"Cleanup error: {str(e)}")
