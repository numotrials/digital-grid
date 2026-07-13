# Smart meter simulator

## Step 1: "The Dumb Smart Meter"

This smart meter knows one thing: **Current Power Consumption**

Assume the connected load is constant.

If the load is consuming 2.5 kW, telemetry would be:

```json
{
    "power": 2.5,
    "status": "Connected"
}
```

Commands:

* connect
* disconnect

## Step 2: Time behavior

Publish power every second.

If connected:

* Publish the configured load every second.

If disconnected:

* Publish zero power.

## Step 3: Introduce Energy Consumption

Energy is now derived from power over time.

```text
energy += power × time
```

Maintain a cumulative energy counter (kWh).

Example:

```text
Power = 2 kW

Time = 1 hour

Energy = 2 kWh
```

The energy counter should continuously increase while the load is connected.

## Step 4: Introduce Load Profiles

Real consumers do not draw constant power.

Implement simple load profiles such as:

* Residential
* Office
* Classroom
* Laboratory
* Factory

Each profile should have different consumption patterns throughout the day.

Example:

```text
08:00   0.8 kW

12:00   2.5 kW

18:00   4.2 kW

23:00   0.4 kW
```

## Step 5: Introduce Electrical Measurements

Derive additional telemetry.

Examples:

```text
Voltage = 230 V

Power = 2.3 kW

Current = Power / Voltage

Power Factor = 0.96

Frequency = 50 Hz
```

Voltage and frequency may include small random variations.

## Step 6: Import and Export Energy

Support bidirectional energy flow.

Examples:

* House consuming power from the grid
* House exporting excess solar generation

Maintain separate counters for:

* Import Energy (kWh)
* Export Energy (kWh)

Instantaneous power should be:

* Positive when importing
* Negative when exporting

## Step 7: Tariffs and Demand

Introduce electricity pricing.

Examples:

* Peak tariff
* Off-peak tariff
* Weekend tariff

Track:

* Current tariff
* Instantaneous cost
* Daily cost

Also record:

* Peak demand
* Maximum power observed

## Step 8: Alarms

Generate alarm events for common situations.

Examples:

* Over Voltage
* Under Voltage
* Over Current
* Reverse Energy Flow
* Meter Tamper
* Communication Failure

## Example Final Telemetry

```json
{
    "power": 3.8,
    "voltage": 231.6,
    "current": 16.4,
    "frequency": 49.98,
    "power_factor": 0.97,
    "energy_import": 1248.6,
    "energy_export": 62.4,
    "peak_demand": 6.3,
    "daily_cost": 428.75,
    "tariff": "Peak",
    "status": "Connected",
    "fault": "None"
}
```
