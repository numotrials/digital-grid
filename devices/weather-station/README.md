# Weather station simulator

## Step 1: "The Dumb Weather Station"

This weather station knows one thing: **Ambient Temperature**

Assume the weather never changes.

If the temperature is 30°C, telemetry would be:

```json
{
    "temperature": 30,
    "status": "Online"
}
```

Commands:

* start
* stop

## Step 2: Time behavior

Publish weather telemetry every second.

If started:

* Publish the configured weather conditions every second.

If stopped:

* Stop publishing telemetry.

## Step 3: Introduce Multiple Measurements

Expand the telemetry to include:

* Temperature
* Humidity
* Wind Speed
* Wind Direction
* Solar Irradiance

Example:

```json
{
    "temperature": 30,
    "humidity": 62,
    "wind_speed": 5.3,
    "wind_direction": 245,
    "irradiance": 810
}
```

## Step 4: Daily Weather Patterns

Weather should vary throughout the day.

Examples:

* Temperature rises after sunrise.
* Irradiance follows the position of the sun.
* Humidity decreases during the afternoon.
* Wind speed changes gradually.

Simple sine curves are sufficient.

## Step 5: Random Variations

Introduce realistic randomness.

Examples:

* Passing clouds
* Wind gusts
* Small temperature fluctuations

Avoid sudden unrealistic jumps.

## Step 6: Weather Events

Generate larger events.

Examples:

* Cloudy
* Rain
* Storm
* Heatwave

These events should influence other simulators.

## Step 7: Forecast

Generate a simple short-term forecast.

Example:

```json
{
    "forecast_temperature": 32,
    "forecast_irradiance": 900,
    "forecast_wind_speed": 7,
    "confidence": 95
}
```

## Step 8: Alarms

Generate events for unusual conditions.

Examples:

* High Wind
* Heavy Rain
* Heat Warning
* Sensor Failure

## Example Final Telemetry

```json
{
    "temperature": 31.2,
    "humidity": 58,
    "wind_speed": 6.8,
    "wind_direction": 255,
    "irradiance": 845,
    "cloud_cover": 22,
    "rainfall": 0,
    "status": "Online"
}
```
