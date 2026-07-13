# Battery simulator

## Step 1: "The Dumb Battery"

This battery knows one thing: State of Charge (SOC)

If soc = 60 %, telemetry would be:

```json
{
    "soc": 60,
    "status": "Idle"
}
```

Commands:

- charge
- discharge

## Step 2: Time behavior

Publish SoC every second:

- If charging, soc += 0.1%
- If discharging soc -= 0.1%

Clamp to limits (0 / 100%)

## Step 3: Derive the SoC

`soc = energy / capacity`

## Step 4: Introduce input power

`soc += power_supplied * time`

## Step 5: Efficiency

95% efficiency means 10kWh supplied = 9.5 kWh stored

## Step 6: Discharge curves

Limit discharge energy as per battery characteristics

## Step 7: Battery health decreases over time

Reduce capacity over time

## Step 8: Alarms

Generate alarm events on temperature thresholds, deep discharge

## Example final telemetry

```json
{
    "soc": 62.4,
    "energy": 62.4,
    "capacity": 100,
    "power": -18,
    "status": "Discharging",
    "temperature": 31,
    "soh": 99.8,
    "cycles": 214
}
```
