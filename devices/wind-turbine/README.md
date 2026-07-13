# Wind turbine simulator

## Step 1: "The Dumb Wind Turbine"

This turbine knows one thing: **Current Power Output**

Assume the wind is constant.

If the turbine is producing 20 kW, telemetry would be:

```json
{
    "power": 20.0,
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

## Step 3: Introduce Wind Speed

Power is now derived from wind speed.

The simplest approximation is:

```text
power = rated_power × (wind_speed / rated_wind_speed)^3
```

Limit the result to the rated power of the turbine.

Example:

```text
Rated Power = 100 kW

Rated Wind Speed = 12 m/s

Current Wind Speed = 8 m/s

Power ≈ 30 kW
```

This demonstrates the cubic relationship between wind speed and generated power.

## Step 4: Cut-in and Cut-out Speeds

Real wind turbines only operate within a safe wind range.

Introduce three parameters:

* Cut-in speed (e.g. 3 m/s)
* Rated wind speed (e.g. 12 m/s)
* Cut-out speed (e.g. 25 m/s)

Behavior:

* Below cut-in: no generation
* Between cut-in and rated: increasing power
* Between rated and cut-out: constant rated power
* Above cut-out: turbine shuts down for safety

## Step 5: Wind Variability

Wind is never perfectly constant.

Introduce small random fluctuations every few seconds.

Optional improvements:

* Gusts
* Calm periods
* Daily wind profile
* Seasonal variation

This produces a more realistic power output.

## Step 6: Turbine Limits

Introduce operational limits.

Examples:

* Maximum rotor speed
* Maximum generator power
* Maximum yaw speed

Clamp generated power to the rated output.

Prevent negative power values.

## Step 7: Grid Availability

Introduce grid status.

If the grid is unavailable:

* Stop exporting power.
* Change status to "Grid Lost".

When the grid returns:

* Resume generation automatically.

## Step 8: Alarms

Generate alarm events for common operating conditions.

Examples:

* High Wind Shutdown
* Low Wind
* Overspeed
* Grid Lost
* Generator Fault
* Brake Activated
* High Bearing Temperature

## Example Final Telemetry

```json
{
    "power": 84.2,
    "rated_power": 100,
    "wind_speed": 11.3,
    "wind_direction": 245,
    "rotor_speed": 17.8,
    "ambient_temperature": 18,
    "energy_today": 426.8,
    "energy_total": 184523.4,
    "status": "Generating",
    "grid_status": "Connected",
    "fault": "None"
}
```
