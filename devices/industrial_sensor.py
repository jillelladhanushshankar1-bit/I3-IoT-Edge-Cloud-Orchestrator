import random

from shared.schemas import Workload


class IndustrialSensor:
    """Simulates an industrial machine using temperature and vibration readings."""

    def __init__(self, device_id: str, demo_mode: bool = False):
        self.device_id = device_id
        self.demo_mode = demo_mode

        # Normal operating baseline
        self.normal_temperature = 30.0
        self.normal_vibration = 0.20

        # Current sensor readings
        self.temperature = self.normal_temperature
        self.vibration = self.normal_vibration

        # Current machine state
        self.state = "normal"

        # Indicates whether the current readings are abnormal
        self.has_anomaly = False
        self.latest_event = None

        # Used only by deterministic demo mode
        self._demo_cycle = 0

    def update(self):
        """Advance the machine simulation by one cycle."""

        if self.demo_mode:
            self._update_demo_mode()
        else:
            self._update_realistic_mode()

        self._update_state()

    def _update_realistic_mode(self):
        """Simulate natural sensor fluctuations and occasional degradation."""

        # Small normal fluctuations
        self.temperature += random.uniform(-0.8, 0.8)
        self.vibration += random.uniform(-0.04, 0.04)

        # Occasionally introduce a temporary increase in machine stress
        if random.random() < 0.15:
            self.temperature += random.uniform(1.0, 3.0)
            self.vibration += random.uniform(0.05, 0.20)

        # Occasionally allow the machine to recover toward normal
        if random.random() < 0.20:
            self.temperature += (self.normal_temperature - self.temperature) * 0.20
            self.vibration += (self.normal_vibration - self.vibration) * 0.20

        self._clamp_readings()

    def _update_demo_mode(self):
        """Produce a predictable sequence for hackathon demonstrations."""

        self._demo_cycle += 1

        if self._demo_cycle <= 4:
            # Normal operation
            self.temperature = 30.0 + random.uniform(-0.5, 0.5)
            self.vibration = 0.20 + random.uniform(-0.02, 0.02)

        elif self._demo_cycle <= 8:
            # Medium warning
            progress = self._demo_cycle - 4
            self.temperature = 50.0 + progress * 2.5
            self.vibration = 0.80 + progress * 0.12

        elif self._demo_cycle <= 11:
            # High anomaly
            progress = self._demo_cycle - 8
            self.temperature = 62.0 + progress * 2.5
            self.vibration = 1.55 + progress * 0.18

        else:
            # Critical anomaly
            self.temperature = 75.0 + random.uniform(-1.0, 1.0)
            self.vibration = 2.50 + random.uniform(-0.10, 0.10)

        self._clamp_readings()

    def _update_state(self):
        """Update the machine state from its current sensor readings."""

        if self.temperature >= 70.0 and self.vibration >= 2.0:
            self.state = "critical"
            self.has_anomaly = True

        elif self.temperature >= 70.0 or self.vibration >= 2.0:
            self.state = "high"
            self.has_anomaly = True

        elif self.temperature >= 60.0 or self.vibration >= 1.5:
            self.state = "warning"
            self.has_anomaly = True

        else:
            self.state = "normal"
            self.has_anomaly = False

    def _clamp_readings(self):
        """Keep simulated readings within reasonable physical limits."""

        self.temperature = max(20.0, min(self.temperature, 100.0))
        self.vibration = max(0.0, min(self.vibration, 10.0))

    def detect_event(self) -> bool:
        """Return whether the machine is currently experiencing an anomaly."""

        return self.has_anomaly

    def generate_workload(self) -> Workload | None:
        """
        Generate a predictive-maintenance workload if an anomaly is detected.

        This method is retained for compatibility with the existing interface.
        The main pipeline now uses EventDetector and WorkloadGenerator.
        """

        if not self.detect_event():
            return None

        return Workload(
            id=f"{self.device_id}-maintenance",
            source_device_id=self.device_id,
            type="predictive_maintenance",
            cpu_required=1.5,
            memory_required=512.0,
            data_size=5.0,
            latency_requirement=100.0,
            energy_requirement=20.0,
            priority=5,
            model_confidence=0.90,
        )


if __name__ == "__main__":
    sensor = IndustrialSensor("industrial-001", demo_mode=True)

    print("Running Industrial Sensor simulation...\n")

    for cycle in range(12):
        sensor.update()

        print(
            f"Cycle {cycle + 1:02d} | "
            f"Temperature: {sensor.temperature:5.2f} °C | "
            f"Vibration: {sensor.vibration:4.2f} | "
            f"State: {sensor.state.upper():8s} | "
            f"Anomaly: {sensor.has_anomaly}"
        )