from devices.industrial_sensor import IndustrialSensor
from devices.event_detector import EventDetector
from devices.workload_generator import WorkloadGenerator


class DeviceManager:
    """Manages virtual IoT devices and their event-to-workload pipeline."""

    def __init__(self):
        self.devices = []
        self.event_detector = EventDetector()
        self.workload_generator = WorkloadGenerator()

    def add_device(self, device):
        """Add a virtual device to the manager."""
        self.devices.append(device)

    def update_devices(self):
        """Update sensor readings for all registered devices."""
        for device in self.devices:
            device.update()

    def detect_events(self):
        """Detect events from all registered devices."""
        events = []

        for device in self.devices:
            event = self.event_detector.detect(device)

            if event is not None:
                events.append(event)

        return events

    def generate_workloads(self, events):
        """Convert detected events into computational workloads."""
        workloads = []

        for event in events:
            workload = self.workload_generator.generate(event)
            workloads.append(workload)

        return workloads


if __name__ == "__main__":
    manager = DeviceManager()

    sensor = IndustrialSensor("industrial-001")
    manager.add_device(sensor)

    print("Updating virtual devices...")

    # Simulate normal sensor readings
    for _ in range(3):
        manager.update_devices()

        print(
            f"Temperature: {sensor.temperature:.2f} °C | "
            f"Vibration: {sensor.vibration:.2f}"
        )

    # Simulate a critical machine condition
    sensor.temperature = 75.0
    sensor.vibration = 2.5

    print("\nDetecting events...")

    events = manager.detect_events()

    if events:
        for event in events:
            print("\nEvent detected:")
            print(event)

        workloads = manager.generate_workloads(events)

        print("\nGenerated workloads:")

        for workload in workloads:
            print(workload)

    else:
        print("No events detected.")