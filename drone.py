import time
import math
from config import (DRONE_DEFAULT_SPEED,DRONE_INITIAL_BATTERY,DRONE_IDLE_DRAIN_RATE,
    DRONE_FLYING_DRAIN_RATE,DRONE_HIGH_POWER_DRAIN_RATE,
    DRONE_INITIAL_X,DRONE_INITIAL_Y,DRONE_INITIAL_Z,DRONE_INITIAL_YAW)

"""Handles Drone related physics and command logic"""
class Drone:
    def __init__(self, weather_data=None):
        self.x = DRONE_INITIAL_X  # cm, right is positive
        self.y = DRONE_INITIAL_Y  # cm, forward is positive
        self.z = DRONE_INITIAL_Z  # cm, up is positive
        self.yaw = DRONE_INITIAL_YAW  # degrees, clockwise from north (0°)
        self.battery = DRONE_INITIAL_BATTERY  # percent, float for precision
        self.speed = DRONE_DEFAULT_SPEED  # cm/s
        self.connected = False
        self.flying = False
        self.last_update_time = time.time()  # Track time for battery updates
        self.IDLE_DRAIN_RATE = DRONE_IDLE_DRAIN_RATE
        self.FLYING_DRAIN_RATE = DRONE_FLYING_DRAIN_RATE
        self.HIGH_POWER_DRAIN_RATE = DRONE_HIGH_POWER_DRAIN_RATE
        self.weather_data = weather_data if weather_data else {}
        self.temperature = self.weather_data.get("temperature", 20)  # Default 20°C

    def update_battery(self, current_time):
        """Update battery based on elapsed time, state, and temperature."""
        if self.last_update_time is None:
            self.last_update_time = current_time
            return

        elapsed = current_time - self.last_update_time
        if elapsed <= 0:
            return

        # Determine base drain rate based on state
        if not self.flying:
            drain_rate = DRONE_IDLE_DRAIN_RATE
        elif self.battery > 0:
            drain_rate = DRONE_FLYING_DRAIN_RATE
        else:
            drain_rate = 0

        # Adjust drain rate for temperature
        temp_factor = 0.0
        if self.temperature < 10:
            temp_factor = max(0, (20 - self.temperature) * 0.0167)  # Up to 1.5x at -10°C
        elif self.temperature > 30:
            temp_factor = max(0, (self.temperature - 30) * 0.02)  # Up to 1.2x at 40°C
        adjusted_drain_rate = drain_rate * (1 + temp_factor)

        # Update battery level
        self.battery = max(0.0, self.battery - adjusted_drain_rate * elapsed)
        self.last_update_time = current_time

    def execute_command(self, cmd):
        """Execute Tello SDK commands and return appropriate responses."""
        current_time = time.time()
        self.update_battery(current_time)

        parts = cmd.strip().split()
        if not parts:
            return "error"

        command = parts[0].lower()

        if command == "command":
            self.connected = True
            return "ok"

        if not self.connected:
            return "error"

        if command == "takeoff":
            if self.flying:
                return "error"
            self.flying = True
            self.z = 100 #1m hover
            return "ok"

        elif command == "land":
            if not self.flying:
                return "error"
            self.flying = False
            self.z = 0
            return "ok"

        elif command in ["up", "down", "left", "right", "forward", "back"]:
            if not self.flying:
                return "error"
            try:
                dist = int(parts[1])
                if not (20 <= dist <= 500):
                    return "error"

                if command == "up":
                    self.z += dist
                elif command == "down":
                    self.z = max(0, self.z - dist)
                elif command == "forward":
                    rad = math.radians(self.yaw)  # Convert yaw to radians
                    self.x += dist * math.sin(rad)  # East-west movement
                    self.y += dist * math.cos(rad)  # North-south movement
                elif command == "back":
                    rad = math.radians(self.yaw)  # Convert yaw to radians
                    self.x -= dist * math.sin(rad)  # East-west movement
                    self.y -= dist * math.cos(rad)  # North-south movement
                elif command == "right":
                    rad = math.radians(self.yaw + 90)  # 90° clockwise from yaw
                    self.x += dist * math.sin(rad)
                    self.y += dist * math.cos(rad)
                elif command == "left":
                    rad = math.radians(self.yaw - 90)  # 90° counterclockwise from yaw
                    self.x += dist * math.sin(rad)
                    self.y += dist * math.cos(rad)
                return "ok"
            except (IndexError, ValueError):
                return "error"

        elif command == "cw" or command == "ccw":
            if not self.flying:
                return "error"
            try:
                angle = int(parts[1])
                if not (1 <= angle <= 360):
                    return "error"
                self.yaw = (self.yaw + (angle if command == "cw" else -angle)) % 360
                return "ok"
            except (IndexError, ValueError):
                return "error"

        elif command == "flip":
            if not self.flying:
                return "error"
            try:
                direction = parts[1].lower()
                if direction not in ["l", "r", "f", "b"]:
                    return "error"
                # Temporarily increase drain rate for flip (applied in simulator)
                return "ok"
            except IndexError:
                return "error"

        elif command == "go":
            if not self.flying:
                return "error"
            try:
                x, y, z, speed = map(int, parts[1:5])
                if not (-500 <= x <= 500 and -500 <= y <= 500 and -500 <= z <= 500):
                    return "error"
                if not (10 <= speed <= 100):
                    return "error"
                self.x = x
                self.y = y
                self.z = max(0, z)
                self.speed = speed
                return "ok"
            except (IndexError, ValueError):
                return "error"

        elif command == "speed":
            try:
                speed = int(parts[1])
                if not (10 <= speed <= 100):
                    return "error"
                self.speed = speed
                return "ok"
            except (IndexError, ValueError):
                return "error"

        elif command == "battery?":
            return str(int(self.battery))  # Return integer percentage as string

        elif command == "speed?":
            return str(self.speed)

        elif command == "time?":
            return "0"

        elif command == "emergency":
            self.flying = False
            self.z = 0
            return "ok"

        return "error"

    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "yaw": self.yaw
        }