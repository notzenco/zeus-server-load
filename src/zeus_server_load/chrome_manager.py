import os
import subprocess
import logging

class ChromeManager:
    """Manages Chrome profiles and related actions."""

    def __init__(self, config_manager):
        """Initialize with a ConfigManager instance."""
        self.config_manager = config_manager
        self.bo6_url = "https://www.xbox.com/en-US/play/launch/call-of-duty-black-ops-6---cross-gen-bundle/9PF528M6CRHQ"


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
                    self.bo6_url,  # The URL to open
                    '--window-size=500,500',  # Set window size (adjust as needed)
                ]

                subprocess.Popen(cmd, shell=False)
                print(f"Opened Chrome profile using shortcut '{shortcut}'.")
                logging.info(f"Opened Chrome profile using shortcut '{shortcut}'.")
            except Exception as e:
                print(f"Failed to open shortcut '{shortcut}': {e}")
                logging.error(f"Failed to open shortcut '{shortcut}': {e}")


    def install_tampermonkey_script_in_all_profiles(self, script_url):
        """Open the user script URL in all profiles to prompt Tampermonkey installation."""
        shortcuts_path = self.config_manager.get_config('chrome_shortcuts_path')
        if not shortcuts_path:
            logging.warning("Chrome shortcuts path is not set. Cannot install script.")
            return

        if not os.path.isdir(shortcuts_path):
            logging.warning(f"The path '{shortcuts_path}' does not exist or is not a directory.")
            return

        # List all .lnk files in the directory
        shortcuts = [f for f in os.listdir(shortcuts_path) if f.endswith('.lnk')]
        if not shortcuts:
            logging.warning(f"No shortcut files (.lnk) found in '{shortcuts_path}'.")
            return

        logging.info(f"Opening script URL '{script_url}' in {len(shortcuts)} Chrome profiles.")

        for shortcut in shortcuts:
            shortcut_path = os.path.join(shortcuts_path, shortcut)
            try:
                # Build the command to open the shortcut with the script URL
                cmd = [
                    'cmd', '/c', 'start', '',  # Use cmd /c start to open the shortcut
                    shortcut_path,
                    script_url,
                    '--window-size=500,500',  # Set window size (adjust as needed)
                ]

                subprocess.Popen(cmd, shell=False)
                logging.info(f"Opened script URL in Chrome profile using shortcut '{shortcut}'.")
            except Exception as e:
                logging.error(f"Failed to open script URL with shortcut '{shortcut}': {e}")

        logging.info("Please confirm the script installation in each opened browser window.")
        """Open the Chrome extensions page with developer mode instructions."""
        try:
            import win32com.client
        except ImportError:
            logging.error("Required module 'pywin32' not installed. Please install it using 'pip install pywin32'.")
            return

        shortcuts_path = self.config_manager.get_config('chrome_shortcuts_path')
        if not shortcuts_path:
            logging.warning("Chrome shortcuts path is not set. Cannot open developer options.")
            return

        if not os.path.isdir(shortcuts_path):
            logging.warning(f"The path '{shortcuts_path}' does not exist or is not a directory.")
            return

        # List all .lnk files in the directory
        shortcuts = [f for f in os.listdir(shortcuts_path) if f.endswith('.lnk')]
        if not shortcuts:
            logging.warning(f"No shortcut files (.lnk) found in '{shortcuts_path}'.")
            return

        logging.info(f"Opening developer options in {len(shortcuts)} Chrome profiles.")

        shell = win32com.client.Dispatch("WScript.Shell")

        for shortcut in shortcuts:
            shortcut_path = os.path.join(shortcuts_path, shortcut)
            try:
                sc = shell.CreateShortCut(shortcut_path)
                # Extract the profile directory from the shortcut's arguments
                arguments = sc.Arguments
                profile_dir = None
                if arguments:
                    import re
                    match = re.search(r'--profile-directory=("[^"]+"|\S+)', arguments)
                    if match:
                        profile_dir = match.group(1).strip('"')
                if not profile_dir:
                    logging.warning(f"Could not determine profile directory from shortcut '{shortcut}'. Skipping.")
                    continue

                # Path to Chrome executable
                chrome_exe_path = sc.Targetpath

                if not os.path.isfile(chrome_exe_path):
                    logging.error(f"Chrome executable not found at '{chrome_exe_path}'.")
                    continue

                cmd = [
                    chrome_exe_path,
                    f'--profile-directory="{profile_dir}"',
                    'chrome://extensions/',
                    '--window-size=500,500',  # Set window size (adjust as needed)
                ]
                subprocess.Popen(cmd)
                logging.info(f"Opened developer options in Chrome profile '{profile_dir}'.")
            except Exception as e:
                logging.error(f"Failed to open developer options with shortcut '{shortcut}': {e}")

        logging.info("Please enable 'Developer mode' in each opened browser window.")



    def install_extension_on_all_profiles(self, extension_url):
        """Open the Chrome Web Store page of an extension in all profiles."""
        shortcuts_path = self.config_manager.get_config('chrome_shortcuts_path')
        if not shortcuts_path:
            logging.warning("Chrome shortcuts path is not set. Cannot install extension.")
            return

        if not os.path.isdir(shortcuts_path):
            logging.warning(f"The path '{shortcuts_path}' does not exist or is not a directory.")
            return

        # List all .lnk files in the directory
        shortcuts = [f for f in os.listdir(shortcuts_path) if f.endswith('.lnk')]
        if not shortcuts:
            logging.warning(f"No shortcut files (.lnk) found in '{shortcuts_path}'.")
            return

        logging.info(f"Opening extension page '{extension_url}' in {len(shortcuts)} Chrome profiles.")

        for shortcut in shortcuts:
            shortcut_path = os.path.join(shortcuts_path, shortcut)
            try:
                # Build the command to open the shortcut with the extension URL
                cmd = [
                    'cmd', '/c', 'start', '',  # Use cmd /c start to open the shortcut
                    shortcut_path,
                    extension_url,
                    '--window-size=500,500',  # Set window size (adjust as needed)
                ]

                subprocess.Popen(cmd, shell=False)
                logging.info(f"Opened extension page in Chrome profile using shortcut '{shortcut}'.")
            except Exception as e:
                logging.error(f"Failed to open extension page with shortcut '{shortcut}': {e}")

        logging.info("Please manually install the extension in each opened browser window.")