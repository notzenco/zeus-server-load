import threading
import signal
import sys
from zeus_server_load.server import CommandServer
from zeus_server_load.hwid_manager import HWIDManager
from zeus_server_load.utils import setup_logging, display_menu, check_and_install_dependencies


def main():
    # Set up logging
    setup_logging()

    # Handle signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check and install dependencies
    check_and_install_dependencies()

    # Initialize HWID Manager
    hwid_manager = HWIDManager()

    # Start the server in a separate thread
    server = CommandServer(hwid_manager)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    # Run the menu interface in the main thread
    display_menu(server)


def signal_handler(sig, frame):
    """Handle signals for graceful shutdown."""
    print("[INFO] Received termination signal. Exiting...")
    sys.exit(0)


if __name__ == "__main__":
    main()
