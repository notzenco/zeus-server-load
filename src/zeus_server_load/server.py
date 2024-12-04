import socket
import threading
import logging
from zeus_server_load.gamepad_controller import GamepadController


class CommandServer:
    """A server that handles client commands and enforces HWID checks."""

    def __init__(self, hwid_manager, host="0.0.0.0", port=9999):
        self.hwid_manager = hwid_manager
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_running = True
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
                    elif data in self.get_supported_commands():
                        self.execute_gamepad_command(data)
                        conn.sendall(f"Executed command: {data}".encode())
                    elif data == "start_anti_afk":
                        self.start_anti_afk()
                        conn.sendall("Anti-AFK started.".encode())
                    elif data == "stop_anti_afk":
                        self.stop_anti_afk()
                        conn.sendall("Anti-AFK stopped.".encode())
                    elif data == "start_movement":
                        self.start_movement()
                        conn.sendall("Movement started.".encode())
                    elif data == "stop_movement":
                        self.stop_movement()
                        conn.sendall("Movement stopped.".encode())
                    else:
                        conn.sendall("unknown command".encode())

            except Exception as e:
                logging.error(f"Error handling client {addr}: {e}")

    def get_supported_commands(self):
        """Return a list of supported gamepad commands."""
        return [
            "press_a", "press_b", "press_x", "press_y",
            "press_lb", "press_rb", "press_lt", "press_rt",
            "press_up", "press_down", "press_left", "press_right",
            "press_start", "press_back", "press_ls", "press_rs"
        ]

    def execute_gamepad_command(self, command):
        """Execute the corresponding gamepad command."""
        try:
            method = getattr(self.gamepad_controller, command)
            method()
        except Exception as e:
            logging.error(f"Failed to execute gamepad command '{command}': {e}")

    def start_anti_afk(self):
        """Start the anti-AFK loop."""
        self.gamepad_controller.anti_afk_enabled = True
        if not hasattr(self, "_anti_afk_thread") or not self._anti_afk_thread.is_alive():
            self._anti_afk_thread = threading.Thread(target=self.gamepad_controller.anti_afk_loop, daemon=True)
            self._anti_afk_thread.start()
        logging.info("Anti-AFK started.")

    def stop_anti_afk(self):
        """Stop the anti-AFK loop."""
        self.gamepad_controller.anti_afk_enabled = False
        logging.info("Anti-AFK stopped.")

    def start_movement(self):
        """Start the movement loop."""
        self.gamepad_controller.movement_enabled = True
        if not hasattr(self, "_movement_thread") or not self._movement_thread.is_alive():
            self._movement_thread = threading.Thread(target=self.gamepad_controller.movement_loop, daemon=True)
            self._movement_thread.start()
        logging.info("Movement started.")

    def stop_movement(self):
        """Stop the movement loop."""
        self.gamepad_controller.movement_enabled = False
        logging.info("Movement stopped.")

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
        self.is_running = False
        self.server_socket.close()
