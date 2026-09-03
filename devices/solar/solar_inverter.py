class SolarInverter:
    def __init__(self, rated_power):
        self.rated_power = rated_power
        self.power = 0
        self.status = "Stopped"

    def start(self):
        self.power = self.rated_power
        self.status = "Generating"

    def stop(self):
        self.power = 0
        self.status = "Stopped"

    def telemetry(self):
        return {
            "power": self.power,
            "status": self.status
        }