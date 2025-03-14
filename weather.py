from avwx import Metar

class Weather:
    def __init__(self, icao="KSEA"):
        """Initialize with an ICAO code for the weather station."""
        self.icao = icao
        self.obs = Metar(icao)
        self.weather_data = {}
        self.update()  # Fetch initial data

    def update(self):
        """Fetch and parse the latest METAR data."""
        self.obs.update()
        self.weather_data = {
            "wind_speed": self.obs.data.wind_speed.value if self.obs.data.wind_speed else 0,  # knots
            "wind_direction": self.obs.data.wind_direction.value if self.obs.data.wind_direction else 0,  # degrees
            "wind_gust": self.obs.data.wind_gust.value if self.obs.data.wind_gust else None,  # knots, optional
            "temperature": self.obs.data.temperature.value if self.obs.data.temperature else 20,  # Celsius
            "precipitation": bool("rain" in self.obs.data.wx_codes or "snow" in self.obs.data.wx_codes)  # Boolean
        }

    def get_weather_data(self):
        """Return the current weather data dictionary."""
        return self.weather_data

    def print_summary(self):
        """Print a formatted summary of the METAR data, split into lines."""
        summary = self.obs.summary
        summary_lines = summary.split(', ')  # Split summary into individual conditions
        print(f"METAR Summary for {self.obs.station}:")
        print(self.obs.raw)
        print("\n".join(summary_lines))  # Print each condition on a new line
        print("\n*****************************")
        print("*****************************\n")