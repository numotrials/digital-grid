import unittest

from devices.battery.battery import Battery


class TestBattery(unittest.TestCase):
    def test_initial_state(self) -> None:
        battery = Battery(soc=60)

        self.assertEqual(battery.soc, 60)
        self.assertEqual(battery.status, "Idle")

    def test_charge(self) -> None:
        battery = Battery(soc=60)

        battery.charge()

        self.assertEqual(battery.status, "Charging")
        self.assertEqual(battery.soc, 60)

    def test_discharge(self) -> None:
        battery = Battery(soc=60)

        battery.discharge()

        self.assertEqual(battery.status, "Discharging")
        self.assertEqual(battery.soc, 60)

    def test_telemetry(self) -> None:
        battery = Battery(soc=60)

        self.assertEqual(
            battery.telemetry(),
            {
                "soc": 60,
                "status": "Idle",
            },
        )
