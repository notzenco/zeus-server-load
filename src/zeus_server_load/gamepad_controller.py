import time
import random
import threading
import vgamepad as vg
import logging


class GamepadController:
    def __init__(self):
        self.running = True
        self.anti_afk_enabled = False
        self.movement_enabled = False
        self.gamepad = vg.VX360Gamepad()
        self.lock = threading.Lock()

        # Default configuration values

        # Anti-AFK settings
        self.anti_afk_interval = 60.0  # in seconds
        self.right_bumper_duration = 0.1  # in seconds
        self.left_bumper_duration = 0.1  # in seconds
        self.delay_between_buttons = 0.5  # in seconds

        # Movement settings
        self.min_movement_duration = 4.0  # in seconds
        self.max_movement_duration = 6.0  # in seconds
        self.min_break_duration = 3.0  # in seconds
        self.max_break_duration = 7.0  # in seconds

    # Setter methods for configuration
    def set_anti_afk_settings(self, interval=None, right_bumper_duration=None, left_bumper_duration=None, delay_between_buttons=None):
        """Set Anti-AFK settings."""
        if interval is not None:
            self.anti_afk_interval = interval
        if right_bumper_duration is not None:
            self.right_bumper_duration = right_bumper_duration
        if left_bumper_duration is not None:
            self.left_bumper_duration = left_bumper_duration
        if delay_between_buttons is not None:
            self.delay_between_buttons = delay_between_buttons

    def set_movement_settings(self, min_movement_duration=None, max_movement_duration=None, min_break_duration=None, max_break_duration=None):
        """Set movement simulation settings."""
        if min_movement_duration is not None:
            self.min_movement_duration = min_movement_duration
        if max_movement_duration is not None:
            self.max_movement_duration = max_movement_duration
        if min_break_duration is not None:
            self.min_break_duration = min_break_duration
        if max_break_duration is not None:
            self.max_break_duration = max_break_duration

    # Existing methods remain unchanged
    def anti_afk_loop(self):
        """Anti-AFK loop that periodically presses buttons."""
        logging.info("Anti-AFK loop started")
        while self.running:
            if not self.anti_afk_enabled:
                time.sleep(0.1)
                continue

            with self.lock:
                self.press_rb()
                time.sleep(self.delay_between_buttons)
                self.press_lb()

            logging.info(f"Anti-AFK: Waiting {self.anti_afk_interval} seconds")
            time.sleep(self.anti_afk_interval)
        logging.info("Anti-AFK loop ended")

    def movement_loop(self):
        """Movement loop that simulates random controller inputs."""
        logging.info("Movement loop started")
        while self.running:
            if not self.movement_enabled:
                time.sleep(0.1)
                continue

            logging.info("Simulating movement...")
            duration = random.uniform(self.min_movement_duration, self.max_movement_duration)
            start_time = time.time()

            while self.running and self.movement_enabled and (time.time() - start_time) < duration:
                move_x = random.uniform(-1, 1)
                move_y = random.uniform(-1, 1)
                with self.lock:
                    self.gamepad.left_joystick_float(x_value_float=move_x, y_value_float=move_y)
                    self.gamepad.update()
                time.sleep(0.1)

            logging.info(f"Movement phase complete. Breaking for {duration} seconds.")
            time.sleep(random.uniform(self.min_break_duration, self.max_break_duration))
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
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, "LB")

    def press_rb(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER, "RB")

    def press_lt(self):
        self._press_trigger(0, "LT")

    def press_rt(self):
        self._press_trigger(1, "RT")

    def press_start(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START, "START")

    def press_back(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK, "BACK")

    def press_ls(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB, "Left Stick Click")

    def press_rs(self):
        self._press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB, "Right Stick Click")

    def move_dpad_up(self):
        self._move_dpad(vg.DPAD.UP, "DPAD UP")

    def move_dpad_down(self):
        self._move_dpad(vg.DPAD.DOWN, "DPAD DOWN")

    def move_dpad_left(self):
        self._move_dpad(vg.DPAD.LEFT, "DPAD LEFT")

    def move_dpad_right(self):
        self._move_dpad(vg.DPAD.RIGHT, "DPAD RIGHT")

    def move_left_stick(self, x, y):
        with self.lock:
            self.gamepad.left_joystick_float(x_value_float=x, y_value_float=y)
            self.gamepad.update()
        logging.info(f"Moved Left Stick to ({x}, {y})")

    def move_right_stick(self, x, y):
        with self.lock:
            self.gamepad.right_joystick_float(x_value_float=x, y_value_float=y)
            self.gamepad.update()
        logging.info(f"Moved Right Stick to ({x}, {y})")

    # Helper Methods for Actions
    def _press_button(self, button, name):
        logging.info(f"Pressing '{name}' button")
        with self.lock:
            self.gamepad.press_button(button)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(button)
            self.gamepad.update()

    def _press_trigger(self, trigger, name):
        logging.info(f"Pressing '{name}' trigger")
        with self.lock:
            if trigger == 0:  # LT
                self.gamepad.left_trigger(value=255)
            elif trigger == 1:  # RT
                self.gamepad.right_trigger(value=255)
            self.gamepad.update()
            time.sleep(0.1)
            if trigger == 0:  # LT
                self.gamepad.left_trigger(value=0)
            elif trigger == 1:  # RT
                self.gamepad.right_trigger(value=0)
            self.gamepad.update()

    def _move_dpad(self, direction, name):
        logging.info(f"Moving '{name}'")
        with self.lock:
            self.gamepad.d_pad(direction)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.d_pad(vg.DPAD.OFF)
            self.gamepad.update()

    def toggle_mode(self, mode):
        """Switch between Anti-AFK and Movement mode."""
        if mode == "anti_afk":
            self.anti_afk_enabled = True
            self.movement_enabled = False
            logging.info("Switched to Anti-AFK mode")
        elif mode == "movement":
            self.anti_afk_enabled = False
            self.movement_enabled = True
            logging.info("Switched to Movement mode")
