# test_meter.py
import unittest
from meter import DumbSmartMeter


class TestDumbSmartMeter(unittest.TestCase):

    def setUp(self):
        # Runs before every test method - gives each test a fresh meter
        self.meter = DumbSmartMeter(load_kw=2.5)

    def test_initial_state_is_disconnected(self):
        telemetry = self.meter.telemetry()
        self.assertEqual(telemetry["status"], "Disconnected")
        self.assertEqual(telemetry["power"], 0.0)

    def test_connect_sets_status_connected(self):
        telemetry = self.meter.connect()
        self.assertEqual(telemetry["status"], "Connected")

    def test_connect_reports_correct_power(self):
        telemetry = self.meter.connect()
        self.assertEqual(telemetry["power"], 2.5)

    def test_disconnect_sets_status_disconnected(self):
        self.meter.connect()
        telemetry = self.meter.disconnect()
        self.assertEqual(telemetry["status"], "Disconnected")

    def test_disconnect_zeroes_power(self):
        self.meter.connect()
        telemetry = self.meter.disconnect()
        self.assertEqual(telemetry["power"], 0.0)

    def test_different_load_value(self):
        meter = DumbSmartMeter(load_kw=5.75)
        telemetry = meter.connect()
        self.assertEqual(telemetry["power"], 5.75)

    def test_telemetry_keys_present(self):
        telemetry = self.meter.telemetry()
        self.assertIn("power", telemetry)
        self.assertIn("status", telemetry)


if __name__ == "__main__":
    unittest.main()