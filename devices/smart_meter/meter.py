# meter.py
class DumbSmartMeter:
    def __init__(self, load_kw: float):
        self._load_kw = load_kw
        self._connected = False

    def connect(self):
        self._connected = True
        return self.telemetry()

    def disconnect(self):
        self._connected = False
        return self.telemetry()

    def telemetry(self):
        return {
            "power": round(self._load_kw, 2) if self._connected else 0.0,
            "status": "Connected" if self._connected else "Disconnected"
        }