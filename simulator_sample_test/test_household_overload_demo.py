"""
Tests for the household overload demo simulation.

Covers every digital twin (BatteryTwin, LightingLoad, HeaterLoad, Inverter),
the pandapower network builder, and the step function that bridges the two
worlds. Test names stick to the electrical / physics vocabulary used by the
demo.
"""

import io
import unittest
from contextlib import redirect_stdout

import simulator_sample.household_overload_demo as demo


# ---------------------------------------------------------------------------
# BatteryTwin
# ---------------------------------------------------------------------------


class BatteryTwinDischargeTests(unittest.TestCase):
    """Energy store behaviour: state of charge and DC discharge."""

    def test_discharge_returns_dc_power_equal_to_discharge_rate(self):
        battery = demo.BatteryTwin(capacity_kwh=10.0, soc=0.8, discharge_kw=6.0)
        dc_power = battery.step(dt_hours=0.25)
        self.assertEqual(dc_power, 6.0)

    def test_discharge_reduces_state_of_charge_by_energy_ratio(self):
        capacity_kwh = 10.0
        discharge_kw = 6.0
        dt = 0.25
        battery = demo.BatteryTwin(capacity_kwh=capacity_kwh, soc=0.8, discharge_kw=discharge_kw)
        battery.step(dt)
        expected_soc = 0.8 - (discharge_kw * dt) / capacity_kwh
        self.assertAlmostEqual(battery.soc, expected_soc)

    def test_state_of_charge_drops_to_zero_when_energy_depleted(self):
        # 10 kWh capacity, 6 kW for 0.25h uses 1.5 kWh per tick -> 0.6 soc
        # lasts exactly 4 ticks.
        battery = demo.BatteryTwin(capacity_kwh=10.0, soc=0.6, discharge_kw=6.0)
        for _ in range(4):
            battery.step(0.25)
        self.assertEqual(battery.soc, 0.0)

    def test_depleted_battery_delivers_zero_dc_power(self):
        battery = demo.BatteryTwin(capacity_kwh=10.0, soc=0.0, discharge_kw=6.0)
        self.assertEqual(battery.step(dt_hours=0.25), 0.0)

    def test_discharge_below_zero_is_clamped_to_empty(self):
        battery = demo.BatteryTwin(capacity_kwh=10.0, soc=0.01, discharge_kw=100.0)
        battery.step(dt_hours=1.0)
        self.assertEqual(battery.soc, 0.0)
        self.assertEqual(battery.step(dt_hours=1.0), 0.0)


# ---------------------------------------------------------------------------
# LightingLoad
# ---------------------------------------------------------------------------


class LightingLoadTests(unittest.TestCase):
    """Always-on fixed lighting draw."""

    def test_lighting_returns_rated_active_power(self):
        lighting = demo.LightingLoad(power_kw=0.5)
        self.assertEqual(lighting.step(dt_hours=0.25), 0.5)

    def test_lighting_draw_is_independent_of_time_step(self):
        lighting = demo.LightingLoad(power_kw=0.5)
        self.assertEqual(lighting.step(dt_hours=0.0), 0.5)
        self.assertEqual(lighting.step(dt_hours=1.0), 0.5)


# ---------------------------------------------------------------------------
# HeaterLoad
# ---------------------------------------------------------------------------


class HeaterLoadTests(unittest.TestCase):
    """Always-on fixed resistive heater draw."""

    def test_heater_returns_rated_active_power(self):
        heater = demo.HeaterLoad(power_kw=25.0)
        self.assertEqual(heater.step(dt_hours=0.25), 25.0)

    def test_heater_draw_is_independent_of_time_step(self):
        heater = demo.HeaterLoad(power_kw=25.0)
        self.assertEqual(heater.step(dt_hours=0.0), 25.0)
        self.assertEqual(heater.step(dt_hours=2.0), 25.0)


# ---------------------------------------------------------------------------
# Inverter
# ---------------------------------------------------------------------------


class InverterConversionTests(unittest.TestCase):
    """DC-to-AC conversion, efficiency losses and rated capacity clipping."""

    def test_ac_output_reflects_efficiency_losses(self):
        inverter = demo.Inverter(rated_kva=5.0, efficiency=0.95)
        ac_power = inverter.convert(dc_power_kw=4.0)
        self.assertAlmostEqual(ac_power, 4.0 * 0.95)

    def test_unity_efficiency_passes_dc_through_unchanged(self):
        inverter = demo.Inverter(rated_kva=10.0, efficiency=1.0)
        self.assertEqual(inverter.convert(dc_power_kw=3.0), 3.0)

    def test_zero_dc_input_yields_zero_ac_output(self):
        inverter = demo.Inverter(rated_kva=5.0, efficiency=0.95)
        self.assertEqual(inverter.convert(dc_power_kw=0.0), 0.0)

    def test_output_above_rating_is_clipped_to_rated_kva(self):
        inverter = demo.Inverter(rated_kva=5.0, efficiency=0.95)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ac_power = inverter.convert(dc_power_kw=6.0)
        self.assertEqual(ac_power, 5.0)

    def test_clipping_announces_power_limiting_on_stdout(self):
        inverter = demo.Inverter(rated_kva=5.0, efficiency=0.95)
        buf = io.StringIO()
        with redirect_stdout(buf):
            inverter.convert(dc_power_kw=6.0)
        self.assertIn("clipping", buf.getvalue())
        self.assertIn("rated", buf.getvalue())

    def test_output_at_exactly_rating_is_not_clipped(self):
        inverter = demo.Inverter(rated_kva=5.0, efficiency=1.0)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ac_power = inverter.convert(dc_power_kw=5.0)
        self.assertEqual(ac_power, 5.0)
        self.assertEqual(buf.getvalue(), "")


# ---------------------------------------------------------------------------
# build_network
# ---------------------------------------------------------------------------


class BuildNetworkTopologyTests(unittest.TestCase):
    """Physical topology of the pandapower grid."""

    def setUp(self):
        self.net, self.load_lighting, self.load_heater, self.sgen_battery = demo.build_network()

    def test_network_has_two_buses(self):
        self.assertEqual(len(self.net.bus), 2)

    def test_buses_share_low_voltage_rating(self):
        self.assertTrue((self.net.bus.vn_kv == 0.4).all())

    def test_external_grid_anchors_the_supply_bus(self):
        self.assertEqual(len(self.net.ext_grid), 1)
        self.assertEqual(self.net.ext_grid.at[0, "bus"], self.net.bus.index[0])

    def test_single_service_line_connects_grid_to_house(self):
        self.assertEqual(len(self.net.line), 1)
        line = self.net.line.iloc[0]
        self.assertEqual(line.from_bus, self.net.bus.index[0])
        self.assertEqual(line.to_bus, self.net.bus.index[1])

    def test_service_line_has_thermal_limit(self):
        line = self.net.line.iloc[0]
        self.assertEqual(line.max_i_ka, 0.02)

    def test_two_loads_attached_to_house_bus(self):
        house_bus = self.net.bus.index[1]
        self.assertEqual(len(self.net.load), 2)
        self.assertTrue((self.net.load.bus == house_bus).all())

    def test_one_battery_sgen_attached_to_house_bus(self):
        house_bus = self.net.bus.index[1]
        self.assertEqual(len(self.net.sgen), 1)
        self.assertEqual(self.net.sgen.at[0, "bus"], house_bus)

    def test_all_loads_and_sgen_initialised_to_zero_power(self):
        self.assertEqual(self.net.load.at[self.load_lighting, "p_mw"], 0.0)
        self.assertEqual(self.net.load.at[self.load_heater, "p_mw"], 0.0)
        self.assertEqual(self.net.sgen.at[self.sgen_battery, "p_mw"], 0.0)

    def test_returned_indices_match_created_elements(self):
        self.assertEqual(self.net.load.at[self.load_lighting, "name"], "lighting")
        self.assertEqual(self.net.load.at[self.load_heater, "name"], "heater")
        self.assertEqual(self.net.sgen.at[self.sgen_battery, "name"], "battery_via_inverter")


# ---------------------------------------------------------------------------
# step_all
# ---------------------------------------------------------------------------


class StepAllPowerFlowTests(unittest.TestCase):
    """Coupling of digital twins to the pandapower power-flow solver."""

    def setUp(self):
        self.net, self.load_lighting, self.load_heater, self.sgen_battery = demo.build_network()

    def _make_assets(self):
        battery = demo.BatteryTwin(capacity_kwh=10.0, soc=0.8, discharge_kw=6.0)
        inverter = demo.Inverter(rated_kva=5.0, efficiency=0.95)
        lighting = demo.LightingLoad(power_kw=0.5)
        heater = demo.HeaterLoad(power_kw=25.0)
        return battery, inverter, lighting, heater

    def test_lighting_load_power_written_to_network_in_mw(self):
        battery, inverter, lighting, heater = self._make_assets()
        demo.step_all(
            self.net,
            self.load_lighting,
            self.load_heater,
            self.sgen_battery,
            battery,
            inverter,
            lighting,
            heater,
            dt_hours=0.25,
        )
        self.assertAlmostEqual(self.net.load.at[self.load_lighting, "p_mw"], 0.5 / 1000.0)

    def test_heater_load_power_written_to_network_in_mw(self):
        battery, inverter, lighting, heater = self._make_assets()
        demo.step_all(
            self.net,
            self.load_lighting,
            self.load_heater,
            self.sgen_battery,
            battery,
            inverter,
            lighting,
            heater,
            dt_hours=0.25,
        )
        self.assertAlmostEqual(self.net.load.at[self.load_heater, "p_mw"], 25.0 / 1000.0)

    def test_inverter_ac_output_written_to_battery_sgen_in_mw(self):
        battery, inverter, lighting, heater = self._make_assets()
        demo.step_all(
            self.net,
            self.load_lighting,
            self.load_heater,
            self.sgen_battery,
            battery,
            inverter,
            lighting,
            heater,
            dt_hours=0.25,
        )
        # 6 kW DC * 0.95 = 5.7 kW, clipped to rated 5.0 kVA
        self.assertAlmostEqual(self.net.sgen.at[self.sgen_battery, "p_mw"], 5.0 / 1000.0)

    def test_power_flow_is_solved_and_line_loading_recorded(self):
        battery, inverter, lighting, heater = self._make_assets()
        with redirect_stdout(io.StringIO()):
            demo.step_all(
                self.net,
                self.load_lighting,
                self.load_heater,
                self.sgen_battery,
                battery,
                inverter,
                lighting,
                heater,
                dt_hours=0.25,
            )
        self.assertIn("loading_percent", self.net.res_line.columns)
        self.assertGreater(self.net.res_line.at[0, "loading_percent"], 0.0)

    def test_oversized_heater_drives_line_into_overload(self):
        battery, inverter, lighting, heater = self._make_assets()
        with redirect_stdout(io.StringIO()):
            demo.step_all(
                self.net,
                self.load_lighting,
                self.load_heater,
                self.sgen_battery,
                battery,
                inverter,
                lighting,
                heater,
                dt_hours=0.25,
            )
        self.assertGreater(self.net.res_line.at[0, "loading_percent"], 100.0)

    def test_house_bus_voltage_stays_near_per_unit(self):
        battery, inverter, lighting, heater = self._make_assets()
        with redirect_stdout(io.StringIO()):
            demo.step_all(
                self.net,
                self.load_lighting,
                self.load_heater,
                self.sgen_battery,
                battery,
                inverter,
                lighting,
                heater,
                dt_hours=0.25,
            )
        vm = self.net.res_bus.at[1, "vm_pu"]
        self.assertGreater(vm, 0.0)
        self.assertLess(abs(vm - 1.0), 0.1)

    def test_step_decrements_battery_state_of_charge(self):
        battery, inverter, lighting, heater = self._make_assets()
        soc_before = battery.soc
        with redirect_stdout(io.StringIO()):
            demo.step_all(
                self.net,
                self.load_lighting,
                self.load_heater,
                self.sgen_battery,
                battery,
                inverter,
                lighting,
                heater,
                dt_hours=0.25,
            )
        self.assertLess(battery.soc, soc_before)

    def test_overload_message_printed_when_line_exceeds_rating(self):
        battery, inverter, lighting, heater = self._make_assets()
        buf = io.StringIO()
        with redirect_stdout(buf):
            demo.step_all(
                self.net,
                self.load_lighting,
                self.load_heater,
                self.sgen_battery,
                battery,
                inverter,
                lighting,
                heater,
                dt_hours=0.25,
            )
        self.assertIn("OVERLOAD", buf.getvalue())

    def test_no_overload_message_below_line_rating(self):
        # Tiny loads so the line stays well within its thermal limit.
        battery = demo.BatteryTwin(capacity_kwh=10.0, soc=0.8, discharge_kw=1.0)
        inverter = demo.Inverter(rated_kva=5.0, efficiency=1.0)
        lighting = demo.LightingLoad(power_kw=0.1)
        heater = demo.HeaterLoad(power_kw=0.1)
        buf = io.StringIO()
        with redirect_stdout(buf):
            demo.step_all(
                self.net,
                self.load_lighting,
                self.load_heater,
                self.sgen_battery,
                battery,
                inverter,
                lighting,
                heater,
                dt_hours=0.25,
            )
        self.assertNotIn("OVERLOAD", buf.getvalue())

    def test_power_flow_solver_refreshes_results_each_step(self):
        battery, inverter, lighting, heater = self._make_assets()
        with redirect_stdout(io.StringIO()):
            demo.step_all(
                self.net,
                self.load_lighting,
                self.load_heater,
                self.sgen_battery,
                battery,
                inverter,
                lighting,
                heater,
                dt_hours=0.25,
            )
        first_loading = self.net.res_line.at[0, "loading_percent"]
        first_voltage = self.net.res_bus.at[1, "vm_pu"]
        # A second step with a lighter load must yield genuinely recomputed
        # power-flow results, proving the solver ran again this tick.
        light_heater = demo.HeaterLoad(power_kw=1.0)
        with redirect_stdout(io.StringIO()):
            demo.step_all(
                self.net,
                self.load_lighting,
                self.load_heater,
                self.sgen_battery,
                battery,
                inverter,
                lighting,
                light_heater,
                dt_hours=0.25,
            )
        self.assertLess(
            self.net.res_line.at[0, "loading_percent"],
            first_loading,
            "line loading should drop with a lighter heater",
        )
        self.assertGreater(
            self.net.res_bus.at[1, "vm_pu"],
            first_voltage,
            "house voltage should recover with a lighter heater",
        )


# ---------------------------------------------------------------------------
# main (scenario driver)
# ---------------------------------------------------------------------------


class MainScenarioTests(unittest.TestCase):
    """The hardcoded four-tick household overload scenario."""

    def test_main_runs_four_ticks_without_error(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            demo.main()
        output = buf.getvalue()
        self.assertEqual(output.count("tick "), 4)

    def test_main_reports_overload_on_each_tick(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            demo.main()
        self.assertEqual(buf.getvalue().count("OVERLOAD"), 4)
