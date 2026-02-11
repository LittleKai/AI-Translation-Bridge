import os
import sys
import tempfile
import zipfile
import subprocess
import threading
import requests
from version import __version__


class AppUpdater:
    """Handles checking for updates and applying them from GitHub releases"""

    GITHUB_REPO = "LittleKai/AI-Translation-Bridge"
    PROTECTED_FILES = ['bot_settings.json', '.key_store']

    def __init__(self, main_window):
        self.main_window = main_window

    def get_app_dir(self):
        """Get the application directory"""
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            return os.path.dirname(sys.executable)
        else:
            # Running as script
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def check_for_update(self):
        """Check GitHub for latest release.
        Returns (has_update, latest_version, release_notes, download_url)
        """
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=10)

            if response.status_code == 404:
                return False, __version__, "No releases found", None

            if response.status_code != 200:
                return False, __version__, f"GitHub API error: {response.status_code}", None

            data = response.json()
            tag = data.get('tag_name', '')
            latest_version = tag.lstrip('v')

            # Compare versions
            if not self._is_newer(latest_version, __version__):
                return False, latest_version, "Already up to date", None

            # Find zip asset
            download_url = None
            for asset in data.get('assets', []):
                if asset['name'].endswith('.zip'):
                    download_url = asset['browser_download_url']
                    break

            if not download_url:
                return False, latest_version, "Update available but no zip asset found", None

            release_notes = data.get('body', '') or 'No release notes'
            return True, latest_version, release_notes, download_url

        except requests.exceptions.Timeout:
            return False, __version__, "Connection timed out", None
        except requests.exceptions.ConnectionError:
            return False, __version__, "No internet connection", None
        except Exception as e:
            return False, __version__, f"Error checking for updates: {e}", None

    def _is_newer(self, latest, current):
        """Compare version strings (e.g. '0.0.3' > '0.0.2')"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            return latest_parts > current_parts
        except (ValueError, AttributeError):
            return False

    def download_and_apply(self, download_url, progress_callback=None):
        """Download update zip and apply via batch script.
        Returns (success, message)
        """
        try:
            # Setup temp directory
            update_dir = os.path.join(tempfile.gettempdir(), 'aibridge_update')
            if os.path.exists(update_dir):
                import shutil
                shutil.rmtree(update_dir)
            os.makedirs(update_dir)

            zip_path = os.path.join(update_dir, 'update.zip')
            staging_dir = os.path.join(update_dir, 'staging')

            # Download zip with progress
            if progress_callback:
                progress_callback("Downloading update...")

            response = requests.get(download_url, stream=True, timeout=120)
            if response.status_code != 200:
                return False, f"Download failed: HTTP {response.status_code}"

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        pct = int(downloaded * 100 / total_size)
                        progress_callback(f"Downloading... {pct}%")

            # Extract zip
            if progress_callback:
                progress_callback("Extracting update...")

            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(staging_dir)

            # Check if files are nested in a subfolder
            staging_contents = os.listdir(staging_dir)
            if len(staging_contents) == 1 and os.path.isdir(os.path.join(staging_dir, staging_contents[0])):
                # Files are nested - use the subfolder as staging
                staging_dir = os.path.join(staging_dir, staging_contents[0])

            # Get app directory
            app_dir = self.get_app_dir()

            # Find exe name
            exe_name = "AI Translation Bridge.exe"
            if getattr(sys, 'frozen', False):
                exe_name = os.path.basename(sys.executable)

            # Build protected files exclusion for robocopy
            xf_args = " ".join(f'"{f}"' for f in self.PROTECTED_FILES)

            # Write update batch script
            bat_path = os.path.join(app_dir, '_update.bat')
            bat_content = f'''@echo off
chcp 65001 >nul
echo Updating AI Translation Bridge...
echo Waiting for application to close...
timeout /t 3 /nobreak >nul
echo Copying new files...
robocopy "{staging_dir}" "{app_dir}" /E /NFL /NDL /NJH /NJS /XF {xf_args} /XD __pycache__
echo Cleaning up...
rmdir /s /q "{update_dir}"
echo Starting application...
start "" "{os.path.join(app_dir, exe_name)}"
del "%~f0"
'''
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)

            if progress_callback:
                progress_callback("Restarting application...")

            # Launch batch script (detached from current process)
            subprocess.Popen(
                ['cmd', '/c', bat_path],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                close_fds=True
            )

            return True, "Update downloaded. Application will restart."

        except zipfile.BadZipFile:
            return False, "Downloaded file is not a valid zip"
        except Exception as e:
            return False, f"Update failed: {e}"
