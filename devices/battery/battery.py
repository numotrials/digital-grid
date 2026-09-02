class Battery:
    """A simple battery digital twin."""

    def __init__(self, soc: float) -> None:
        self.soc = soc
        self.status = "Idle"

    def charge(self) -> None:
        """Set the battery status to charging."""
        self.status = "Charging"

    def discharge(self) -> None:
        """Set the battery status to discharging."""
        self.status = "Discharging"

    def telemetry(self) -> dict[str, float | str]:
        """Return the battery's current telemetry."""
        return {
            "soc": self.soc,
            "status": self.status,
        }
