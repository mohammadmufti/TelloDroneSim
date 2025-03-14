import math
from obstruction_visuals import CylindricalObstruction, RectangularObstruction, PyramidalObstruction, SphereObstruction
from config import DRONE_LENGTH, DRONE_WIDTH, DRONE_HEIGHT

"""For multiple collisions in a single command path - you will only be made aware of one"""
class CollisionDetector:
    def __init__(self, obstructions):
        self.simple_obstructions = []
        self.composite_obstructions = []
        for o in obstructions:
            if hasattr(o, 'components') and o.components:
                self.composite_obstructions.append(o)
            else:
                self.simple_obstructions.append(o)
        # Precompute drone dimension values
        self.drone_half_width = DRONE_WIDTH / 2
        self.drone_half_length = DRONE_LENGTH / 2
        self.drone_half_height = DRONE_HEIGHT / 2
        self.min_dimension = min(DRONE_WIDTH, DRONE_LENGTH, DRONE_HEIGHT)
        self.max_horizontal = max(self.drone_half_width, self.drone_half_length)
        self.max_dimension = max(self.drone_half_width, self.drone_half_length, self.drone_half_height)

    def check_path_collision(self, current_state, target_state):
        """
        Check if a path from current_state to target_state would collide with any obstruction.
        Returns the colliding obstruction or None if no collision.
        """
        # Calculate 3D path length
        dx = target_state["x"] - current_state["x"]
        dy = target_state["y"] - current_state["y"]
        dz = target_state["z"] - current_state["z"]
        path_length = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5

        # Use smallest drone dimension for step size
        steps = max(1, math.ceil(path_length / self.min_dimension))

        for i in range(steps + 1):
            t = i / steps
            x = current_state["x"] + t * dx
            y = current_state["y"] + t * dy
            z = current_state["z"] + t * dz

            # Check each obstruction
            for obstruction in self.simple_obstructions:
                if self.check_point_collision(x, y, z, obstruction):
                    return obstruction
            for obstruction in self.composite_obstructions:
                for component in obstruction.components:
                    if self.check_point_collision(x, y, z, component):
                        return obstruction
        return None

    def check_point_collision(self, x, y, z, obstruction):
        """
        Check if a point (x, y, z) collides with a specific obstruction.
        Returns True if collision detected, False otherwise.
        """
        # Get obstruction properties
        pos_x, pos_y, pos_z = obstruction.position
        z_min = z - self.drone_half_height
        z_max = z + self.drone_half_height

        # Check collision based on obstruction type
        if isinstance(obstruction, CylindricalObstruction):
            if z_max >= pos_z and z_min <= pos_z + obstruction.height:
                dx = x - pos_x
                dy = y - pos_y
                horizontal_distance = (dx ** 2 + dy ** 2) ** 0.5
                return horizontal_distance <= obstruction.radius + self.max_horizontal
            return False

        elif isinstance(obstruction, RectangularObstruction):
            if z_max >= pos_z and z_min <= pos_z + obstruction.height:
                rel_x = x - pos_x
                rel_y = y - pos_y
                angle_rad = -math.radians(obstruction.rotation)
                cos_rad = math.cos(angle_rad)
                sin_rad = math.sin(angle_rad)
                rot_x = rel_x * cos_rad - rel_y * sin_rad
                rot_y = rel_x * sin_rad + rel_y * cos_rad
                return (abs(rot_x) <= obstruction.half_width + self.drone_half_width and
                        abs(rot_y) <= obstruction.half_depth + self.drone_half_length)
            return False

        elif isinstance(obstruction, SphereObstruction):
            if z_max >= pos_z - obstruction.radius and z_min <= pos_z + obstruction.radius:
                dx = x - pos_x
                dy = y - pos_y
                dz = z - pos_z
                distance_sq = dx ** 2 + dy ** 2 + dz ** 2
                radius_sum = obstruction.radius + self.max_dimension
                return distance_sq <= radius_sum ** 2
            return False

        elif isinstance(obstruction, PyramidalObstruction):
            if z_max >= pos_z and z_min <= pos_z + obstruction.height:
                rel_x = x - pos_x
                rel_y = y - pos_y
                angle_rad = -math.radians(obstruction.rotation)
                cos_rad = math.cos(angle_rad)
                sin_rad = math.sin(angle_rad)
                rot_x = rel_x * cos_rad - rel_y * sin_rad
                rot_y = rel_x * sin_rad + rel_y * cos_rad
                rel_height = max(0, min(1, (z - pos_z) / obstruction.height))
                allowed_width = obstruction.half_width * (1 - rel_height) + self.drone_half_width
                allowed_depth = obstruction.half_depth * (1 - rel_height) + self.drone_half_length
                return (abs(rot_x) <= allowed_width and abs(rot_y) <= allowed_depth)

            return False
        return False  # Default case if obstruction type is not recognized