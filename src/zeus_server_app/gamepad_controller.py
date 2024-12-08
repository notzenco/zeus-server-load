import time
import random
import threading
import vgamepad as vg
import logging

class GamepadController:
    def __init__(self):
        self.running = True
        self.anti_afk_enabled = True
        self.movement_enabled = False
        self.gamepad = vg.VX360Gamepad()
        self.lock = threading.Lock()

        # Events for stopping loops
        self.anti_afk_stop_event = threading.Event()
        self.movement_stop_event = threading.Event()

        # Threads for loops
        self._anti_afk_thread = None
        self._movement_thread = None

        # Default configuration values
        # Anti-AFK settings
        self.anti_afk_interval = 40.0     # seconds
        self.right_bumper_duration = 0.1  # seconds
        self.left_bumper_duration = 0.1   # seconds
        self.delay_between_buttons = 1.0  # seconds

        # Movement settings
        self.min_movement_duration = 4.0  # seconds
        self.max_movement_duration = 6.0  # seconds
        self.min_break_duration = 3.0     # seconds
        self.max_break_duration = 7.0     # seconds

        self.start_anti_afk()

    # Configuration Setters
    def set_anti_afk_settings(self, interval=None, right_bumper_duration=None, left_bumper_duration=None, delay_between_buttons=None):
        """Set Anti-AFK settings."""
        if interval is not None:
            self.anti_afk_interval = interval
            logging.info(f"Anti-AFK interval set to {interval} seconds")
        if right_bumper_duration is not None:
            self.right_bumper_duration = right_bumper_duration
            logging.info(f"Right Bumper duration set to {right_bumper_duration} seconds")
        if left_bumper_duration is not None:
            self.left_bumper_duration = left_bumper_duration
            logging.info(f"Left Bumper duration set to {left_bumper_duration} seconds")
        if delay_between_buttons is not None:
            self.delay_between_buttons = delay_between_buttons
            logging.info(f"Delay between buttons set to {delay_between_buttons} seconds")

    def set_movement_settings(self, min_movement_duration=None, max_movement_duration=None, min_break_duration=None, max_break_duration=None):
        """Set movement simulation settings."""
        if min_movement_duration is not None:
            self.min_movement_duration = min_movement_duration
            logging.info(f"Minimum movement duration set to {min_movement_duration} seconds")
        if max_movement_duration is not None:
            self.max_movement_duration = max_movement_duration
            logging.info(f"Maximum movement duration set to {max_movement_duration} seconds")
        if min_break_duration is not None:
            self.min_break_duration = min_break_duration
            logging.info(f"Minimum break duration set to {min_break_duration} seconds")
        if max_break_duration is not None:
            self.max_break_duration = max_break_duration
            logging.info(f"Maximum break duration set to {max_break_duration} seconds")

    def get_supported_commands(self):
        """Return a list of supported gamepad commands."""
        return [
            "press_a", "press_b", "press_x", "press_y",
            "press_lb", "press_rb", "press_lt", "press_rt",
            "press_dpad_up", "press_dpad_down", "press_dpad_left", "press_dpad_right",
            "press_start", "press_back", "press_ls", "press_rs"
        ]

    def execute_gamepad_command(self, command):
        """Execute the corresponding gamepad command."""
        try:
            method = getattr(self, command)
            method()
            logging.info(f"Executed gamepad command: {command}")
        except AttributeError:
            logging.error(f"Unsupported gamepad command: {command}")
        except Exception as e:
            logging.error(f"Failed to execute gamepad command '{command}': {e}")

    # Thread start/stop methods for Anti-AFK
    def start_anti_afk(self):
        """Start the anti-AFK loop in a separate thread if not already running."""
        if self._anti_afk_thread and self._anti_afk_thread.is_alive():
            logging.info("Anti-AFK thread is already running.")
            return

        self.anti_afk_enabled = True
        self.anti_afk_stop_event.clear()
        self._anti_afk_thread = threading.Thread(target=self.anti_afk_loop, daemon=True)
        self._anti_afk_thread.start()
        logging.info("Anti-AFK thread started.")

    def stop_anti_afk(self):
        """Stop the anti-AFK loop."""
        if not self.anti_afk_enabled:
            logging.info("Anti-AFK is not running.")
            return

        self.anti_afk_enabled = False
        self.anti_afk_stop_event.set()

        if self._anti_afk_thread:
            self._anti_afk_thread.join(timeout=10)
            if self._anti_afk_thread.is_alive():
                logging.warning("Anti-AFK thread did not terminate within timeout.")
            else:
                logging.info("Anti-AFK thread stopped.")

    # Thread start/stop methods for Movement
    def start_movement(self):
        """Start the movement loop in a separate thread. Also stops anti-afk if running."""
        if self._movement_thread and self._movement_thread.is_alive():
            logging.info("Movement thread is already running.")
            return

        # Stop Anti-AFK if it's running
        if self.anti_afk_enabled:
            self.stop_anti_afk()

        self.movement_enabled = True
        self.movement_stop_event.clear()
        self._movement_thread = threading.Thread(target=self.movement_loop, daemon=True)
        self._movement_thread.start()
        logging.info("Movement thread started.")

    def stop_movement(self):
        """Stop the movement loop. Also restart anti-afk if it was enabled by default."""
        if not self.movement_enabled:
            logging.info("Movement is not running.")
            return

        self.movement_enabled = False
        self.movement_stop_event.set()

        if self._movement_thread:
            self._movement_thread.join(timeout=10)
            if self._movement_thread.is_alive():
                logging.warning("Movement thread did not terminate within timeout.")
            else:
                logging.info("Movement thread stopped.")

        # Since anti-afk was on by default, re-enable it if running is still True
        # and user wants it enabled again
        if self.running and self.anti_afk_enabled:
            self.start_anti_afk()

    def anti_afk_loop(self):
        """Anti-AFK loop that periodically presses RB and LB."""
        logging.info("Anti-AFK loop started")
        try:
            while self.running:
                if not self.anti_afk_enabled:
                    time.sleep(0.1)
                    continue

                with self.lock:
                    self._press_button_for_duration(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER, "RB", self.right_bumper_duration)
                    time.sleep(self.delay_between_buttons)
                    self._press_button_for_duration(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, "LB", self.left_bumper_duration)

                logging.info(f"Anti-AFK: Waiting {self.anti_afk_interval} seconds")
                # Wait for either the interval to pass or the event to be set, no increments here
                if self._wait_or_stop(self.anti_afk_stop_event, self.anti_afk_interval):
                    break
        except Exception as e:
            logging.error(f"Exception in anti_afk_loop: {e}")
        finally:
            logging.info("Anti-AFK loop ended")

    def movement_loop(self):
        """Movement loop that simulates random joystick movements."""
        logging.info("Movement loop started")
        try:
            while self.running:
                if not self.movement_enabled:
                    time.sleep(0.1)
                    continue

                logging.info("Simulating movement...")
                duration = random.uniform(self.min_movement_duration, self.max_movement_duration)
                start_time = time.time()

                while self.movement_enabled and (time.time() - start_time) < duration and self.running:
                    move_x = random.uniform(-1, 1)
                    move_y = random.uniform(-1, 1)
                    with self.lock:
                        self.gamepad.left_joystick_float(x_value_float=move_x, y_value_float=move_y)
                        self.gamepad.update()
                    time.sleep(0.1)

                if not self.movement_enabled or not self.running:
                    break

                logging.info(f"Movement phase complete. Breaking for {duration:.2f} seconds.")
                # No increments, just one wait or stop
                if self._wait_or_stop(self.movement_stop_event, random.uniform(self.min_break_duration, self.max_break_duration)):
                    break
        except Exception as e:
            logging.error(f"Exception in movement_loop: {e}")
        finally:
            logging.info("Movement loop ended")

    # Individual Button and Control Methods
    def press_a(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, "A")

    def press_b(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B, "B")

    def press_x(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X, "X")

    def press_y(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y, "Y")

    def press_lb(self):
        self._press_button_for_duration(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, "LB", self.left_bumper_duration)

    def press_rb(self):
        self._press_button_for_duration(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER, "RB", self.right_bumper_duration)

    def press_start(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START, "START")

    def press_back(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK, "BACK")

    def press_ls(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB, "Left Stick Click")

    def press_rs(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB, "Right Stick Click")

    def press_dpad_up(self):
        self._press_dpad(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, "DPAD UP")

    def press_dpad_down(self):
        self._press_dpad(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, "DPAD DOWN")

    def press_dpad_left(self):
        self._press_dpad(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT, "DPAD LEFT")

    def press_dpad_right(self):
        self._press_dpad(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT, "DPAD RIGHT")

    # Helper Methods for Actions
    def _press_button(self, button, name):
        """Press and release a button quickly."""
        logging.info(f"Pressing '{name}' button (short press)")
        self.gamepad.press_button(button)
        self.gamepad.update()
        time.sleep(0.1)
        self.gamepad.release_button(button)
        self.gamepad.update()

    def _press_button_for_duration(self, button, name, duration):
        """Press and hold a button for a specified duration."""
        logging.info(f"Pressing '{name}' button for {duration:.2f} seconds")
        self.gamepad.press_button(button)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.release_button(button)
        self.gamepad.update()

    def _press_dpad(self, button, name):
        """Tap a D-Pad direction briefly."""
        logging.info(f"Pressing '{name}' (D-Pad)")
        self.gamepad.press_button(button)
        self.gamepad.update()
        time.sleep(0.1)
        self.gamepad.release_button(button)
        self.gamepad.update()

    def toggle_mode(self, mode):
        """Switch between Anti-AFK and Movement mode."""
        if mode == "anti_afk":
            self.stop_movement()      # Stop movement if running
            self.anti_afk_enabled = True
            self.start_anti_afk()    # Start anti-afk if not started
            logging.info("Switched to Anti-AFK mode")
        elif mode == "movement":
            self.stop_anti_afk()     # Stop anti-afk if running
            self.movement_enabled = True
            self.start_movement()    # Start movement
            logging.info("Switched to Movement mode")

    def _wait_or_stop(self, stop_event, duration):
        """
        Wait for `duration` seconds or until `stop_event` is set.
        Returns True if stopped early (event set), False if waited full duration.
        """
        return stop_event.wait(duration)
