import io
import json
import unittest
from unittest.mock import patch

from .stimulator_1 import SmartMeter, run_command, main


class TestSmartMeter(unittest.TestCase):
    def setUp(self):
        self.meter = SmartMeter(power_kw=2.5)

    def test_default_power_is_used(self):
        meter = SmartMeter()
        self.assertEqual(meter.get_telemetry()["power"], 2.5)

    def test_custom_power_is_used(self):
        meter = SmartMeter(power_kw=7.0)
        self.assertEqual(meter.get_telemetry()["power"], 7.0)

    def test_starts_connected(self):
        self.assertEqual(self.meter.get_telemetry()["status"], "Connected")

    def test_disconnect_sets_status_disconnected(self):
        self.meter.disconnect()
        self.assertEqual(self.meter.get_telemetry()["status"], "Disconnected")

    def test_disconnect_zeroes_power(self):
        self.meter.disconnect()
        self.assertEqual(self.meter.get_telemetry()["power"], 0.0)

    def test_connect_after_disconnect(self):
        self.meter.disconnect()
        self.meter.connect()
        self.assertEqual(self.meter.get_telemetry()["status"], "Connected")
        self.assertEqual(self.meter.get_telemetry()["power"], 2.5)

    def test_connect_prints_message(self):
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            self.meter.connect()
        self.assertIn("Meter connected.", captured.getvalue())

    def test_disconnect_prints_message(self):
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            self.meter.disconnect()
        self.assertIn("Meter disconnected.", captured.getvalue())

    def test_get_telemetry_json_is_valid_json(self):
        json_str = self.meter.get_telemetry_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed, self.meter.get_telemetry())


class TestRunCommand(unittest.TestCase):
    def setUp(self):
        self.meter = SmartMeter(power_kw=2.5)

    def test_connect_command(self):
        self.meter.disconnect()
        run_command(self.meter, "connect")
        self.assertEqual(self.meter.get_telemetry()["status"], "Connected")

    def test_disconnect_command(self):
        run_command(self.meter, "disconnect")
        self.assertEqual(self.meter.get_telemetry()["status"], "Disconnected")

    def test_status_command_prints_telemetry(self):
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            run_command(self.meter, "status")
        output = captured.getvalue()
        self.assertIn("power", output)
        self.assertIn("status", output)

    def test_telemetry_alias_command(self):
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            run_command(self.meter, "telemetry")
        self.assertIn("power", captured.getvalue())

    def test_command_is_case_insensitive_and_trimmed(self):
        self.meter.disconnect()
        run_command(self.meter, "  CONNECT  ")
        self.assertEqual(self.meter.get_telemetry()["status"], "Connected")

    def test_unknown_command_prints_message(self):
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            run_command(self.meter, "banana")
        self.assertIn("Unknown command", captured.getvalue())


class TestMain(unittest.TestCase):
    @patch("builtins.input", side_effect=["status", "quit"])
    def test_main_runs_status_then_quits(self, _mock_input):
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            main()
        output = captured.getvalue()
        self.assertIn("Smart Meter Simulator", output)
        self.assertIn("Initial telemetry", output)

    @patch("builtins.input", side_effect=["connect", "exit"])
    def test_main_accepts_exit_as_quit(self, mock_input):
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            main()
        self.assertIn("Meter connected.", captured.getvalue())

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_main_handles_keyboard_interrupt(self, mock_input):
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            main()
        self.assertIn("Smart Meter Simulator", captured.getvalue())


if __name__ == "__main__":
    unittest.main()
