from OpenGL.GL import *
from config import DRONE_BASE_COLOR, DRONE_BODY_COLOR

class DroneRenderer:
    def __init__(self, width, length, height, scale_factor):
        """
        Initialize the drone renderer with dimensions and scale factor.

        Args:
            width (float): Base width of the drone.
            length (float): Base length of the drone.
            height (float): Base height of the drone.
            scale_factor (float): Scaling factor for the drone model.
        """
        self.width = width * scale_factor
        self.length = length * scale_factor
        self.height = height * scale_factor
        self.display_list = self._create_display_list()

    def _create_display_list(self):
        """Create a display list for the drone to improve rendering efficiency."""
        half_width = self.width / 2
        half_length = self.length / 2
        height = self.height

        vertices = [
            (-half_width, half_length, 0),  # Back bottom-left
            (half_width, half_length, 0),  # Back bottom-right
            (-half_width, -half_length, 0),  # Front bottom-left
            (half_width, -half_length, 0),  # Front bottom-right
            (0, -half_length, height),  # Front tip (apex)
        ]

        faces = [
            (0, 1, 3, 2),  # Bottom (rectangular base at z=0)
            (4, 2, 3),  # Top (rectangular-ish triangle)
            (0, 2, 4),  # Left side (triangle)
            (1, 3, 4),  # Right side (triangle)
            (0, 1, 4),  # Back (triangle)
        ]

        display_list = glGenLists(1)
        glNewList(display_list, GL_COMPILE)

        # Draw bottom face (quad)
        glBegin(GL_QUADS)
        glColor3f(*DRONE_BASE_COLOR)
        for vertex in faces[0]:  # Bottom
            glVertex3fv(vertices[vertex])
        glEnd()

        # Draw triangular faces
        glBegin(GL_TRIANGLES)
        glColor3f(*DRONE_BODY_COLOR)
        for face in faces[1:]:  # Top, left, right, back
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        glEndList()
        return display_list

    def render(self, x, y, z, yaw):
        """
        Render the drone at the specified position and orientation.

        Args:
            x (float): X-coordinate of the drone.
            y (float): Y-coordinate of the drone.
            z (float): Z-coordinate of the drone.
            yaw (float): Yaw angle in degrees (clockwise from pilot's view).
        """
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(-yaw, 0, 0, 1)  # Clockwise around z from pilot's view
        glCallList(self.display_list)
        glPopMatrix()

    def cleanup(self):
        """Clean up the OpenGL display list."""
        glDeleteLists(self.display_list, 1)