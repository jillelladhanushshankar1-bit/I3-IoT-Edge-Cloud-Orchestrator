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

    def run_simulation(self, cycles=12):
        """
        Run the complete IoT simulation for a number of cycles.

        Each cycle:
        1. Updates all virtual devices.
        2. Detects events.
        3. Generates workloads from detected events.

        Returns:
            A list containing sensor readings, events, and workloads
            generated during each simulation cycle.
        """

        simulation_results = []

        for cycle in range(1, cycles + 1):
            # Update all virtual sensors
            self.update_devices()

            # Detect events
            events = self.detect_events()

            # Generate workloads from detected events
            workloads = self.generate_workloads(events)

            # Store readings and results for this cycle
            cycle_readings = {}

            for device in self.devices:
                cycle_readings[device.device_id] = {
                    "temperature": device.temperature,
                    "vibration": device.vibration,
                    "state": device.state,
                    "has_anomaly": device.has_anomaly,
                }

            simulation_results.append(
                {
                    "cycle": cycle,
                    "readings": cycle_readings,
                    "events": events,
                    "workloads": workloads,
                }
            )

        return simulation_results


if __name__ == "__main__":
    manager = DeviceManager()

    # Deterministic sensor for hackathon demonstration
    sensor = IndustrialSensor(
        "industrial-001",
        demo_mode=True,
    )

    manager.add_device(sensor)

    print("Running complete IoT simulation...\n")

    results = manager.run_simulation(cycles=12)

    for result in results:
        cycle = result["cycle"]
        readings = result["readings"]["industrial-001"]
        events = result["events"]
        workloads = result["workloads"]

        print(
            f"Cycle {cycle:02d} | "
            f"Temperature: {readings['temperature']:.2f} °C | "
            f"Vibration: {readings['vibration']:.2f} | "
            f"State: {readings['state'].upper():8s}"
        )

        if events:
            for event in events:
                print(
                    f"  Event: {event.event_type} | "
                    f"Severity: {event.severity}"
                )

            for workload in workloads:
                print(
                    f"  Workload: {workload.id} | "
                    f"CPU: {workload.cpu_required} | "
                    f"Memory: {workload.memory_required} MB | "
                    f"Latency: {workload.latency_requirement} ms | "
                    f"Priority: {workload.priority}"
                )
        else:
            print("  Event: None")

        print()