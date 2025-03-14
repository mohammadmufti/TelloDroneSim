# TelloDroneSim
A Tello Drone Simulator

Running main runs simulator.

[config.py] Operator modifies config.py to provide a list of tuples (Tello SDK corresponding command, delay before sending next command in sequence). Operator can also configure values such as drone dimensions and speed to impact physics.

[obstruction_visuals.py] Operator modifies obstruction_visuals.py to code simple obstructions (physical elements that risk flight-path collisions).Operator can configure a list of obstructions to plan safe operation of sequential commands and modify accordingly.
