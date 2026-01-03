
import sys
import os

# Ensure jaraco modules are importable
try:
    import jaraco
    import jaraco.text
    import jaraco.functools
    import jaraco.context
    import jaraco.classes
    print("[HOOK] jaraco modules loaded successfully")
except ImportError as e:
    print(f"[HOOK ERROR] Failed to import jaraco: {e}")
