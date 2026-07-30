"""
Illustrates the division of responsibility between:

1. DIGITAL TWINS   - pure Python objects that know nothing about the
                      electrical network. They just track their own
                      internal state (battery charge, whether a load
                      is on) and report a power value.

2. INVERTER        - also a digital twin, but its job is specifically
                      to convert the battery's DC output to AC and
                      cap it at its own rated capacity. It doesn't
                      know about pandapower either.

3. ELECTRICAL NETWORK (pandapower) - knows nothing about batteries or
                      heaters as "things". It only knows about buses,
                      lines, loads (p_mw) and generators (p_mw), and
                      solves the physics: currents, voltages, line
                      loading.

4. THE STEP FUNCTION - the only place that knows about BOTH worlds.
                      It reads power values out of the twins and
                      writes them into the network, then asks
                      pandapower to solve and reports on overload.

Everything below is hardcoded on purpose - one battery, one inverter,
one lighting load, one heater, one line. Not meant to be extended.
"""

import pandapower as pp


# ---------------------------------------------------------------------------
# 1. DIGITAL TWINS - no knowledge of the network at all
# ---------------------------------------------------------------------------


class BatteryTwin:
    """Tracks state of charge. Discharges at a fixed rate every step."""

    def __init__(self, capacity_kwh: float, soc: float, discharge_kw: float):
        self.capacity_kwh = capacity_kwh
        self.soc = soc  # 0.0 - 1.0
        self.discharge_kw = discharge_kw

    def step(self, dt_hours: float) -> float:
        """Discharge for this tick. Returns DC power output in kW."""
        if self.soc <= 0.0:
            return 0.0
        energy_used_kwh = self.discharge_kw * dt_hours
        self.soc -= energy_used_kwh / self.capacity_kwh
        self.soc = max(0.0, self.soc)
        return self.discharge_kw


class LightingLoad:
    """Fixed lighting draw, always on."""

    def __init__(self, power_kw: float):
        self.power_kw = power_kw

    def step(self, dt_hours: float) -> float:
        return self.power_kw


class HeaterLoad:
    """Fixed heater draw, always on."""

    def __init__(self, power_kw: float):
        self.power_kw = power_kw

    def step(self, dt_hours: float) -> float:
        return self.power_kw


# ---------------------------------------------------------------------------
# 2. INVERTER - also a digital twin. Converts DC battery power to AC,
#    capped at its own rated capacity. Still knows nothing about pandapower.
# ---------------------------------------------------------------------------


class Inverter:
    """Converts DC input power to AC output power, with losses and a cap."""

    def __init__(self, rated_kva: float, efficiency: float):
        self.rated_kva = rated_kva
        self.efficiency = efficiency

    def convert(self, dc_power_kw: float) -> float:
        ac_power_kw = dc_power_kw * self.efficiency
        if ac_power_kw > self.rated_kva:
            print(
                f"  [inverter] clipping output {ac_power_kw:.2f} kW "
                f"down to rated {self.rated_kva:.2f} kVA"
            )
            ac_power_kw = self.rated_kva
        return ac_power_kw


# ---------------------------------------------------------------------------
# 3. ELECTRICAL NETWORK - pandapower only knows buses/lines/loads/sgens.
#    It has never heard of a "battery" or a "heater".
# ---------------------------------------------------------------------------


def build_network() -> tuple[pp.pandapowerNet, pp.Int, pp.Int, pp.Int]:
    net = pp.create_empty_network()

    bus_grid = pp.create_bus(net, vn_kv=0.4, name="grid_bus")
    bus_house = pp.create_bus(net, vn_kv=0.4, name="house_bus")

    pp.create_ext_grid(net, bus=bus_grid, vm_pu=1.0)

    # Deliberately thin line (low max_i_ka) so it's easy to overload
    # for this demo - a real service line would be sized much larger.
    pp.create_line_from_parameters(
        net,
        from_bus=bus_grid,
        to_bus=bus_house,
        length_km=0.05,
        r_ohm_per_km=0.642,
        x_ohm_per_km=0.083,
        c_nf_per_km=210,
        max_i_ka=0.02,  # ~8.6 kW thermal limit at 0.4 kV, on purpose
    )

    # Placeholder p_mw=0.0 - the step function overwrites these every tick
    load_lighting = pp.create_load(net, bus=bus_house, p_mw=0.0, name="lighting")
    load_heater = pp.create_load(net, bus=bus_house, p_mw=0.0, name="heater")
    sgen_battery = pp.create_sgen(net, bus=bus_house, p_mw=0.0, name="battery_via_inverter")

    return net, load_lighting, load_heater, sgen_battery


# ---------------------------------------------------------------------------
# 4. THE STEP FUNCTION - the only code that touches both the twins and
#    the network. This is where "digital twin power value" becomes
#    "pandapower element power value".
# ---------------------------------------------------------------------------


def step_all(
    net,
    load_lighting_idx,
    load_heater_idx,
    sgen_battery_idx,
    battery: BatteryTwin,
    inverter: Inverter,
    lighting: LightingLoad,
    heater: HeaterLoad,
    dt_hours: float,
) -> None:
    # --- twins step on their own, oblivious to the network ---
    battery_dc_kw = battery.step(dt_hours)
    battery_ac_kw = inverter.convert(battery_dc_kw)
    lighting_kw = lighting.step(dt_hours)
    heater_kw = heater.step(dt_hours)

    # --- translate twin outputs into pandapower's units (MW) ---
    net.load.at[load_lighting_idx, "p_mw"] = lighting_kw / 1000.0
    net.load.at[load_heater_idx, "p_mw"] = heater_kw / 1000.0
    net.sgen.at[sgen_battery_idx, "p_mw"] = battery_ac_kw / 1000.0

    # --- network solves the physics, twins have no idea this happened ---
    pp.runpp(net)

    line_loading_pct = net.res_line.at[0, "loading_percent"]
    house_voltage_pu = net.res_bus.at[1, "vm_pu"]

    print(
        f"  battery soc={battery.soc:.3f}  "
        f"battery_ac={battery_ac_kw:.2f}kW  "
        f"lighting={lighting_kw:.2f}kW  heater={heater_kw:.2f}kW  "
        f"house_voltage={house_voltage_pu:.3f}pu  "
        f"line_loading={line_loading_pct:.1f}%"
    )

    if line_loading_pct > 100.0:
        print("  *** OVERLOAD: line loading exceeds 100% ***")


# ---------------------------------------------------------------------------
# MAIN - hardcoded scenario, run for a handful of ticks
# ---------------------------------------------------------------------------


def main() -> None:
    net, load_lighting_idx, load_heater_idx, sgen_battery_idx = build_network()

    battery = BatteryTwin(capacity_kwh=10.0, soc=0.8, discharge_kw=6.0)
    inverter = Inverter(rated_kva=5.0, efficiency=0.95)
    lighting = LightingLoad(power_kw=0.5)
    heater = HeaterLoad(power_kw=25.0)  # deliberately oversized to trigger overload

    dt_hours = 0.25  # 15-minute ticks
    for tick in range(4):
        print(f"tick {tick}:")
        step_all(
            net,
            load_lighting_idx,
            load_heater_idx,
            sgen_battery_idx,
            battery,
            inverter,
            lighting,
            heater,
            dt_hours,
        )


if __name__ == "__main__":
    main()
