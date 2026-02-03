# Instructions for Claude Code

## Session Start Checklist

1. **Read PROJECT_SUMMARY.md first** - Get current project state
2. **Check recent history** in `.claude/history/` - Understand recent changes
3. **Review CONVENTIONS.md** if making code changes

---

## Before Making Changes

### Required Steps
1. Read relevant files before modifying
2. Understand the component's role in the architecture
3. Check if change affects other components (see dependency tree in PROJECT_SUMMARY.md)
4. Consider both API mode and web automation mode impact

### Critical Files to Check
- `gui/main_window.py` - Main orchestration
- `helper/translation_processor.py` - Core translation logic
- `helper/ai_api_handler.py` - API integrations
- `bot_settings.json` - Configuration schema

---

## After Making Changes

### Required Documentation Updates
1. Update `PROJECT_SUMMARY.md`:
   - Update "Last Updated" timestamp
   - Add to Section 7 "Recent Changes"
   - Update Section 4 "Active Features" if applicable
   - Update Section 5 "Known Issues" if applicable

2. Create history entry:
   - File: `.claude/history/YYYY-MM-DD_HH-MM.md`
   - Use template from `.claude/templates/change-log-template.md`

---

## Code Change Guidelines

### GUI Changes
- Test that window resizing works correctly
- Ensure compact mode still functions
- Verify auto-save triggers on variable changes
- Check thread safety for background operations

### API Integration Changes
- Test error handling for all HTTP status codes
- Ensure API key rotation works
- Verify timeout handling
- Log appropriate messages for debugging

### Translation Logic Changes
- Test batch processing with different sizes
- Verify resume capability (stop and restart)
- Check output file format (both CSV and Excel)
- Test with edge cases (empty batches, missing IDs)

### File Processing Changes
- Support both CSV and Excel formats
- Handle encoding issues (UTF-8, Shift-JIS, etc.)
- Preserve existing data when updating files

---

## Common Tasks Reference

### Adding a New AI Service
1. Add API handler method in `helper/ai_api_handler.py`
2. Add service config in `gui/tabs/processing_tab.py` → `api_configs`
3. Add service to dropdown list in `create_ai_service_section()`
4. Add case in `helper/translation_processor.py` → `process_with_api()`
5. Create UI templates folder in `assets/` if web automation needed

### Adding a New Tab
1. Create tab class in `gui/tabs/new_tab.py`
2. Import and add in `gui/main_window.py` → `create_tabbed_section()`
3. Add settings handling in `gui/window_manager.py`
4. Update `bot_settings.json` schema

### Modifying Settings Schema
1. Update `gui/window_manager.py` → `load_settings()` and `save_settings()`
2. Add migration logic for existing settings files
3. Document new fields in PROJECT_SUMMARY.md Section 9

---

## Testing Checklist

Before completing a session with code changes:

- [ ] Application starts without errors
- [ ] Settings are saved and loaded correctly
- [ ] API mode works (if modified)
- [ ] Web automation mode works (if modified)
- [ ] Keyboard shortcuts work (Shift+F1, Shift+F3)
- [ ] Compact mode transitions correctly
- [ ] Progress display updates correctly

---

## Communication Style

### Log Messages
```python
# Informational
self.main_window.log_message(f"Processing batch {current}/{total}")

# Success
self.main_window.log_message("Translation completed successfully")

# Warning
self.main_window.log_message(f"Warning: {message}")

# Error
self.main_window.log_message(f"Error: {error_message}")
```

### User Dialogs
```python
# Information
messagebox.showinfo("Title", "Message")

# Warning
messagebox.showwarning("Warning", "Message")

# Error
messagebox.showerror("Error", "Message")

# Confirmation
result = messagebox.askyesno("Confirm", "Are you sure?")
```

---

## Quick Reference

### Key Classes
| Class | File | Purpose |
|-------|------|---------|
| AITranslationBridgeGUI | main_window.py | Main application window |
| WindowManager | window_manager.py | Settings persistence |
| TranslationProcessor | translation_processor.py | Translation workflow |
| AIAPIHandler | ai_api_handler.py | API calls |
| BotController | bot_controller.py | Web automation control |
| PromptHelper | prompt_helper.py | Prompt management |

### Key Methods
| Method | Class | Purpose |
|--------|-------|---------|
| `start_bot()` | AITranslationBridgeGUI | Start processing |
| `stop_bot()` | AITranslationBridgeGUI | Stop processing |
| `log_message()` | AITranslationBridgeGUI | Add log entry |
| `save_settings()` | WindowManager | Persist settings |
| `process_with_api()` | TranslationProcessor | Run API translation |
| `call_gemini_api()` | AIAPIHandler | Call Gemini API |

---

## Troubleshooting

### Common Issues

**Settings not saving:**
- Check variable trace bindings
- Verify JSON serialization

**GUI freezing:**
- Ensure long operations run in daemon threads
- Use `root.after(0, callback)` for GUI updates

**API errors:**
- Check API key validity
- Verify model name is correct
- Check rate limiting (429 errors)

**File encoding issues:**
- Use `encoding='utf-8'` for CSV operations
- Try detect_encoding() for unknown files
