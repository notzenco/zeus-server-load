import logging
import time
import os
import platform
import subprocess
import requests
import zipfile
from colorama import init, Fore, Style
from datetime import datetime
import ctypes
import sys
import os
import vgamepad as vg
import subprocess
import webbrowser



def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        filename='server.log',
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )


def log_info(message):
    """Log informational messages."""
    logging.info(message)


def log_error(message):
    """Log error messages."""
    logging.error(message)


def log_success(message):
    """Log success messages."""
    logging.info(message)


def display_menu(server):
    """Display the menu-driven interface."""
    init(autoreset=True)
    while True:
        print(f"{Fore.BLUE}Select an option:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1. Add HWID{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. Tail Logs{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. Exit{Style.RESET_ALL}")
        choice = input(f"{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        if choice == '1':
            hwid = input("Enter HWID to add: ")
            if server.hwid_manager.add_hwid(hwid):
                print(f"{Fore.GREEN}HWID '{hwid}' added successfully.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}HWID '{hwid}' is already in the whitelist.{Style.RESET_ALL}")
        elif choice == '2':
            tail_logs()
        elif choice == '3':
            print("Exiting...")
            server.shutdown()
            break
        else:
            print("Invalid choice. Please try again.")


def tail_logs():
    """Tail the server logs."""
    log_file = 'server.log'
    if not os.path.exists(log_file):
        print("Log file does not exist.")
        return
    print(f"Tailing logs from {log_file}. Press Ctrl+C to exit.")
    try:
        with open(log_file, 'r') as f:
            # Move to the end of the file
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                print(line, end='')
    except KeyboardInterrupt:
        print("\nExiting log tail.")


def setup_chrome_driver():
    """Set up ChromeDriver using webdriver-manager."""
    try:
        log_info("Setting up ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        log_success("ChromeDriver setup complete.")
        return driver
    except Exception as e:
        log_error(f"Failed to set up ChromeDriver: {e}")
        raise





    """Set up ChromeDriver using webdriver-manager."""
    try:
        log_info("Setting up ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        log_success("ChromeDriver setup complete.")
        return driver
    except Exception as e:
        log_error(f"Failed to set up ChromeDriver: {e}")
        raise
    """Download the ChromeDriver that matches the installed Google Chrome version."""
    try:
        log_info("Determining the correct ChromeDriver version...")

        # Extract the full prefix of the Chrome version (e.g., '72.0.3626')
        version_prefix = ".".join(chrome_version.split(".")[:3])
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version_prefix}"
        
        log_info(f"Fetching the latest ChromeDriver version for Chrome {version_prefix}...")
        response = requests.get(url)
        if response.status_code != 200 or "Error" in response.text:
            raise Exception(f"Failed to retrieve the latest ChromeDriver version for Chrome {version_prefix}")
        
        latest_driver_version = response.text.strip()

        # Detect the system platform and architecture
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        # Map OS and architecture to ChromeDriver download filenames
        if system == "windows":
            if "arm" in arch or "aarch64" in arch:
                system = "win_arm64"
            else:
                system = "win32"
        elif system == "linux":
            if "arm" in arch or "aarch64" in arch:
                system = "linux_arm64"
            else:
                system = "linux64"
        elif system == "darwin":  # macOS
            if "arm" in arch or "aarch64" in arch:
                system = "mac_arm64"
            else:
                system = "mac64"
        else:
            raise Exception("Unsupported Operating System for ChromeDriver")

        driver_download_url = f"https://chromedriver.storage.googleapis.com/{latest_driver_version}/chromedriver_{system}.zip"
        log_info(f"Downloading ChromeDriver from: {driver_download_url}")

        # Download and save ChromeDriver
        response = requests.get(driver_download_url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Failed to download ChromeDriver from {driver_download_url}")
        
        zip_path = "chromedriver.zip"
        with open(zip_path, "wb") as file:
            file.write(response.content)

        # Extract the downloaded zip
        log_info("Extracting ChromeDriver...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("chromedriver")

        # Clean up
        os.remove(zip_path)
        chromedriver_path = os.path.abspath("chromedriver/chromedriver")
        log_success(f"ChromeDriver downloaded and available at: {chromedriver_path}")
        return chromedriver_path
    except Exception as e:
        log_error(f"Failed to download ChromeDriver: {e}")
        raise

    """Download the ChromeDriver that matches the installed Google Chrome version."""
    try:
        log_info("Determining the correct ChromeDriver version...")
        major_version = chrome_version.split(".")[0]
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        print(url)
        
        log_info(f"Fetching the latest ChromeDriver version for Chrome {major_version}...")
        response = requests.get(url)
        if response.status_code != 200 or "Error" in response.text:
            raise Exception(f"Failed to retrieve the latest ChromeDriver version for Chrome {major_version}")
        
        latest_driver_version = response.text.strip()

        system = platform.system().lower()
        arch = platform.machine().lower()
        
        # Map OS and architecture to ChromeDriver download filenames
        if system == "windows":
            if "arm" in arch or "aarch64" in arch:
                system = "win_arm64"
            else:
                system = "win32"
        elif system == "linux":
            if "arm" in arch or "aarch64" in arch:
                system = "linux_arm64"
            else:
                system = "linux64"
        elif system == "darwin":  # macOS
            if "arm" in arch or "aarch64" in arch:
                system = "mac_arm64"
            else:
                system = "mac64"
        else:
            raise Exception("Unsupported Operating System for ChromeDriver")

        driver_download_url = f"https://chromedriver.storage.googleapis.com/{latest_driver_version}/chromedriver_{system}.zip"
        log_info(f"Downloading ChromeDriver from: {driver_download_url}")

        # Download and save ChromeDriver
        response = requests.get(driver_download_url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Failed to download ChromeDriver from {driver_download_url}")
        
        zip_path = "chromedriver.zip"
        with open(zip_path, "wb") as file:
            file.write(response.content)

        # Extract the downloaded zip
        log_info("Extracting ChromeDriver...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("chromedriver")

        # Clean up
        os.remove(zip_path)
        chromedriver_path = os.path.abspath("chromedriver/chromedriver")
        log_success(f"ChromeDriver downloaded and available at: {chromedriver_path}")
        return chromedriver_path
    except Exception as e:
        log_error(f"Failed to download ChromeDriver: {e}")
        raise


def check_vigem_bus_driver():
    """Check if ViGEmBus driver is installed and operational on Windows."""
    if sys.platform != "win32":
        logging.error("ViGEmBus driver check is only applicable on Windows.")
        return False

    try:
        # Attempt to create a gamepad instance
        from zeus_server_load.server import CommandServer
        logging.info("ViGEmBus driver is installed and operational.")
        return True
    except Exception as e:
        logging.error(f"An unexpected error occurred while checking ViGEmBus driver: {e}")
        user_input = input("Would you like to download and install it now? (y/n): ")
        if user_input.lower() == 'y':
            download_and_install_vigem_bus()
        else:
            print("Cannot proceed without ViGEmBus driver. Exiting.")
            sys.exit(1)
        return False

def download_and_install_vigem_bus():
    """Launch the ViGEmBus driver installer included with the package."""
    try:
        installer_path = os.path.join(os.path.dirname(__file__), "ViGEmBus_Setup_1.22.0.exe")

        if not os.path.exists(installer_path):
            print("ViGEmBus installer not found in package.")
            logging.error("ViGEmBus installer not found in package.")
            sys.exit(1)

        print("Launching ViGEmBus installer...")
        logging.info(f"Launching ViGEmBus installer from {installer_path}")
        subprocess.run([installer_path], check=True)

        print("ViGEmBus installer launched. Please follow the on-screen instructions to complete the installation.")
        logging.info("ViGEmBus installer launched.")

        # After installation, check again
        input("Press Enter after you have completed the installation to continue...")
        if not check_vigem_bus_driver():
            print("ViGEmBus driver still not detected. Exiting.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to launch ViGEmBus installer: {e}")
        print(f"An error occurred while launching the installer: {e}")
        print("Please download and install the ViGEmBus driver manually from https://github.com/ViGEm/ViGEmBus/releases")
        sys.exit(1)
