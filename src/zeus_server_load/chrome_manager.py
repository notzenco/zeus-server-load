import os
import subprocess
import logging

class ChromeManager:
    """Manages Chrome profiles and related actions."""

    def __init__(self, config_manager):
        """Initialize with a ConfigManager instance."""
        self.config_manager = config_manager

    def open_all_chrome_profiles(self):
        """Open all Chrome profiles using shortcuts in the specified directory."""
        shortcuts_path = self.config_manager.get_config('chrome_shortcuts_path')
        if not shortcuts_path:
            print("Chrome shortcuts path is not set. Cannot open profiles.")
            logging.warning("Chrome shortcuts path is not set. Cannot open profiles.")
            return

        if not os.path.isdir(shortcuts_path):
            print(f"The path '{shortcuts_path}' does not exist or is not a directory")
            logging.warning(f"The path '{shortcuts_path}' does not exist or is not a directory.")
            return

        # List all .lnk files in the directory
        shortcuts = [f for f in os.listdir(shortcuts_path) if f.endswith('.lnk')]
        if not shortcuts:
            logging.warning(f"No shortcut files (.lnk) found in '{shortcuts_path}'.")
            return

        print(f"Found {len(shortcuts)} Chrome profile shortcuts. Opening all profiles...")
        logging.info(f"Found {len(shortcuts)} Chrome profile shortcuts. Opening all profiles...")

        for shortcut in shortcuts:
            shortcut_path = os.path.join(shortcuts_path, shortcut)
            try:
                # Build the command to open the shortcut
                cmd = [
                    'cmd', '/c', 'start', '',
                    shortcut_path,
                    'https://xbox.com/play',  # The URL to open
                    '--window-size=800,800',  # Set window size (adjust as needed)
                ]

                subprocess.Popen(cmd, shell=False)
                print(f"Opened Chrome profile using shortcut '{shortcut}'.")
                logging.info(f"Opened Chrome profile using shortcut '{shortcut}'.")
            except Exception as e:
                print(f"Failed to open shortcut '{shortcut}': {e}")
                logging.error(f"Failed to open shortcut '{shortcut}': {e}")
