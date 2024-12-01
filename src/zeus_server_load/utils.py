import logging
import time
import os
import platform
import subprocess
import requests
import zipfile
from colorama import init, Fore, Style
from datetime import datetime


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
    start_time = datetime.now()
    while True:
        uptime = datetime.now() - start_time
        print(f"\n{Fore.CYAN}Zeus Server Load - Uptime: {str(uptime).split('.')[0]}{Style.RESET_ALL}")
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


def check_and_install_dependencies():
    """Check and install required dependencies."""
    try:
        # Check Google Chrome version
        chrome_version = get_chrome_version()
        log_success(f"Google Chrome version detected: {chrome_version}")

        # Check or install ChromeDriver
        if not os.path.exists("chromedriver/chromedriver"):
            log_info("ChromeDriver not found. Downloading...")
            download_chromedriver(chrome_version)
        else:
            log_success("ChromeDriver already exists.")
    except Exception as e:
        log_error(f"Dependency check failed: {e}")
        raise


def get_chrome_version():
    """Get the version of installed Google Chrome."""
    log_info("Checking Google Chrome version...")
    try:
        system = platform.system()
        if system == "Windows":
            command = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
            version = subprocess.check_output(command, shell=True).decode().strip()
            return version.split()[-1]
        elif system == "Darwin":  # macOS
            command = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version"
            version = subprocess.check_output(command, shell=True).decode().strip()
            return version.split()[-1]
        elif system == "Linux":
            command = "google-chrome --version"
            version = subprocess.check_output(command, shell=True).decode().strip()
            return version.split()[-1]
        else:
            raise Exception("Unsupported Operating System")
    except Exception as e:
        log_error(f"Could not detect Google Chrome version: {e}")
        raise


def download_chromedriver(chrome_version):
    """Download the ChromeDriver that matches the installed Google Chrome version."""
    try:
        log_info("Determining the correct ChromeDriver version...")
        major_version = chrome_version.split(".")[0]
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        latest_driver_version = requests.get(url).text.strip()

        system = platform.system().lower()
        if system == 'darwin':
            system = 'mac64'  # For macOS
        elif system == 'windows':
            system = 'win32'
        elif system == 'linux':
            system = 'linux64'
        else:
            raise Exception("Unsupported Operating System for ChromeDriver")

        driver_download_url = f"https://chromedriver.storage.googleapis.com/{latest_driver_version}/chromedriver_{system}.zip"
        log_info(f"Downloading ChromeDriver from: {driver_download_url}")

        response = requests.get(driver_download_url, stream=True)
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
