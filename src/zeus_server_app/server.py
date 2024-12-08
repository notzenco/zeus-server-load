import socket
import threading
import logging
from zeus_server_app.gamepad_controller import GamepadController
from zeus_server_app.chrome_manager import ChromeManager
from zeus_server_app.utils import tail_lines

class CommandServer:
    """A server that handles client commands and enforces HWID checks."""

    def __init__(self, hwid_manager, config_manager, host="0.0.0.0", port=9999):
        self.hwid_manager = hwid_manager
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_running = True
        self.config_manager = config_manager
        self.chrome_manager = ChromeManager(config_manager)  # Instantiate ChromeManager
        self.gamepad_controller = GamepadController()

    def handle_client(self, conn, addr):
        """Handle incoming client commands."""
        logging.info(f"Connected to {addr}")
        with conn:
            try:
                # Receive the HWID from the client as the first message
                hwid = conn.recv(1024).decode().strip()
                logging.info(f"Received HWID: {hwid}")

                # Validate the HWID
                if not self.hwid_manager.is_hwid_whitelisted(hwid):
                    conn.sendall("HWID not authorized.".encode())
                    logging.warning(f"Unauthorized HWID: {hwid}")
                    return

                conn.sendall("HWID authorized.".encode())
                logging.info(f"HWID authorized: {hwid}")

                # Process subsequent commands
                while True:
                    data = conn.recv(1024).decode().strip()
                    if not data:
                        break

                    logging.info(f"Received command: {data}")

                    if data == "healthCheck":
                        conn.sendall("alive".encode())
                    elif data in self.gamepad_controller.get_supported_commands():
                        self.gamepad_controller.execute_gamepad_command(data)
                        conn.sendall(f"Executed command: {data}".encode())
                    elif data == "start_anti_afk":
                        self.gamepad_controller.start_anti_afk()
                        conn.sendall("Anti-AFK started.".encode())
                    elif data == "stop_anti_afk":
                        self.gamepad_controller.stop_anti_afk()
                        conn.sendall("Anti-AFK stopped.".encode())
                    elif data == "install_tampermonkey_script":
                        script_url = "https://github.com/redphx/better-xcloud/releases/latest/download/better-xcloud.user.js"
                        self.chrome_manager.install_tampermonkey_script_in_all_profiles(script_url)
                        conn.sendall("Opened script URL in all Chrome profiles. Please install manually.".encode())
                    elif data == "install_tampermonkey":
                        extension_url = "https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo"
                        self.chrome_manager.install_extension_on_all_profiles(extension_url)
                        conn.sendall("Opened extension page in all Chrome profiles. Please install manually.".encode())
                    elif data == "open_all_chrome_profiles":
                        self.chrome_manager.open_all_chrome_profiles()
                        conn.sendall("Opened all Chrome profiles.".encode())
                    elif data == "start_movement":
                        self.gamepad_controller.start_movement()
                        conn.sendall("Movement started.".encode())
                    elif data == "stop_movement":
                        self.gamepad_controller.stop_movement()
                        conn.sendall("Movement stopped.".encode())
                    elif data == "tail_logs":
                        try:
                            # Tail the last 100 lines of the log file
                            last_logs = tail_lines('server.log', num_lines=100)
                            if not last_logs:
                                last_logs = "No logs found or log file empty.\n"
                            conn.sendall(last_logs.encode('utf-8', errors='replace'))
                        except Exception as e:
                            logging.error(f"Failed to tail logs: {e}")
                            error_msg = f"Error reading logs: {e}"
                            conn.sendall(error_msg.encode('utf-8'))
                    else:
                        conn.sendall("unknown command".encode())

            except Exception as e:
                logging.error(f"Error handling client {addr}: {e}")

    def start(self):
        """Start the server."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            logging.info(f"Server listening on {self.host}:{self.port}")

            while self.is_running:
                conn, addr = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                client_thread.start()
        except Exception as e:
            logging.error(f"Server encountered an error: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown the server gracefully."""
        logging.info("Shutting down server...")
        self.gamepad_controller.running = False

        # Stop Anti-AFK if running
        if self.gamepad_controller.anti_afk_enabled:
            self.gamepad_controller.stop_anti_afk()

        # Stop Movement Loop if running
        if self.gamepad_controller.movement_enabled:
            self.gamepad_controller.stop_movement()

        self.is_running = False
        self.server_socket.close()
