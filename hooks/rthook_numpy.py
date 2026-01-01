import sys
import os

# Remove numpy source directory from sys.path if present
# This prevents the "importing from source directory" error
paths_to_remove = []
for path in sys.path:
    if 'numpy' in path.lower() and os.path.isdir(path):
        # Check if this is a source directory (has setup.py or pyproject.toml)
        if os.path.exists(os.path.join(path, 'setup.py')) or \
                os.path.exists(os.path.join(path, 'pyproject.toml')):
            paths_to_remove.append(path)

for path in paths_to_remove:
    sys.path.remove(path)