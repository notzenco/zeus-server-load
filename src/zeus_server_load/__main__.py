import threading
import signal
import sys
from zeus_server_load.hwid_manager import HWIDManager
from zeus_server_load.config_manager import ConfigManager
from zeus_server_load.utils import setup_logging, check_vigem_bus_driver, display_menu
from zeus_server_load.chrome_manager import ChromeManager



def main():
    # Set up logging
    setup_logging()

    if not check_vigem_bus_driver():
        # If the driver is not installed and the user chooses not to install it, the program will exit.
        return
    
    from zeus_server_load.server import CommandServer

    # Handle signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize HWID Manager
    hwid_manager = HWIDManager()
    config_manager = ConfigManager()
    chrome_manager = ChromeManager(config_manager)



    # Start the server in a separate thread
    server = CommandServer(hwid_manager = hwid_manager, config_manager = config_manager)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    # Run the menu interface in the main thread
    display_menu(server, config_manager, chrome_manager)


def signal_handler(sig, frame):
    """Handle signals for graceful shutdown."""
    print("[INFO] Received termination signal. Exiting...")
    sys.exit(0)


if __name__ == "__main__":
    main()
