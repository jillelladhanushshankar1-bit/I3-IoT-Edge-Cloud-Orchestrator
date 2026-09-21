import random
from shared.schemas import Workload


class IndustrialSensor:
    """Simulates an industrial sensor measuring temperature and vibration."""

    def __init__(self, device_id: str):
        self.device_id = device_id

        # Starting normal operating conditions
        self.temperature = 30.0
        self.vibration = 0.20

        # Current operating state
        self.state = "normal"

    def update(self):
        """Update sensor readings based on the current operating state."""

        if self.state == "normal":
            self.temperature += random.uniform(-0.5, 0.5)
            self.vibration += random.uniform(-0.03, 0.03)

        elif self.state == "warning":
            self.temperature += random.uniform(0.2, 1.0)
            self.vibration += random.uniform(0.03, 0.08)

        elif self.state == "anomaly":
            self.temperature += random.uniform(0.5, 1.5)
            self.vibration += random.uniform(0.10, 0.25)

        # Keep sensor values within realistic limits
        self.temperature = max(20.0, min(self.temperature, 100.0))
        self.vibration = max(0.0, min(self.vibration, 10.0))

    def detect_event(self) -> bool:
        """Check whether the sensor readings indicate an abnormal condition."""

        return self.temperature >= 70.0 or self.vibration >= 2.0

    def generate_workload(self) -> Workload | None:
        """Generate a predictive-maintenance workload if an anomaly is detected."""

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
    sensor = IndustrialSensor("industrial-001")

    print("Normal state:")
    for _ in range(3):
        sensor.update()
        print(
            f"Temperature: {sensor.temperature:.2f} °C | "
            f"Vibration: {sensor.vibration:.2f}"
        )

    print("\nAnomaly detected!")

    sensor.state = "anomaly"

    # Simulate an abnormal machine condition
    sensor.temperature = 70.0
    sensor.vibration = 2.0

    print(
        f"Temperature: {sensor.temperature:.2f} °C | "
        f"Vibration: {sensor.vibration:.2f}"
    )

    if sensor.detect_event():
        workload = sensor.generate_workload()
        print("\nWorkload generated:")
        print(workload)