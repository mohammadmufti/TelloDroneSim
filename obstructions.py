import numpy as np
from OpenGL.GL import *
from abc import ABC, abstractmethod
import math
from OpenGL.GLU import *


class Obstruction(ABC):
    """Abstract base class for all obstructions in the simulation."""

    def __init__(self, position, color=(0.5, 0.5, 0.5)):
        """
        Initialize an obstruction.

        Args:
            position: Tuple/list (x, y, z) for the center position of the obstruction
            color: Tuple (r, g, b) for the color of the obstruction
        """
        self.position = np.array(position, dtype=float)
        self.color = color
        # Each obstruction type must create its own display list
        self.display_list = None

    def create_display_list(self):
        """Create an OpenGL display list for efficient rendering."""
        list_id = glGenLists(1)
        glNewList(list_id, GL_COMPILE)
        self._draw_shape()
        glEndList()
        return list_id

    def render(self):
        """Render the obstruction using its display list."""
        if self.display_list is None:
            self.display_list = self.create_display_list()

        glPushMatrix()
        glTranslatef(*self.position)
        glCallList(self.display_list)
        glPopMatrix()

    @abstractmethod
    def _draw_shape(self):
        """Draw the shape - must be implemented by subclasses."""
        pass

    def delete(self):
        """Clean up OpenGL resources."""
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)


class CylindricalObstruction(Obstruction):
    """Cylindrical obstruction with configurable radius and height."""

    def __init__(self, position, radius, height, color=(0.5, 0.5, 0.5), segments=16):
        """
        Initialize a cylindrical obstruction.

        Args:
            position: Tuple/list (x, y, z) for the base center of the cylinder
            radius: Radius of the cylinder
            height: Height of the cylinder
            color: Tuple (r, g, b) for the color
            segments: Number of segments to use when drawing the cylinder
        """
        super().__init__(position, color)
        self.radius = radius
        self.height = height
        self.segments = segments
        self.display_list = self.create_display_list()

    def _draw_shape(self):
        """Draw the cylindrical shape using OpenGL."""
        glColor3f(*self.color)

        # Draw the cylinder body
        glBegin(GL_QUAD_STRIP)
        for i in range(self.segments + 1):
            angle = 2.0 * math.pi * i / self.segments
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)

            # Bottom vertex
            glVertex3f(x, y, 0)
            # Top vertex
            glVertex3f(x, y, self.height)
        glEnd()

        # Draw top and bottom caps
        for cap_z in [0, self.height]:
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, cap_z)  # Center point
            for i in range(self.segments + 1):
                angle = 2.0 * math.pi * i / self.segments
                x = self.radius * math.cos(angle)
                y = self.radius * math.sin(angle)
                glVertex3f(x, y, cap_z)
            glEnd()

class RectangularObstruction(Obstruction):
    """Rectangular prism obstruction with configurable dimensions."""

    def __init__(self, position, dimensions, color=(0.5, 0.5, 0.5), rotation=0):
        """
        Initialize a rectangular prism obstruction.

        Args:
            position: Tuple/list (x, y, z) for the center bottom of the prism
            dimensions: Tuple/list (width, depth, height)
            color: Tuple (r, g, b) for the color
            rotation: Rotation angle in degrees around the z-axis
        """
        super().__init__(position, color)
        self.dimensions = np.array(dimensions, dtype=float)
        self.rotation = rotation
        self.display_list = self.create_display_list()

        # Pre-compute half-dimensions for collision detection
        self.half_width = self.dimensions[0] / 2
        self.half_depth = self.dimensions[1] / 2
        self.height = self.dimensions[2]

        # Create rotation matrix for collision detection
        angle_rad = math.radians(self.rotation)
        self.rot_matrix = np.array([
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ])

    def _draw_shape(self):
        """Draw the rectangular prism using OpenGL."""
        glColor3f(*self.color)

        # Apply rotation
        glRotatef(self.rotation, 0, 0, 1)

        # Half dimensions for centered drawing
        half_width = self.dimensions[0] / 2
        half_depth = self.dimensions[1] / 2
        height = self.dimensions[2]

        # Define vertices for a box centered at origin
        vertices = [
            # Bottom face
            (-half_width, -half_depth, 0),
            (half_width, -half_depth, 0),
            (half_width, half_depth, 0),
            (-half_width, half_depth, 0),

            # Top face
            (-half_width, -half_depth, height),
            (half_width, -half_depth, height),
            (half_width, half_depth, height),
            (-half_width, half_depth, height)
        ]

        # Define faces using vertex indices
        faces = [
            (0, 1, 2, 3),  # Bottom
            (4, 5, 6, 7),  # Top
            (0, 1, 5, 4),  # Front
            (2, 3, 7, 6),  # Back
            (0, 3, 7, 4),  # Left
            (1, 2, 6, 5)  # Right
        ]

        # Draw each face as a quad
        glBegin(GL_QUADS)
        for face in faces:
            for vertex_idx in face:
                glVertex3fv(vertices[vertex_idx])
        glEnd()

        # Draw borders
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(-1.0, -1.0)  # Push lines slightly forward to avoid z-fighting
        glLineWidth(1.5)  # Thicker lines for visibility
        glColor3f(1.0, 1.0, 1.0)  # Black borders (adjust as needed)

        glBegin(GL_LINE_LOOP)
        for face in faces:
            for vertex_idx in face:
                glVertex3fv(vertices[vertex_idx])
            glEnd()  # End after each face to restart GL_LINE_LOOP
            glBegin(GL_LINE_LOOP)  # Start new loop for next face
        glEnd()  # Final end for the last face

        glDisable(GL_POLYGON_OFFSET_LINE)

class PyramidalObstruction(Obstruction):
    """Pyramidal obstruction with a rectangular base and a point at the top."""

    def __init__(self, position, base_dimensions, height, color=(0.5, 0.5, 0.5), rotation=0):
        """
        Initialize a pyramidal obstruction.

        Args:
            position: Tuple/list (x, y, z) for the center bottom of the pyramid
            base_dimensions: Tuple/list (width, depth) for the rectangular base
            height: Height of the pyramid
            color: Tuple (r, g, b) for the color
            rotation: Rotation angle in degrees around the z-axis
        """
        super().__init__(position, color)
        self.base_dimensions = np.array(base_dimensions, dtype=float)
        self.height = height
        self.rotation = rotation
        self.display_list = self.create_display_list()

        # Pre-compute half-dimensions for collision detection
        self.half_width = self.base_dimensions[0] / 2
        self.half_depth = self.base_dimensions[1] / 2

        # Create rotation matrix for collision detection
        angle_rad = math.radians(self.rotation)
        self.rot_matrix = np.array([
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ])

    def _draw_shape(self):
        """Draw the pyramid using OpenGL."""
        glColor3f(*self.color)

        # Apply rotation
        glRotatef(self.rotation, 0, 0, 1)

        # Half dimensions for centered drawing
        half_width = self.base_dimensions[0] / 2
        half_depth = self.base_dimensions[1] / 2

        # Define base vertices
        base_vertices = [
            (-half_width, -half_depth, 0),
            (half_width, -half_depth, 0),
            (half_width, half_depth, 0),
            (-half_width, half_depth, 0)
        ]

        # Define apex
        apex = (0, 0, self.height)

        # Draw base (one quad)
        glBegin(GL_QUADS)
        for vertex in base_vertices:
            glVertex3fv(vertex)
        glEnd()

        # Draw triangular faces (four triangles)
        glBegin(GL_TRIANGLES)
        for i in range(4):
            # Get current and next vertex
            v1 = base_vertices[i]
            v2 = base_vertices[(i + 1) % 4]

            # Draw triangle from v1 to v2 to apex
            glVertex3fv(v1)
            glVertex3fv(v2)
            glVertex3fv(apex)
        glEnd()


class SphereObstruction(Obstruction):
    """Spherical obstruction with configurable radius."""

    def __init__(self, position, radius, color=(0.5, 0.5, 0.5), slices=16, stacks=16):
        """
        Initialize a spherical obstruction.

        Args:
            position: Tuple/list (x, y, z) for the center of the sphere
            radius: Radius of the sphere
            color: Tuple (r, g, b) for the color
            slices: Number of slices (longitude lines)
            stacks: Number of stacks (latitude lines)
        """
        super().__init__(position, color)
        self.radius = radius
        self.slices = slices
        self.stacks = stacks
        self.quadric = gluNewQuadric()  # Initialize quadric immediately
        self.display_list = None  # Defer display list creation

    def _draw_shape(self):
        """Draw the sphere using OpenGL."""
        glColor3f(*self.color)
        gluQuadricDrawStyle(self.quadric, GLU_FILL)
        gluQuadricNormals(self.quadric, GLU_SMOOTH)
        gluSphere(self.quadric, self.radius, self.slices, self.stacks)

    def delete(self):
        """Clean up OpenGL resources."""
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
        if self.quadric is not None:  # Check to be safe
            gluDeleteQuadric(self.quadric)


class CompositeObstruction(Obstruction):
    """Composite obstruction combining multiple basic shapes."""

    def __init__(self, position, color=(0.5, 0.5, 0.5)):
        """
        Initialize a composite obstruction.

        Args:
            position: Tuple/list (x, y, z) for the reference position
            color: Default color for all sub-obstructions (can be overridden)
        """
        super().__init__(position, color)
        self.components = []

        # No display list for composite - we'll use the components' lists
        self.display_list = None

    def add_component(self, obstruction_class, offset_position, *args, **kwargs):
        """
        Add a component obstruction to this composite.

        Args:
            obstruction_class: The class of obstruction to create
            offset_position: Position offset relative to composite's position
            *args, **kwargs: Arguments to pass to the obstruction constructor

        Returns:
            The created component obstruction
        """
        # If no color specified, use the composite's color
        if 'color' not in kwargs:
            kwargs['color'] = self.color

        # Calculate absolute position
        abs_position = np.array(self.position) + np.array(offset_position)

        # Create the component
        component = obstruction_class(abs_position, *args, **kwargs)
        self.components.append(component)
        return component

    def _draw_shape(self):
        """Draw shape - not used for composite as we render components directly."""
        pass

    def render(self):
        """Render all component obstructions."""
        for component in self.components:
            component.render()

    def delete(self):
        """Clean up OpenGL resources for all components."""
        for component in self.components:
            component.delete()