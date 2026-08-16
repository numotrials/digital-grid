import time


class WindTurbine:
    """Wind turbine digital twin."""

    def __init__(self, rated_power: float, rated_wind_speed: float):
        self.rated_power = rated_power
        self.rated_wind_speed = rated_wind_speed
        self.wind_speed = 0.0
        self.status = "Stopped"

    def start(self) -> None:
        self.status = "Generating"

    def stop(self) -> None:
        self.status = "Stopped"

    def set_wind_speed(self, wind_speed: float) -> None:
        self.wind_speed = max(0.0, wind_speed)

    def calculate_power(self) -> float:
        if self.status != "Generating":
            return 0.0

        power = self.rated_power * (
            self.wind_speed / self.rated_wind_speed
        ) ** 3

        return min(power, self.rated_power)

    def telemetry(self) -> dict[str, float | str]:
        return {
            "power": self.calculate_power(),
            "wind_speed": self.wind_speed,
            "status": self.status,
        }

    def run(self, seconds: int) -> None:
        """Publish telemetry every second."""
        for _ in range(seconds):
            print(self.telemetry())
            time.sleep(1)