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
        """Analyze a device and create an event when abnormal conditions occur."""

        temperature = device.temperature
        vibration = device.vibration

        # No abnormal condition
        if temperature < 60.0 and vibration < 1.5:
            return None

        # Determine event type
        if temperature >= 70.0 and vibration >= 2.0:
            event_type = "thermal_vibration_anomaly"
            severity = "critical"
            description = (
                "High temperature and vibration detected. "
                "Possible machine failure."
            )

        elif temperature >= 70.0:
            event_type = "thermal_anomaly"
            severity = "high"
            description = (
                "Abnormally high machine temperature detected."
            )

        elif vibration >= 2.0:
            event_type = "vibration_anomaly"
            severity = "high"
            description = (
                "Abnormally high machine vibration detected."
            )

        else:
            event_type = "machine_warning"
            severity = "medium"
            description = (
                "Machine operating conditions are outside the normal range."
            )

        self.event_counter += 1

        return SensorEvent(
            event_id=f"event-{self.event_counter:04d}",
            device_id=device.device_id,
            event_type=event_type,
            severity=severity,
            temperature=temperature,
            vibration=vibration,
            description=description,
        )


if __name__ == "__main__":
    sensor = IndustrialSensor("industrial-001")
    detector = EventDetector()

    print("Testing normal condition...")

    sensor.temperature = 35.0
    sensor.vibration = 0.30

    event = detector.detect(sensor)

    if event is None:
        print("No event detected.")
    else:
        print(event)

    print("\nTesting warning condition...")

    sensor.temperature = 62.0
    sensor.vibration = 1.60

    event = detector.detect(sensor)

    if event is not None:
        print(event)

    print("\nTesting critical condition...")

    sensor.temperature = 75.0
    sensor.vibration = 2.50

    event = detector.detect(sensor)

    if event is not None:
        print(event)