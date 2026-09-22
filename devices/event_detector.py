from dataclasses import dataclass

from devices.industrial_sensor import IndustrialSensor


@dataclass
class SensorEvent:
    """Represents an event detected from a virtual IoT device."""

    event_id: str
    device_id: str
    event_type: str
    severity: str
    temperature: float
    vibration: float
    description: str


class EventDetector:
    """Detects and describes events from virtual IoT devices."""

    def __init__(self):
        self.event_counter = 0

    def detect(self, device: IndustrialSensor) -> SensorEvent | None:
        """Detect an event from the current sensor readings."""

        temperature = device.temperature
        vibration = device.vibration

        # Normal operating condition
        if temperature < 60.0 and vibration < 1.5:
            return None

        # Critical anomaly
        if temperature >= 70.0 and vibration >= 2.0:
            event_type = "thermal_vibration_anomaly"
            severity = "critical"
            description = (
                "High temperature and vibration detected. "
                "Possible machine failure."
            )

        # High anomaly
        elif temperature >= 70.0 or vibration >= 2.0:
            event_type = "thermal_or_vibration_anomaly"
            severity = "high"

            if temperature >= 70.0:
                description = "Abnormally high machine temperature detected."
            else:
                description = "Abnormally high machine vibration detected."

        # Medium warning
        else:
            event_type = "machine_warning"
            severity = "medium"
            description = (
                "Machine operating conditions are outside "
                "the normal range."
            )

        self.event_counter += 1

        event = SensorEvent(
            event_id=f"event-{self.event_counter:04d}",
            device_id=device.device_id,
            event_type=event_type,
            severity=severity,
            temperature=temperature,
            vibration=vibration,
            description=description,
        )

        device.latest_event = event

        return event


if __name__ == "__main__":
    sensor = IndustrialSensor("industrial-001", demo_mode=True)
    detector = EventDetector()

    print("Testing Event Detector...\n")

    for cycle in range(12):
        sensor.update()
        event = detector.detect(sensor)

        if event:
            print(
                f"Cycle {cycle + 1:02d} | "
                f"State: {sensor.state.upper():8s} | "
                f"Severity: {event.severity.upper():8s} | "
                f"Type: {event.event_type}"
            )
        else:
            print(
                f"Cycle {cycle + 1:02d} | "
                f"State: {sensor.state.upper():8s} | "
                f"Event: NONE"
            )