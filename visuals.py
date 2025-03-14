import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from drone_visuals import DroneRenderer
from grid_visuals import GridRenderer
from camera import Camera
from config import (
    VIEWPORT_WIDTH, VIEWPORT_HEIGHT, GRID_SIZE, GRID_STEP,
    CAMERA_EYE_X, CAMERA_EYE_Y, CAMERA_EYE_Z,
    CAMERA_TARGET_X, CAMERA_TARGET_Y, CAMERA_TARGET_Z,
    CAMERA_UP_X, CAMERA_UP_Y, CAMERA_UP_Z,
    FRAME_RATE, DRONE_WIDTH, DRONE_LENGTH, DRONE_HEIGHT, DRONE_SCALE_FACTOR,
    GRID_COLOR, GRID_LINE_COLOR, FIELD_OF_VIEW, NEAR_CLIP, FAR_CLIP, CLEAR_COLOR,
    WORLD_TO_PIXEL_SCALE_X,WORLD_TO_PIXEL_SCALE_Y)

class Visualizer:
    def __init__(self):
        try:
            pygame.init()
            self.display = (VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
            pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        except pygame.error as e:
            raise RuntimeError(f"Failed to initialize PyGame/OpenGL: {e}")
        pygame.display.set_caption("3D Drone Simulator")

        self.aspect_ratio = self.display[0] / self.display[1]  # Store aspect ratio
        self.scale = WORLD_TO_PIXEL_SCALE_X
        self._init_opengl()

        self.grid_renderer = GridRenderer(GRID_SIZE, GRID_STEP, GRID_COLOR, GRID_LINE_COLOR)
        self.drone_renderer = DroneRenderer(DRONE_WIDTH, DRONE_LENGTH, DRONE_HEIGHT, DRONE_SCALE_FACTOR)

        self.clock = pygame.time.Clock()
        self.fps = FRAME_RATE

        self.camera = Camera(
            CAMERA_EYE_X, CAMERA_EYE_Y, CAMERA_EYE_Z,
            CAMERA_TARGET_X, CAMERA_TARGET_Y, CAMERA_TARGET_Z,
            CAMERA_UP_X, CAMERA_UP_Y, CAMERA_UP_Z
        )

    def _init_opengl(self):
        """Initialize OpenGL settings."""
        glEnable(GL_DEPTH_TEST)
        glClearColor(*CLEAR_COLOR)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(FIELD_OF_VIEW, self.aspect_ratio, NEAR_CLIP, FAR_CLIP)
        glMatrixMode(GL_MODELVIEW)
        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        # Position the light (x, y, z, w) - w=1 for positional light
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 10.0, 1.0])  # Light directly above the origin
        # Set light properties
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.6, 0.6, 0.6, 1.0])  # Moderate white light
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.4, 1.0])  # Brighter but soft ambient
        # Enable material properties for objects
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        # Polished specular lighting
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.02, 0.02, 0.02, 1.0])  # Very faint specular
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.05, 0.05, 0.05, 1.0])  # Minimal reflection
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 1.0)  # Very low shininess
        # Enable fog for distance blurring
        glEnable(GL_FOG)
        glFogf(GL_FOG_MODE, GL_LINEAR)  # Linear fog for smooth fade
        glFogfv(GL_FOG_COLOR, CLEAR_COLOR)  # Match fog to background (e.g., gray or sky color)
        glFogf(GL_FOG_START, 500.0)  # Fog starts at 500 units
        glFogf(GL_FOG_END, 2000.0)  # Fully fogged by 2000 units

    def render(self, drone_state, obstructions):
        """
        Render the scene with drone and obstructions.

        Args:
            drone_state: Dictionary with the drone state
            obstructions: List of obstruction objects to render
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        self.camera.apply()
        glScale(1 / WORLD_TO_PIXEL_SCALE_X, 1 / WORLD_TO_PIXEL_SCALE_Y, 1 / WORLD_TO_PIXEL_SCALE_X)
        self.grid_renderer.render()

        for obstruction in obstructions:
            obstruction.render()

        self.drone_renderer.render(
            drone_state["x"], drone_state["y"],
            drone_state["z"], drone_state["yaw"]
        )

        pygame.display.flip()
        self.clock.tick(self.fps)
        actual_fps = self.clock.get_fps()
        pygame.display.set_caption(f"3D Drone Simulator - FPS: {actual_fps:.1f}")

    def is_running(self):
        """Check if the simulation should continue running."""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
        return True

    def quit(self):
        """Clean up resources and quit."""
        self.drone_renderer.cleanup()
        self.grid_renderer.cleanup()
        pygame.quit()