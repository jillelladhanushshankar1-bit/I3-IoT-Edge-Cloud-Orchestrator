import unittest

from devices.industrial_sensor import IndustrialSensor
from devices.event_detector import EventDetector
from devices.workload_generator import WorkloadGenerator
from devices.device_manager import DeviceManager


class TestIndustrialSensor(unittest.TestCase):

    def test_sensor_update_keeps_readings_valid(self):
        sensor = IndustrialSensor("test-sensor")

        for _ in range(20):
            sensor.update()

            self.assertGreaterEqual(sensor.temperature, 20.0)
            self.assertLessEqual(sensor.temperature, 100.0)

            self.assertGreaterEqual(sensor.vibration, 0.0)
            self.assertLessEqual(sensor.vibration, 10.0)

    def test_demo_mode_reaches_anomaly_states(self):
        sensor = IndustrialSensor("test-sensor", demo_mode=True)

        states = []

        for _ in range(12):
            sensor.update()
            states.append(sensor.state)

        self.assertIn("warning", states)
        self.assertIn("high", states)
        self.assertIn("critical", states)


class TestEventDetector(unittest.TestCase):

    def setUp(self):
        self.detector = EventDetector()

    def test_normal_readings_produce_no_event(self):
        sensor = IndustrialSensor("test-sensor")

        sensor.temperature = 30.0
        sensor.vibration = 0.2

        event = self.detector.detect(sensor)

        self.assertIsNone(event)

    def test_medium_event(self):
        sensor = IndustrialSensor("test-sensor")

        sensor.temperature = 62.0
        sensor.vibration = 1.6

        event = self.detector.detect(sensor)

        self.assertIsNotNone(event)
        self.assertEqual(event.severity, "medium")
        self.assertEqual(event.event_type, "machine_warning")

    def test_high_event(self):
        sensor = IndustrialSensor("test-sensor")

        sensor.temperature = 70.0
        sensor.vibration = 1.8

        event = self.detector.detect(sensor)

        self.assertIsNotNone(event)
        self.assertEqual(event.severity, "high")

    def test_critical_event(self):
        sensor = IndustrialSensor("test-sensor")

        sensor.temperature = 75.0
        sensor.vibration = 2.5

        event = self.detector.detect(sensor)

        self.assertIsNotNone(event)
        self.assertEqual(event.severity, "critical")
        self.assertEqual(event.event_type, "thermal_vibration_anomaly")

    def test_event_is_saved_as_latest_event(self):
        sensor = IndustrialSensor("test-sensor")

        sensor.temperature = 75.0
        sensor.vibration = 2.5

        event = self.detector.detect(sensor)

        self.assertEqual(sensor.latest_event, event)


class TestWorkloadGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = WorkloadGenerator()

    def create_event(self, severity):
        sensor = IndustrialSensor("test-sensor")

        if severity == "medium":
            sensor.temperature = 62.0
            sensor.vibration = 1.6
        elif severity == "high":
            sensor.temperature = 70.0
            sensor.vibration = 1.8
        else:
            sensor.temperature = 75.0
            sensor.vibration = 2.5

        detector = EventDetector()
        return detector.detect(sensor)

    def test_medium_workload(self):
        event = self.create_event("medium")
        workload = self.generator.generate(event)

        self.assertEqual(workload.cpu_required, 1.0)
        self.assertEqual(workload.memory_required, 256.0)
        self.assertEqual(workload.latency_requirement, 200.0)
        self.assertEqual(workload.priority, 2)

    def test_high_workload(self):
        event = self.create_event("high")
        workload = self.generator.generate(event)

        self.assertEqual(workload.cpu_required, 1.5)
        self.assertEqual(workload.memory_required, 512.0)
        self.assertEqual(workload.latency_requirement, 120.0)
        self.assertEqual(workload.priority, 4)

    def test_critical_workload(self):
        event = self.create_event("critical")
        workload = self.generator.generate(event)

        self.assertEqual(workload.cpu_required, 2.5)
        self.assertEqual(workload.memory_required, 1024.0)
        self.assertEqual(workload.latency_requirement, 80.0)
        self.assertEqual(workload.priority, 5)

    def test_critical_workload_requires_more_resources_than_medium(self):
        medium_event = self.create_event("medium")
        critical_event = self.create_event("critical")

        medium_workload = self.generator.generate(medium_event)
        critical_workload = self.generator.generate(critical_event)

        self.assertGreater(
            critical_workload.cpu_required,
            medium_workload.cpu_required,
        )

        self.assertGreater(
            critical_workload.memory_required,
            medium_workload.memory_required,
        )

        self.assertLess(
            critical_workload.latency_requirement,
            medium_workload.latency_requirement,
        )


class TestDeviceManager(unittest.TestCase):

    def test_complete_simulation(self):
        manager = DeviceManager()

        sensor = IndustrialSensor(
            "industrial-test",
            demo_mode=True,
        )

        manager.add_device(sensor)

        results = manager.run_simulation(cycles=12)

        self.assertEqual(len(results), 12)

        all_events = []

        for result in results:
            all_events.extend(result["events"])

        severities = {
            event.severity
            for event in all_events
        }

        self.assertIn("medium", severities)
        self.assertIn("high", severities)
        self.assertIn("critical", severities)

    def test_simulation_generates_workloads(self):
        manager = DeviceManager()

        sensor = IndustrialSensor(
            "industrial-test",
            demo_mode=True,
        )

        manager.add_device(sensor)

        results = manager.run_simulation(cycles=12)

        all_workloads = []

        for result in results:
            all_workloads.extend(result["workloads"])

        self.assertGreater(len(all_workloads), 0)

        for workload in all_workloads:
            self.assertEqual(
                workload.source_device_id,
                "industrial-test",
            )


if __name__ == "__main__":
    unittest.main()