# Project Summary
**Last Updated:** 2026-01-23 (Initial Setup)
**Updated By:** Claude Code Initial Setup

---

## 1. Project Overview
- **Name:** AI Translation Bridge
- **Type:** Desktop GUI Application (Windows)
- **Purpose:** Automated AI-powered translation and document processing platform
- **Tech Stack:** Python 3.10+, Tkinter, pandas, OpenCV, PyTorch/YOLO
- **i18n:** Supports Japanese (JP), Chinese (CN), Korean (KR) language detection
- **Deployment:** PyInstaller executable for Windows

---

## 2. Current Architecture

### File Structure (Key Files Only)
```
AI_Translation_Bridge/
├── main.py                    # Entry point - creates AITranslationBridgeGUI
├── builder.py                 # PyInstaller build script
├── key_validator.py           # App key validation via Google Docs
├── bot_settings.json          # Persistent configuration file
├── requirements.txt           # Python dependencies
│
├── gui/                       # GUI Layer (Tkinter)
│   ├── main_window.py         # Main window class (AITranslationBridgeGUI)
│   ├── window_manager.py      # Window position & settings persistence
│   ├── bot_controller.py      # Bot automation workflow controller
│   ├── components/
│   │   ├── log_section.py     # Activity log display widget
│   │   └── status_section.py  # Progress & key status indicator
│   ├── tabs/
│   │   ├── translation_tab.py # Input/output file & ID range settings
│   │   ├── processing_tab.py  # Batch size, AI service, model, API keys
│   │   └── converter_tab.py   # TXT/DOCX/EPUB → CSV/Excel converter
│   └── dialogs/
│       ├── api_settings_dialog.py  # API key management
│       ├── prompt_dialog.py        # Prompt configuration
│       └── settings_dialog.py      # General settings
│
├── helper/                    # Business Logic Layer
│   ├── translation_processor.py  # Translation workflow orchestration
│   ├── ai_api_handler.py         # Direct API calls (Gemini, ChatGPT, Claude, Grok)
│   ├── web_bot_services.py       # Web automation (pyautogui + image matching)
│   ├── yolo_web_bot_services.py  # YOLO-based web automation
│   ├── novel_converter.py        # Document conversion (TXT/DOCX/EPUB → CSV)
│   ├── prompt_helper.py          # Prompt loading & language detection
│   ├── click_handler.py          # Screen automation helper
│   ├── recognizer.py             # Template matching (OpenCV)
│   └── key_encryption.py         # Fernet cipher for API key encryption
│
├── assets/                    # Resources
│   ├── icon.ico              # Application icon
│   ├── translate_prompt.xlsx # Translation prompts database
│   ├── Perplexity/           # UI templates for Perplexity automation
│   ├── Claude/               # UI templates for Claude automation
│   ├── ChatGPT/              # UI templates for ChatGPT automation
│   ├── Gemini/               # UI templates for Gemini automation
│   └── Grok/                 # UI templates for Grok automation
│
├── hooks/                     # PyInstaller hooks
└── releases/                  # Compiled executables
```

### Component Dependencies
```
main.py
    └── gui/main_window.py (AITranslationBridgeGUI)
            ├── gui/window_manager.py (WindowManager)
            ├── gui/bot_controller.py (BotController)
            ├── helper/translation_processor.py (TranslationProcessor)
            │       ├── helper/ai_api_handler.py (AIAPIHandler)
            │       └── helper/prompt_helper.py (PromptHelper)
            ├── gui/components/status_section.py (StatusSection)
            ├── gui/components/log_section.py (LogSection)
            ├── gui/tabs/translation_tab.py (TranslationTab)
            ├── gui/tabs/processing_tab.py (ProcessingTab)
            └── gui/tabs/converter_tab.py (ConverterTab)
```

---

## 3. Key Decisions & Patterns

### State Management
- **Settings Persistence:** JSON file (`bot_settings.json`) stores all user preferences
- **Variable Tracing:** Tkinter `StringVar` with `trace('w', callback)` for auto-save
- **Progress Tracking:** File-based tracking via output CSV/Excel files
- **Session State:** `is_running`, `key_valid` flags on main window

### Styling Approach
- **Framework:** Tkinter with `ttk` themed widgets
- **Layout:** Grid layout for main sections, Pack for simple containers
- **Font:** Arial (default), configurable sizes
- **Colors:** Status colors (green, orange, red) for visual feedback

### Threading Pattern
- Main thread: Tkinter GUI event loop
- Worker threads: API calls, web automation, file processing (daemon threads)
- Thread-safe logging: `root.after(0, callback)` for UI updates from worker threads

### API Integration Pattern
- **Direct API Mode:** `AIAPIHandler` with methods per service (Gemini, ChatGPT, Claude, Grok)
- **Web Automation Mode:** `WebBotServices` using pyautogui + template matching
- **Key Rotation:** Random selection from available API keys, failed keys tracked
- **Error Handling:** HTTP status codes 401, 403, 429 mark keys as failed

### Document Processing Pattern
- **Input:** CSV/Excel with 'id' and 'text' columns
- **Output:** CSV/Excel with 'id', 'raw', 'edit', 'status' columns
- **Batch Processing:** Configurable batch size (default: 10)
- **Resume Capability:** Skips already-processed IDs on restart

---

## 4. Active Features & Status

| Feature | Status | Files Involved | Notes |
|---------|--------|----------------|-------|
| Gemini API Translation | ✅ | ai_api_handler.py, translation_processor.py | Fully working |
| ChatGPT API Translation | ✅ | ai_api_handler.py, translation_processor.py | Fully working |
| Claude API Translation | ✅ | ai_api_handler.py, translation_processor.py | Fully working |
| Grok API Translation | ✅ | ai_api_handler.py, translation_processor.py | Fully working |
| Perplexity Web Automation | ✅ | web_bot_services.py, bot_controller.py | Template matching |
| Manual Mode | ✅ | processing_tab.py | Copy/Paste workflow |
| Document Converter | ✅ | novel_converter.py, converter_tab.py | TXT/DOCX/EPUB support |
| EPUB Ruby Handling | ✅ | novel_converter.py | Japanese furigana |
| API Key Encryption | ✅ | key_encryption.py | Fernet cipher |
| App Key Validation | ✅ | key_validator.py | Google Docs check |
| Keyboard Shortcuts | ✅ | main_window.py | Shift+F1/F3 |
| Compact Mode | ✅ | main_window.py | Auto during processing |

---

## 5. Known Issues & TODOs

### High Priority
- [ ] No known critical issues

### Medium Priority
- [ ] Grok API not fully tested (configured but usage limited)
- [ ] YOLO web bot services may need model updates

### Low Priority
- [ ] Add more AI model options as they become available
- [ ] Consider adding batch progress persistence for crash recovery

---

## 6. Important Context for Claude

### When making changes:
1. Always update this file's "Last Updated" timestamp
2. Create new history entry in `.claude/history/`
3. Follow naming conventions in CONVENTIONS.md
4. Test with both API mode and web automation mode if modifying translation logic
5. Ensure thread safety when modifying GUI-related code

### Critical Files (read before major changes):
- `gui/main_window.py` - Central orchestration, all components connected here
- `helper/translation_processor.py` - Core translation logic and batch processing
- `helper/ai_api_handler.py` - All API integrations
- `helper/prompt_helper.py` - Prompt loading and language detection
- `bot_settings.json` - Configuration structure (don't break schema)

### Architecture Rules:
- GUI components should NOT directly call APIs - use TranslationProcessor or BotController
- All file I/O should handle both CSV and Excel formats
- API keys must be encrypted when stored
- Use `root.after(0, callback)` for thread-safe GUI updates

---

## 7. Recent Changes (Last 3 Sessions)

1. **2026-01-23** - Initial project documentation setup by Claude Code

---

## 8. Quick Commands
```bash
# Development - Run application
python main.py

# Build executable
python builder.py

# Install dependencies
pip install -r requirements.txt

# Install dependencies (with GPU support)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## 9. AI Services Configuration

### API Services (Direct Integration)
| Service | Base URL | Auth Header |
|---------|----------|-------------|
| Gemini API | generativelanguage.googleapis.com | Query param `key=` |
| ChatGPT API | api.openai.com | Bearer token |
| Claude API | api.anthropic.com | x-api-key header |
| Grok API | api.x.ai | Bearer token |

### Web Automation Services
| Service | Template Folder | Status |
|---------|-----------------|--------|
| Perplexity | assets/Perplexity/ | Active |
| Claude | assets/Claude/ | Available |
| ChatGPT | assets/ChatGPT/ | Available |
| Gemini | assets/Gemini/ | Available |
| Grok | assets/Grok/ | Available |

---

**NOTE TO CLAUDE CODE:**
Read this file FIRST before making any changes.
Update Section 4, 5, 7 after each session.
Create history entry with details of changes made.
