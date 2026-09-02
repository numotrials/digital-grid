"""
Smart Meter Simulator - Step 1: "The Dumb Smart Meter"

Simulates a smart meter that reports a constant power consumption
and supports connect/disconnect commands.
"""

import json


class SmartMeter:
    def __init__(self, power_kw: float = 2.5):
        self._power_kw = power_kw
        self._connected = True

    def connect(self):
        """Handle the 'connect' command."""
        self._connected = True
        print("Meter connected.")

    def disconnect(self):
        """Handle the 'disconnect' command."""
        self._connected = False
        print("Meter disconnected.")

    def get_telemetry(self) -> dict:
        """Return current telemetry as a dict, matching the spec's JSON shape."""
        return {
            "power": self._power_kw if self._connected else 0.0,
            "status": "Connected" if self._connected else "Disconnected",
        }

    def get_telemetry_json(self) -> str:
        return json.dumps(self.get_telemetry(), indent=4)


def run_command(meter: SmartMeter, command: str):
    command = command.strip().lower()
    if command == "connect":
        meter.connect()
    elif command == "disconnect":
        meter.disconnect()
    elif command in ("status", "telemetry"):
        print(meter.get_telemetry_json())
    else:
        print(f"Unknown command: {command!r}")


def main():
    meter = SmartMeter(power_kw=2.5)

    print("Smart Meter Simulator - Step 1: The Dumb Smart Meter")
    print("Commands: connect, disconnect, status, quit\n")

    print("Initial telemetry:")
    print(meter.get_telemetry_json())

    while True:
        try:
            cmd = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            break

        if cmd.strip().lower() in ("quit", "exit"):
            break

        run_command(meter, cmd)


if __name__ == "__main__":
    main()