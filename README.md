# Digital Power Grid

What if you could build a virtual city-sized power grid, simulate thousands of energy devices, and develop algorithms that help balance electricity demand in real time?

Such a system has two parts:

1. The electrical system, consisting of the grid and its devices
2. The information system, which monitors and controls the electrical system

This repository is a next-generation energy simulation platform that combines **Digital Twins**, **IoT**, **Renewable Energy Systems**, **Battery Storage**, **Smart Metering**, and **Artificial Intelligence** into a single environment.

Resulting in realistic software models of:

* Solar inverters and photovoltaic systems
* Battery Energy Storage Systems (BESS)
* Smart electricity meters
* EV charging infrastructure
* Grid-connected energy assets
* Consumer and industrial loads

These digital assets will communicate through an IoT platform and can be assembled to simulate anything from:

* A single smart building
* A university campus
* A residential community
* A city-wide energy network
* A national-scale power grid

### What You Will Build

* Device simulators and digital twins
* Telemetry and control systems
* Real-time data pipelines
* Load forecasting models
* Demand-response algorithms
* Energy optimization and distribution logic
* AI-based prediction and anomaly detection systems
* Interactive dashboards and visualization tools

### Technologies

Python • JavaScript/TypeScript • Docker • MQTT • REST APIs • ThingsBoard • Time-Series Databases • Machine Learning • Cloud Infrastructure • Power System Modeling

### Why Join?

This is not a classroom exercise. You will contribute to a platform that mirrors real-world energy infrastructure and provides a foundation for research and development in:

* Smart Grids
* Renewable Energy Integration
* EV Ecosystems
* Energy Management Systems
* Industrial IoT
* AI for Energy

**Design. Simulate. Predict. Optimize. Build the digital grid before it exists in the real world.**

## Setup

This project uses python with a hierarchical workspace.

History:

1. `uv init --bare --vcs git` done - this made the `pyproject.toml` at the base of the repo
1. `uv add --dev ...` done - to add development dependencies
1. `cd` to the folder where you want to start a sub-project. `uv init` there will add this to the parent workspace automatically
1. In the code, you can do `import devices.battery`
