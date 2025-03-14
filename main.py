import time
from simulator import Simulator
from tello_wrapper import TelloWrapper
from weather import Weather
from config import (IS_SIM, HAS_WEATHER_DETAILS, IS_REAL_WEATHER, CRIT_BATTERY_LVL, ICAO, COMMANDS)

def main():
    weather = Weather(ICAO)
    if HAS_WEATHER_DETAILS:
        weather.print_summary()

    if IS_SIM:
        simulator = Simulator(COMMANDS, weather.get_weather_data() if IS_REAL_WEATHER else None)
        simulator.run()
    else:
        drone = TelloWrapper()
        battery = drone.execute_command("battery?")
        if battery.isdigit() and int(battery) < CRIT_BATTERY_LVL:
            print(f"Battery too low ({battery}%). Aborting.")
            return
        for cmd, delay in COMMANDS:
            response = drone.execute_command(cmd)
            print(f"{cmd}: {response}")
            time.sleep(delay)

if __name__ == "__main__":
    main()