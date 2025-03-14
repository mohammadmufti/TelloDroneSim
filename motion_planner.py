import math
from config import (DEFAULT_MOVE_TIME, FLIP_TIME, TAKEOFF_TIME, LAND_TIME)

class MotionPlanner:
    def __init__(self, drone, linear_accel, angular_accel):
        self.drone = drone
        self.linear_accel = linear_accel
        self.angular_accel = angular_accel

    def interpolate_state(self, current, target, elapsed, total_time, accel_time, coast_time):
        """Interpolate with trapezoidal velocity profile, handling zero distance."""
        distance = self.get_distance(current, target)
        if distance == 0 or total_time <= 0:
            return target.copy()

        if elapsed <= accel_time:  # Acceleration
            progress = 0.5 * self.linear_accel * (elapsed ** 2) / distance
        elif elapsed <= accel_time + coast_time:  # Constant speed
            accel_dist = 0.5 * self.linear_accel * (accel_time ** 2)
            coast_elapsed = elapsed - accel_time
            coast_speed = self.drone.speed
            progress = (accel_dist + coast_speed * coast_elapsed) / distance
        else:  # Deceleration
            decel_elapsed = total_time - elapsed
            decel_dist = 0.5 * self.linear_accel * (accel_time ** 2)
            total_dist = distance
            progress = (total_dist - decel_dist + 0.5 * self.linear_accel * (decel_elapsed ** 2)) / total_dist

        progress = min(max(progress, 0.0), 1.0)

        for key in current:
            current[key] = current[key] + (target[key] - current[key]) * progress
            if abs(current[key] - target[key]) < 0.1:
                current[key] = target[key]
        return current

    def get_distance(self, start, end):
        """Calculate Euclidean distance between states."""
        dx = end["x"] - start["x"]
        dy = end["y"] - start["y"]
        dz = end["z"] - start["z"]
        return math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    def calculate_move_time(self, cmd, start_state, end_state, max_speed):
        """Calculate movement time using a dispatch table."""
        parts = cmd.split()
        command = parts[0].lower()

        def go_time():
            distance = self.get_distance(start_state, end_state)
            return self._calc_linear_time(distance, self.linear_accel)

        def linear_time():
            try:
                distance = int(parts[1])
                return self._calc_linear_time(distance, self.linear_accel)
            except (IndexError, ValueError):
                return DEFAULT_MOVE_TIME

        def angular_time():
            try:
                angle = int(parts[1])
                return self._calc_angular_time(angle, self.angular_accel)
            except (IndexError, ValueError):
                return DEFAULT_MOVE_TIME

        COMMAND_TIMES = {
            "go": go_time,
            "up": linear_time,
            "down": linear_time,
            "left": linear_time,
            "right": linear_time,
            "forward": linear_time,
            "back": linear_time,
            "cw": angular_time,
            "ccw": angular_time,
            "flip": lambda: FLIP_TIME,
            "takeoff": lambda: TAKEOFF_TIME,
            "land": lambda: LAND_TIME,
        }

        return COMMAND_TIMES.get(command, lambda: DEFAULT_MOVE_TIME)()

    def _calc_linear_time(self, distance, accel):
        """Calculate time for linear movement with acceleration."""
        if distance == 0:
            return DEFAULT_MOVE_TIME
        accel_time = self.drone.speed / accel
        accel_dist = 0.5 * accel * (accel_time ** 2)
        if distance <= 2 * accel_dist:
            return 2 * math.sqrt(distance / accel)
        coast_dist = distance - 2 * accel_dist
        coast_time = coast_dist / self.drone.speed
        return 2 * accel_time + coast_time

    def _calc_angular_time(self, angle, accel):
        """Calculate time for angular movement with acceleration."""
        if angle == 0:
            return DEFAULT_MOVE_TIME
        max_angular_speed = accel
        accel_time = max_angular_speed / accel
        accel_angle = 0.5 * accel * (accel_time ** 2)
        if angle <= 2 * accel_angle:
            return 2 * math.sqrt(angle / accel)
        coast_angle = angle - 2 * accel_angle
        coast_time = coast_angle / max_angular_speed
        return 2 * accel_time + coast_time