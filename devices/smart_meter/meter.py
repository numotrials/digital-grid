class DumbSmartMeter:
    def __init__(self, power_kw=2.5):
        self._power = power_kw  # constant load, in kW
        self._connected = False

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def get_telemetry(self):
        return {
            "power": self._power,
            "status": "Connected" if self._connected else "Disconnected",
        }
