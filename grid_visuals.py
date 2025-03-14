from OpenGL.GL import *

class GridRenderer:
    def __init__(self, size, step, plane_color, line_color):
        self.size = size
        self.step = step
        self.plane_color = plane_color
        self.line_color = line_color
        self.display_list = self._create_display_list()

    def _create_display_list(self):
        display_list = glGenLists(1)
        glNewList(display_list, GL_COMPILE)
        half_grid = self.size // 2

        # Draw the ground plane
        glBegin(GL_QUADS)
        glColor3f(*self.plane_color)
        glVertex3f(-half_grid, -half_grid, 0)
        glVertex3f(-half_grid, half_grid, 0)
        glVertex3f(half_grid, half_grid, 0)
        glVertex3f(half_grid, -half_grid, 0)
        glEnd()

        # Draw grid lines
        glBegin(GL_LINES)
        glColor3f(*self.line_color)
        for i in range(-half_grid, half_grid + 1, self.step):
            glVertex3f(i, -half_grid, 0)
            glVertex3f(i, half_grid, 0)
            glVertex3f(-half_grid, i, 0)
            glVertex3f(half_grid, i, 0)
        glEnd()

        glEndList()
        return display_list

    def render(self):
        glCallList(self.display_list)

    def cleanup(self):
        glDeleteLists(self.display_list, 1)