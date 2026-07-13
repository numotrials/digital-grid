# Solar inverter simulator

## Step 1: "The Dumb Solar Inverter"

This inverter knows one thing: **Current Power Output**

Assume it is always sunny.

If the inverter is producing 5 kW, telemetry would be:

```json
{
    "power": 5.0,
    "status": "Generating"
}
```

Commands:

* start
* stop

## Step 2: Time behavior

Publish power every second.

If started:

* Publish the configured output power every second.

If stopped:

* Publish zero power.

## Step 3: Introduce Solar Irradiance

Power is now derived from sunlight.

```
power = rated_power × irradiance
```

Where irradiance is between 0.0 and 1.0.

Example:

```
Rated Power = 10 kW

Irradiance = 0.75

Power = 7.5 kW
```

## Step 4: Day/Night Cycle

Introduce the concept of time.

The inverter should:

* Produce zero power at night.
* Ramp up after sunrise.
* Reach peak output around noon.
* Ramp down towards sunset.

A simple sine curve is sufficient for the first implementation.

## Step 5: Temperature Effects

Solar panels become less efficient as temperature increases.

Example:

```
Ambient = 25°C

Panel Temperature = 45°C

Efficiency = 96%
```

Reduce generated power accordingly.

## Step 6: Inverter Limits

The inverter cannot produce more than its rated capacity.

Example:

```
PV Array could generate: 12 kW

Inverter Rating: 10 kW

Reported Output: 10 kW
```

Also prevent negative power values.

## Step 7: Grid Availability

Introduce grid status.

If the grid is unavailable:

* Stop exporting power.
* Change status to "Grid Lost".

When the grid returns:

* Resume normal generation.

## Step 8: Alarms

Generate alarm events for common conditions.

Examples:

* High Temperature
* Grid Lost
* Low Irradiance
* Inverter Fault
* Overload

## Example Final Telemetry

```json
{
    "power": 8.3,
    "rated_power": 10,
    "irradiance": 0.87,
    "panel_temperature": 42,
    "ambient_temperature": 31,
    "efficiency": 97.1,
    "energy_today": 48.6,
    "energy_total": 12452.8,
    "status": "Generating",
    "grid_status": "Connected",
    "fault": "None"
}
```
