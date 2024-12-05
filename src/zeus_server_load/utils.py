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
import socket



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


def get_local_ip():
    """Get the local IPv4 address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't need to be a reachable address
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_public_ip():
    """Get the public IPv4 address using multiple services."""
    services = [
        'https://api.ipify.org',
        'https://ifconfig.me/ip',
        'https://checkip.amazonaws.com'
    ]
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                return ip
        except requests.RequestException:
            continue
    logging.error("Failed to retrieve public IP from all services.")
    return None


def display_menu(server, config_manager, chrome_manager):
    """Display the menu-driven interface."""
    init(autoreset=True)
    while True:
        # Clear the screen for better readability
        if os.name == 'nt':  # For Windows
            os.system('cls')
        else:
            os.system('clear')

        # Get the public and local IP addresses
        public_ip = get_public_ip()
        local_ip = get_local_ip()

        # Display the header and IP addresses
        print(f"{Fore.CYAN}[Zeus Server Script CoDBo6]{Style.RESET_ALL}")
        if public_ip:
            print(f"The lobby manager can connect to this with Public IP: {Fore.GREEN}{public_ip}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Unable to retrieve public IP address.{Style.RESET_ALL}")
            print("Please ensure the server has internet access.")

        print(f"The lobby manager can connect to this with Local IP: {Fore.YELLOW}{local_ip}{Style.RESET_ALL}")

        # Display the menu options
        print(f"{Fore.BLUE}Select an option:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1. Add HWID{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. Delete HWID{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. Set Chrome Shortcuts Path{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}4. Open All Chrome Profiles{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}5. Tail Logs{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}6. Exit{Style.RESET_ALL}")
        choice = input(f"{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")

        if choice == '1':
            hwid = input("Enter HWID to add: ")
            if server.hwid_manager.add_hwid(hwid):
                print(f"{Fore.GREEN}HWID '{hwid}' added successfully.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}HWID '{hwid}' is already in the whitelist.{Style.RESET_ALL}")
            input("Press Enter to continue...")
        elif choice == '2':
            delete_hwid(server.hwid_manager)
        elif choice == '3':
            set_chrome_shortcuts_path(config_manager)
        elif choice == '4':
            chrome_manager.open_all_chrome_profiles()
            print("All Chrome profiles have been opened.")
            input("Press Enter to continue...")
        elif choice == '5':
            tail_logs()
        elif choice == '6':
            print("Exiting...")
            server.shutdown()
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")
    """Display the menu-driven interface."""
    init(autoreset=True)
    while True:
        if os.name == 'nt':  # For Windows
           os.system('cls')
        else:
            os.system('clear')
        print(f"{Fore.BLUE}Select an option:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1. Add HWID{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. Delete HWID{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. Set Chrome Shortcuts Path{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}4. Tail Logs{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}5. Exit{Style.RESET_ALL}")
        choice = input(f"{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        if choice == '1':
            hwid = input("Enter HWID to add: ")
            if server.hwid_manager.add_hwid(hwid):
                print(f"{Fore.GREEN}HWID '{hwid}' added successfully.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}HWID '{hwid}' is already in the whitelist.{Style.RESET_ALL}")
        elif choice == '2':
            delete_hwid(server.hwid_manager)
        elif choice == '3':
            set_chrome_shortcuts_path(config_manager)
        elif choice == '4':
            chrome_manager.open_all_chrome_profiles()
            print("All Chrome profiles have been opened.")
            input("Press Enter to continue...")
        elif choice == '5':
            tail_logs()
        elif choice == '6':
            print("Exiting...")
            server.shutdown()
            break
        else:
            print("Invalid choice. Please try again.")


def set_chrome_shortcuts_path(config_manager):
    """Set or update the Chrome shortcuts location or path."""
    existing_path = config_manager.get_config('chrome_shortcuts_path')
    if existing_path:
        print(f"{Fore.BLUE}Existing Chrome Shortcuts Path:{Style.RESET_ALL} {existing_path}")
    else:
        print(f"{Fore.YELLOW}No Chrome Shortcuts Path is currently set.{Style.RESET_ALL}")

    print("Enter '0' to go back.")
    new_path = input("Enter the new path to save/update: ").strip()
    if new_path == '0':
        return
    elif new_path:
        config_manager.set_config('chrome_shortcuts_path', new_path)
        print(f"{Fore.GREEN}Chrome Shortcuts Path updated to: {new_path}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}No path entered. Please try again.{Style.RESET_ALL}")



def delete_hwid(hwid_manager):
    """Delete an HWID from the whitelist."""
    hwid_list = hwid_manager.get_all_hwids()
    if not hwid_list:
        print(f"{Fore.YELLOW}No HWIDs to delete.{Style.RESET_ALL}")
        input("Press any key to continue...")
        return

    print(f"{Fore.BLUE}List of HWIDs:{Style.RESET_ALL}")
    for index, hwid in enumerate(hwid_list, start=1):
        print(f"{index}. {hwid}")

    try:
        choice = int(input(f"{Fore.GREEN}Enter the number of the HWID to delete: {Style.RESET_ALL}"))
        if 1 <= choice <= len(hwid_list):
            hwid_to_delete = hwid_list[choice - 1]
            if hwid_manager.delete_hwid(hwid_to_delete):
                print(f"{Fore.GREEN}HWID '{hwid_to_delete}' deleted successfully.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to delete HWID '{hwid_to_delete}'.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid selection. Please enter a number between 1 and {len(hwid_list)}.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}Invalid input. Please enter a valid number.{Style.RESET_ALL}")


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
        print(f"An unexpected error occurred while checking ViGEmBus driver: {e}")
        logging.error(f"An unexpected error occurred while checking ViGEmBus driver: {e}")
        user_input = input("Would you like to download and install ViGEmBus now? (y/n): ")
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
