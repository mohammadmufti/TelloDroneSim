from djitellopy import Tello
import time

class TelloWrapper:
    def __init__(self):
        print("Initializing UDP connection...")
        self.tello = Tello()
        retries = 3
        delay = 2  # Seconds between retries
        for attempt in range(retries):
            try:
                self.tello.connect()  # Attempt UDP connection
                print("Connection established.")
                self.current_command = None
                return  # Exit if successful
            except Exception as e:
                print(f"Connection attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)  # Wait before retrying
                else:
                    raise Exception("Failed to connect to Tello after multiple attempts. Ensure drone is on and Wi-Fi is connected.")

    def execute_command(self, command_str):
        self.current_command = command_str
        try:
            response = self.tello.send_command_with_return(command_str)
        except Exception as e:
            print(f"Command '{command_str}' failed: {e}")
            response = "error"
        self.current_command = None
        return response

    def update(self, dt):
        pass

    def get_state(self):
        return {
            "x": 0,  # Tello doesn't track x/y precisely without external sensors
            "y": 0,
            "z": self.tello.get_height(),
            "yaw": self.tello.get_yaw(),
            "flying": self.tello.is_flying
        }