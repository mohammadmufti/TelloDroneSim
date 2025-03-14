import pygame
from drone import Drone
from visuals import Visualizer
from obstruction_visuals import create_obstructions
from motion_planner import MotionPlanner
from collision_detector import CollisionDetector
from config import (FRAME_RATE, LINEAR_ACCEL, ANGULAR_ACCEL, MIN_SPEED)

class Simulator:
    def __init__(self, commands, weather_data=None):
        self.drone = Drone()
        self.visualizer = Visualizer()
        self.motion_planner = MotionPlanner(self.drone, LINEAR_ACCEL, ANGULAR_ACCEL)
        self.commands = commands
        self.target_state = self.drone.get_state()
        self.current_state = self.target_state.copy()
        self.frame_rate = FRAME_RATE
        self.linear_accel = LINEAR_ACCEL
        self.angular_accel = ANGULAR_ACCEL
        self.obstructions = create_obstructions()
        self.collision_detector = CollisionDetector(self.obstructions)

    def execute_commands(self, clock, sim_start_time):
        print("\n*****************************\n")
        print("Starting 3D Drone Simulator...")
        current_time = sim_start_time
        elapsed_since_start = 0
        command_count = 0
        command_start_times = [0]
        for i, (cmd, delay) in enumerate(self.commands[1:], 1):
            command_start_times.append(command_start_times[i - 1] + self.commands[i - 1][1])

        # Track active animation
        active_animation = None  # (cmd, total_time, elapsed_time, start_state, target_state, accel_time, coast_time)

        while self.visualizer.is_running() and (command_count < len(self.commands) or active_animation):
            delta_time = clock.tick(self.frame_rate) / 1000.0
            elapsed_since_start += delta_time
            current_time = sim_start_time + elapsed_since_start
            is_busy = active_animation is not None

            # Check for new command at this time
            if command_count < len(self.commands):
                cmd, delay = self.commands[command_count]
                start_time = command_start_times[command_count]
                if elapsed_since_start >= start_time:
                    command_count += 1
                    if is_busy:
                        print(f"[{command_count}] [{cmd}] ignored")
                    else:
                        response = self.drone.execute_command(cmd)
                        print(f"[{command_count}] {cmd}: {response}")
                        self.target_state = self.drone.get_state()
                        colliding_obstruction = self.collision_detector.check_path_collision(self.current_state,
                                                                                             self.target_state)
                        if colliding_obstruction:
                            pos_x, pos_y, pos_z = colliding_obstruction.position
                            print(f"***[{command_count}] [{cmd}] collides at [{pos_x}, {pos_y}, {pos_z}]***")

                        movement_commands = {"takeoff", "land", "up", "down", "left", "right", "forward", "back", "cw",
                                             "ccw", "flip", "go"}
                        if cmd.split()[0].lower() in movement_commands:
                            start_state = self.current_state.copy()
                            max_speed = max(self.drone.speed, MIN_SPEED)
                            total_time = self.motion_planner.calculate_move_time(cmd, start_state, self.target_state,
                                                                                 max_speed)
                            accel_time = min(max_speed / self.linear_accel, total_time / 2)
                            coast_time = max(0, total_time - 2 * accel_time)
                            if total_time > 0:
                                active_animation = (
                                cmd, total_time, 0, start_state, self.target_state, accel_time, coast_time)

            # Update active animation
            if active_animation:
                cmd, total_time, elapsed_time, start_state, target_state, accel_time, coast_time = active_animation
                elapsed_time += delta_time
                if elapsed_time >= total_time:
                    self.current_state = target_state.copy()
                    active_animation = None
                else:
                    self.current_state = self.motion_planner.interpolate_state(
                        start_state.copy(), target_state, elapsed_time, total_time, accel_time, coast_time
                    )
                    active_animation = (cmd, total_time, elapsed_time, start_state, target_state, accel_time, coast_time)

            self.drone.update_battery(current_time)
            self.visualizer.render(self.current_state, self.obstructions)
            pygame.event.pump()

        print("Commands completed.")

    def analyze_commands(self):
        """Analyze commands in advance to predict ignores and suggest delays without altering state."""
        print("Analyzing command sequence...")
        command_start_times = [0]
        for i, (cmd, delay) in enumerate(self.commands[1:], 1):
            command_start_times.append(command_start_times[i - 1] + self.commands[i - 1][1])

        # Create a temporary drone instance for analysis
        from drone import Drone  # Ensure this import is at the top of your file
        temp_drone = Drone()  # Fresh drone instance
        temp_drone.state = self.current_state.copy()  # Start from current state
        temp_motion_planner = MotionPlanner(temp_drone, self.linear_accel, self.angular_accel)

        active_until = 0  # Time when the drone is no longer busy
        issues_found = False
        analysis_state = self.current_state.copy()  # Track state changes during analysis

        for i, ((cmd, delay), start_time) in enumerate(zip(self.commands, command_start_times)):
            # Calculate animation time using temporary drone
            max_speed = max(temp_drone.speed, MIN_SPEED)
            temp_drone.execute_command(cmd)  # Update temp drone state
            target_state = temp_drone.get_state()

            movement_commands = {"takeoff", "land", "up", "down", "left", "right", "forward", "back", "cw", "ccw",
                                 "flip", "go"}
            command = cmd.split()[0].lower()
            if command in movement_commands:
                total_time = temp_motion_planner.calculate_move_time(cmd, analysis_state, target_state, max_speed)
            else:
                total_time = 0

            # Check if this command starts while drone is busy
            if start_time < active_until:
                issues_found = True
                print(f"[{i + 1}] [{cmd}] [{delay:.5f}] - previous command delay too short!")
                if i > 0:
                    prev_cmd, prev_delay = self.commands[i - 1]
                    required_delay = active_until - command_start_times[i - 1]
                    print(
                        f"  Suggestion: Increase delay for [{prev_cmd}] from {prev_delay:.5f} to {required_delay:.5f} seconds")
            else:
                if total_time > 0:
                    active_until = start_time + total_time
                    analysis_state = target_state.copy()  # Update analysis state

            # Reset temp_drone state for next iteration
            temp_drone.state = analysis_state.copy()

        if not issues_found:
            print("Commands expected to proceed smoothly")

    def render_loop(self, clock):
        """Keep window open and continue rendering after commands are executed."""
        print("Commands completed. Close the window or press Escape to exit.")
        while self.visualizer.is_running():
            delta_time = clock.tick(self.frame_rate) / 1000.0
            current_time = pygame.time.get_ticks() / 1000.0
            self.drone.update_battery(current_time)
            self.visualizer.render(self.current_state, self.obstructions)
            pygame.event.pump()

    def run(self):
        """Run the simulation by executing commands and maintaining the render loop."""
        clock = pygame.time.Clock()
        sim_start_time = pygame.time.get_ticks() / 1000.0

        # Analyze commands before execution
        self.analyze_commands()

        # Run Commands + Sim
        self.execute_commands(clock, sim_start_time)
        self.render_loop(clock)

        self.visualizer.quit()
        print("Simulation ended.")