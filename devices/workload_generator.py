from devices.event_detector import SensorEvent
from shared.schemas import Workload


class WorkloadGenerator:
    """Converts detected IoT events into computational workloads."""

    def __init__(self):
        self.workload_counter = 0

    def generate(self, event: SensorEvent) -> Workload:
        """Generate a workload based on the detected event severity."""

        self.workload_counter += 1

        # Default requirements
        cpu_required = 1.0
        memory_required = 256.0
        latency_requirement = 200.0
        energy_requirement = 10.0
        priority = 2
        model_confidence = 0.80

        # Adjust workload according to event severity
        if event.severity == "medium":
            cpu_required = 1.0
            memory_required = 256.0
            latency_requirement = 200.0
            energy_requirement = 10.0
            priority = 2
            model_confidence = 0.80

        elif event.severity == "high":
            cpu_required = 1.5
            memory_required = 512.0
            latency_requirement = 120.0
            energy_requirement = 15.0
            priority = 4
            model_confidence = 0.88

        elif event.severity == "critical":
            cpu_required = 2.5
            memory_required = 1024.0
            latency_requirement = 80.0
            energy_requirement = 25.0
            priority = 5
            model_confidence = 0.95

        return Workload(
            id=f"workload-{self.workload_counter:04d}",
            source_device_id=event.device_id,
            type="predictive_maintenance",
            cpu_required=cpu_required,
            memory_required=memory_required,
            data_size=5.0,
            latency_requirement=latency_requirement,
            energy_requirement=energy_requirement,
            priority=priority,
            model_confidence=model_confidence,
        )


if __name__ == "__main__":
    from devices.industrial_sensor import IndustrialSensor
    from devices.event_detector import EventDetector

    sensor = IndustrialSensor("industrial-001")
    detector = EventDetector()
    generator = WorkloadGenerator()

    # Test a medium-severity event
    print("Testing medium-severity workload...")

    sensor.temperature = 62.0
    sensor.vibration = 1.6

    event = detector.detect(sensor)

    if event:
        print("Event:")
        print(event)

        workload = generator.generate(event)

        print("\nGenerated workload:")
        print(workload)

    # Test a critical event
    print("\n\nTesting critical-severity workload...")

    sensor.temperature = 75.0
    sensor.vibration = 2.5

    event = detector.detect(sensor)

    if event:
        print("Event:")
        print(event)

        workload = generator.generate(event)

        print("\nGenerated workload:")
        print(workload)