# Project Conventions

## File Naming

### Python Files
- Use `snake_case` for all Python file names
- Example: `translation_processor.py`, `ai_api_handler.py`, `main_window.py`

### Folders
- Use `snake_case` for folder names
- Exception: Root-level folders may use PascalCase or descriptive names
- Example: `gui/`, `helper/`, `assets/`

### Config Files
- Use `snake_case` with descriptive names
- Example: `bot_settings.json`, `translate_prompt.xlsx`

### Asset Files
- UI template images: Use `snake_case` with descriptive names
- Example: `text_input_box.png`, `send_btn.png`, `is_processing.png`

---

## Component Structure

### GUI Classes (Tkinter)
```python
class ComponentName:
    """Brief description of the component"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window

        # Initialize variables
        self.init_variables()

        # Create content
        self.create_content()

        # Bind events (if needed)
        self.bind_variable_changes()

    def init_variables(self):
        """Initialize all tkinter variables"""
        self.var_name = tk.StringVar(value="default")

    def create_content(self):
        """Create GUI content"""
        pass
```

### Tab Classes
```python
class SomeTab:
    def __init__(self, parent, main_window):
        # Same pattern as above

    def get_settings(self):
        """Return current tab settings as dict"""
        return {'key': self.var.get()}

    def load_settings(self, settings):
        """Load settings into tab"""
        if 'key' in settings:
            self.var.set(settings['key'])
```

### Service/Handler Classes
```python
class ServiceHandler:
    """Handler for specific service"""

    def __init__(self, main_window):
        self.main_window = main_window
        # Initialize state

    def process_something(self, param1, param2):
        """Process description"""
        try:
            # Implementation
            self.main_window.log_message("Status message")
            return result, None
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.main_window.log_message(f"Error: {error_msg}")
            return None, error_msg
```

---

## Code Style

### General
- Follow PEP 8 style guide
- Maximum line length: 120 characters (soft limit)
- Use 4 spaces for indentation (no tabs)

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `TranslationProcessor`, `AIAPIHandler` |
| Functions/Methods | snake_case | `load_settings`, `process_with_api` |
| Variables | snake_case | `input_file`, `batch_size` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Private methods | _leading_underscore | `_update_progress_thread` |
| Tkinter variables | snake_case with suffix | `batch_size_var`, `ai_service` |

### String Formatting
- Use f-strings for string interpolation: `f"Processing {file_name}"`
- Use triple quotes for docstrings: `"""Description"""`

### Comments
- Docstrings for all public classes and methods
- Inline comments for complex logic
- Both English and Vietnamese comments are acceptable

---

## Import Order

Follow this order, separated by blank lines:

```python
# 1. Standard library imports
import os
import re
import json
import threading
from datetime import datetime

# 2. Third-party imports
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import requests

# 3. Local application imports
from gui.window_manager import WindowManager
from helper.translation_processor import TranslationProcessor
```

---

## Error Handling

### API Calls
```python
try:
    response = requests.post(url, json=payload, timeout=30)

    if response.status_code == 200:
        result = response.json()
        return result, None
    else:
        error_msg = f"API error - Status: {response.status_code}"
        if response.status_code in [401, 403, 429]:
            # Handle rate limiting or auth errors
            self.failed_keys.add(api_key)
        return None, error_msg

except requests.exceptions.Timeout:
    return None, "API timeout"
except Exception as e:
    return None, f"Exception: {str(e)}"
```

### File Operations
```python
try:
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame()
except Exception as e:
    self.main_window.log_message(f"Error reading file: {e}")
    df = pd.DataFrame()
```

---

## Threading

### Worker Thread Pattern
```python
def start_long_task(self):
    """Start task in background thread"""
    thread = threading.Thread(
        target=self._long_task_worker,
        daemon=True
    )
    thread.start()

def _long_task_worker(self):
    """Worker method running in background thread"""
    try:
        result = self.do_work()
        # Use root.after for thread-safe GUI update
        self.main_window.root.after(0, self.update_gui, result)
    except Exception as e:
        self.main_window.root.after(0, self.show_error, str(e))
```

### Thread-Safe Logging
```python
# From worker thread:
self.main_window.root.after(0, self.main_window.log_message, "Status message")

# Or using lambda:
self.root.after(0, lambda: self.status_section.set_progress(current, total))
```

---

## File I/O Patterns

### Reading CSV/Excel
```python
def read_input_file(file_path):
    """Read input file with format detection"""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, engine='openpyxl')
    else:
        df = pd.read_csv(file_path, encoding='utf-8')

    return df
```

### Writing CSV/Excel
```python
def save_results(df, output_path):
    """Save results with format detection"""
    _, ext = os.path.splitext(output_path)
    ext = ext.lower()

    if ext in ['.xlsx', '.xls']:
        df.to_excel(output_path, index=False, engine='openpyxl')
    else:
        df.to_csv(output_path, index=False, encoding='utf-8')
```

---

## GUI Patterns

### Layout (Grid)
```python
# Frame setup
frame = ttk.Frame(parent)
frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
frame.columnconfigure(1, weight=1)  # Make column 1 expandable

# Widget placement
ttk.Label(frame, text="Label:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
ttk.Entry(frame, textvariable=self.var).grid(row=0, column=1, sticky=(tk.W, tk.E))
```

### Variable Binding for Auto-Save
```python
def bind_variable_changes(self):
    """Bind variables to auto-save on change"""
    variables = [self.var1, self.var2, self.var3]

    for var in variables:
        var.trace('w', lambda *args: self.main_window.save_settings())
```

### Dialog Creation
```python
def open_dialog(self):
    """Open modal dialog"""
    dialog = tk.Toplevel(self.main_window.root)
    dialog.title("Dialog Title")
    dialog.transient(self.main_window.root)
    dialog.grab_set()

    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
```

---

## Testing Approach

### Manual Testing
- Test both API mode and web automation mode
- Test with different file formats (CSV, Excel)
- Test resume capability (stop and restart processing)
- Test error handling (invalid API keys, network errors)

### Debug Logging
```python
# Use log_message for user-visible logs
self.main_window.log_message(f"Processing batch {batch_num}/{total}")

# Use print for debug-only logs
print(f"Debug: {variable}")

# Use traceback for detailed error info
import traceback
self.main_window.log_message(traceback.format_exc())
```

---

## Configuration Pattern

### Settings Structure (bot_settings.json)
```json
{
  "window": {
    "width": 600,
    "height": 800,
    "x": 100,
    "y": 100
  },
  "translation": {
    "input_file": "",
    "output_dir": "",
    "start_id": "",
    "stop_id": ""
  },
  "processing": {
    "batch_size": "10",
    "prompt_type": "",
    "ai_service": "Gemini API",
    "mode": "automatic"
  },
  "processing.api_configs": {
    "Gemini API": {
      "keys": [],
      "max_tokens": 8192,
      "temperature": 0.7,
      "model": "gemini-2.5-flash-lite"
    }
  }
}
```

---

## Security Practices

### API Key Handling
- Never log full API keys
- Encrypt keys when storing: `key_encryption.py`
- Display masked keys in UI: `key[:10]}...`
- Remove from failed_keys set only after successful use

### Input Validation
- Validate file paths exist before processing
- Check for required columns in input files
- Sanitize user input before using in file paths
