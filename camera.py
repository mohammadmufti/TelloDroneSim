from OpenGL.GLU import gluLookAt

class Camera:
    def __init__(self, eye_x, eye_y, eye_z, target_x, target_y, target_z, up_x, up_y, up_z):
        self.eye_position = (eye_x, eye_y, eye_z)
        self.target_position = (target_x, target_y, target_z)
        self.up_vector = (up_x, up_y, up_z)

    def apply(self):
        """Apply the camera's view transformation."""
        gluLookAt(
            *self.eye_position,
            *self.target_position,
            *self.up_vector
        )