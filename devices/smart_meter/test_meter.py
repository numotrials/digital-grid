import unittest
from .meter import DumbSmartMeter


class TestDumbSmartMeter(unittest.TestCase):
    def setUp(self):
        self.meter = DumbSmartMeter()

    def test_connect_sets_status_connected(self):
        self.meter.connect()
        self.assertEqual(self.meter.get_telemetry()["status"], "Connected")

    def test_disconnect_sets_status_disconnected(self):
        self.meter.connect()
        self.meter.disconnect()
        self.assertEqual(self.meter.get_telemetry()["status"], "Disconnected")

    def test_telemetry_reports_constant_power(self):
        self.meter.connect()
        self.assertEqual(self.meter.get_telemetry()["power"], 2.5)

    def test_telemetry_matches_example(self):
        self.meter.connect()
        self.assertEqual(self.meter.get_telemetry(), {"power": 2.5, "status": "Connected"})
