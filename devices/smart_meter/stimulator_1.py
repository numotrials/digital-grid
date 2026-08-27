class SmartMeter:
    """
    Step 1: The Dumb Smart Meter
    Knows one thing: Current Power Consumption (constant load).
    """

    def __init__(self, load_kw: float = 2.5):
        self._load_kw = load_kw
        self._connected = False

    def connect(self):
        """Connect the meter to the load."""
        self._connected = True

    def disconnect(self):
        """Disconnect the meter from the load."""
        self._connected = False

    def get_telemetry(self) -> dict:
        """Return current telemetry as per Step 1 spec."""
        return {
            "power": self._load_kw if self._connected else 0,
            "status": "Connected" if self._connected else "Disconnected"
        }


if __name__ == "__main__":
    meter = SmartMeter(load_kw=2.5)

    print("Before connecting:", meter.get_telemetry())

    meter.connect()
    print("After connecting:", meter.get_telemetry())

    meter.disconnect()
    print("After disconnecting:", meter.get_telemetry())