"""Dummy weather station simulator."""

import json


class WeatherStation:
    """A simple weather station that reports ambient temperature."""

    def __init__(self, temperature: float = 30.0):
        self.temperature = temperature
        self.running = False

    def start(self) -> None:
        """Start the weather station."""
        self.running = True

    def stop(self) -> None:
        """Stop the weather station."""
        self.running = False

    def get_telemetry(self) -> dict:
        """Return the current weather telemetry."""
        return {
            "temperature": self.temperature,
            "status": "Online" if self.running else "Offline",
        }


if __name__ == "__main__":
    station = WeatherStation(temperature=30)

    print("Starting weather station...")
    station.start()

    print(json.dumps(station.get_telemetry(), indent=4))

    print("\nStopping weather station...")
    station.stop()

    print(json.dumps(station.get_telemetry(), indent=4))