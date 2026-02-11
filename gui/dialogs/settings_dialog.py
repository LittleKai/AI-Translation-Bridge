import tkinter as tk
from tkinter import ttk, messagebox
import threading
from version import __version__


class SettingsDialog:
    """Settings dialog window"""

    def __init__(self, main_window):
        self.main_window = main_window

        # Create dialog window
        self.window = tk.Toplevel(main_window.root)
        self.window.title("Settings")
        self.window.resizable(False, False)

        # Make dialog modal
        self.window.attributes('-topmost', True)
        self.window.transient(main_window.root)
        self.window.grab_set()

        # Setup UI
        self.setup_ui()

        # Center window
        self.center_window()

        # Bind events
        self.window.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def setup_ui(self):
        """Setup the user interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Application Key section
        key_frame = ttk.LabelFrame(main_frame, text="Application Key", padding="10")
        key_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(key_frame, text="Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.key_entry = ttk.Entry(key_frame, textvariable=self.main_window.app_key_var, width=30)
        self.key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(key_frame, text="Enter your application key",
                  font=("Arial", 9), foreground="gray").grid(row=1, column=1, sticky=tk.W, pady=(5, 0))

        # Updates section
        update_frame = ttk.LabelFrame(main_frame, text="Updates", padding="10")
        update_frame.pack(fill=tk.X, pady=(0, 10))
        update_frame.columnconfigure(1, weight=1)

        ttk.Label(update_frame, text=f"Current version: v{__version__}",
                  font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.update_btn = ttk.Button(update_frame, text="Check for Updates",
                                     command=self.check_for_updates)
        self.update_btn.grid(row=0, column=1, sticky=tk.E)

        self.update_status = ttk.Label(update_frame, text="", font=("Arial", 9))
        self.update_status.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side=tk.RIGHT)

    def check_for_updates(self):
        """Check for updates in background thread"""
        self.update_btn.config(state="disabled")
        self.update_status.config(text="Checking...", foreground="blue")

        def do_check():
            from helper.updater import AppUpdater
            updater = AppUpdater(self.main_window)
            has_update, latest_version, notes, download_url = updater.check_for_update()

            def show_result():
                self.update_btn.config(state="normal")

                if has_update:
                    self.update_status.config(
                        text=f"v{latest_version} available!",
                        foreground="green"
                    )
                    # Ask user to confirm update
                    msg = (f"New version v{latest_version} is available!\n\n"
                           f"{notes[:500]}\n\n"
                           f"Update now?")
                    if messagebox.askyesno("Update Available", msg, parent=self.window):
                        self.apply_update(updater, download_url)
                else:
                    self.update_status.config(text=notes, foreground="gray")

            self.window.after(0, show_result)

        threading.Thread(target=do_check, daemon=True).start()

    def apply_update(self, updater, download_url):
        """Download and apply the update"""
        self.update_btn.config(state="disabled")

        def progress(msg):
            self.window.after(0, lambda: self.update_status.config(text=msg, foreground="blue"))

        def do_update():
            success, message = updater.download_and_apply(download_url, progress)

            def handle_result():
                if success:
                    # Close the entire application - bat script will restart
                    self.main_window.on_closing()
                else:
                    self.update_status.config(text=message, foreground="red")
                    self.update_btn.config(state="normal")
                    messagebox.showerror("Update Failed", message, parent=self.window)

            self.window.after(0, handle_result)

        threading.Thread(target=do_update, daemon=True).start()

    def on_save(self):
        """Save settings and close"""
        # Save settings
        self.main_window.save_settings()

        # Re-validate key
        self.main_window.check_key_validation()

        messagebox.showinfo("Success", "Settings saved successfully!")
        self.window.destroy()

    def on_cancel(self):
        """Close without saving"""
        self.window.destroy()

    def center_window(self):
        """Center the window on parent"""
        self.window.update_idletasks()

        width = 400
        height = 280

        parent_x = self.main_window.root.winfo_x()
        parent_y = self.main_window.root.winfo_y()
        parent_width = self.main_window.root.winfo_width()
        parent_height = self.main_window.root.winfo_height()

        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)

        self.window.geometry(f"{width}x{height}+{x}+{y}")
