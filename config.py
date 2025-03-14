"""Operator-modifiable configurations"""
IS_SIM = True  # Toggle if we are running simulation
HAS_WEATHER_DETAILS = True  # Toggle for if we want printed METAR details
IS_REAL_WEATHER = True  # Toggle if we want to simulate real weather from relevant station
CRIT_BATTERY_LVL = 20  # Minimal battery level considered hazardous (percent)
ICAO = 'KJFK'  # Select ICAO Weather Station code

"""Operator-modifiable commands"""
COMMANDS = [
    ("command", 0.5),
    ("takeoff", 3.0),
    ("left 400", .00001),
    ("right 400", 1),
    ("right 400", 6),
    ("right 400", 6),
    ("forward 200", 3.0),
    ("right 50", 3.0),
    ("right 200", 3.0),
    ("right 200", 3.0),
    ("left 200", 3.0),
    ("up 100", 3.0),
    ("left 200", 3.0),
    ("ccw 40", 3.0),
    ("forward 400", 6.0),
    ("up 110", 3.0),
    ("forward 400", 6.0),
    ("forward 400", 6.0),
    ("back 400", 6.0),
    ("land", 3.0),
    ("battery?", 0.5),
]

"""Configuration constants for the drone simulator."""
FRAME_RATE = 60  # Frames per second
LINEAR_ACCEL = 250  # cm/s² rw 200-400?
ANGULAR_ACCEL = 600  # degrees/s² rw peaks 720
DEFAULT_MOVE_TIME = 0.1  # Default time for invalid or zero-distance moves
FLIP_TIME = 1.0  # Time for flip command
TAKEOFF_TIME = 2.0  # Time for takeoff command
LAND_TIME = 2.5  # Time for land command
MIN_SPEED = 10  # Minimum speed to ensure movement

"""Drone specific constants - modifiable based on drone model"""
DRONE_DEFAULT_SPEED = 75  # cm/s rw 50-100
DRONE_INITIAL_BATTERY = 100.0  # percent
DRONE_IDLE_DRAIN_RATE = 0.02  # %/s rw 0.016–0.033 %/s
DRONE_FLYING_DRAIN_RATE = 0.128  # %/s
DRONE_HIGH_POWER_DRAIN_RATE = 0.2  # %/s
DRONE_INITIAL_X = 0  # cm, right is positive
DRONE_INITIAL_Y = -900  # cm, forward is positive
DRONE_INITIAL_Z = 0  # cm, up is positive
DRONE_INITIAL_YAW = 0
DRONE_WIDTH = 9.8   # cm (left to right)
DRONE_LENGTH = 9.25 # cm (back to front)
DRONE_HEIGHT = 4.1  # cm (bottom to top)
DRONE_SCALE_FACTOR = 2  # Multiplier for rendered size (e.g., 2× real size)
DRONE_BASE_COLOR = (0.8, 0.0, 0.0)  # Darker red for drone base
DRONE_BODY_COLOR = (1.0, 0.0, 0.0)  # Bright red for drone body

"""Visualizer (Operator Frame of Reference) constants"""
VIEWPORT_WIDTH = 1000  # New
VIEWPORT_HEIGHT = 600  # New
GRID_SIZE = 2000       # New, total width/height in cm (10m)
GRID_STEP = 50         # New, spacing between grid lines in cm
WORLD_TO_PIXEL_SCALE_X = GRID_SIZE / VIEWPORT_WIDTH
WORLD_TO_PIXEL_SCALE_Y = 2 #GRID_SIZE / VIEWPORT_HEIGHT
GRID_COLOR = (0.2, 0.2, 0.2)        # Dark gray for the ground plane
GRID_LINE_COLOR = (0.5, 0.5, 0.5)   # Light gray for grid lines
FIELD_OF_VIEW = 60  # Degrees
NEAR_CLIP = 1.0     # Near clipping plane
FAR_CLIP = 2500.0   # Far clipping plane
CLEAR_COLOR = (0.1, 0.1, 0.1, 1.0)  # Dark gray background
CAMERA_EYE_X = 0       # New
CAMERA_EYE_Y = -650    # New
CAMERA_EYE_Z = 80     # New
CAMERA_TARGET_X = 0    # New
CAMERA_TARGET_Y = 0    # New
CAMERA_TARGET_Z = 0    # New
CAMERA_UP_X = 0        # New
CAMERA_UP_Y = 0        # New
CAMERA_UP_Z = 1        # New

"""Operator Insertable Obstructions Instructions in obstruction_visuals"""