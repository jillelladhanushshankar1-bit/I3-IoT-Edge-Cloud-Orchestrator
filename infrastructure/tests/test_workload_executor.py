import unittest

from infrastructure.resources import CloudServer, IoTDeviceResource
from infrastructure.workload_executor import WorkloadExecutor
from shared.schemas import Workload


class TestWorkloadExecutor(unittest.TestCase):

    def setUp(self) -> None:
        self.executor = WorkloadExecutor()

        self.workload = Workload(
            id="workload-01",
            source_device_id="device-01",
            type="sensor_analysis",
            cpu_required=1.0,
            memory_required=256.0,
            data_size=10.0,
            latency_requirement=100.0,
            energy_requirement=20.0,
            priority=5,
            model_confidence=0.90,
        )

    def test_successful_execution(self) -> None:
        resource = IoTDeviceResource(
            id="device-01",
            cpu_capacity=2.0,
            memory_capacity=1024.0,
            latency=5.0,
            bandwidth=50.0,
            energy_level=100.0,
        )

        feedback = self.executor.execute(
            self.workload,
            resource,
        )

        self.assertTrue(feedback.success)
        self.assertEqual(feedback.workload_id, "workload-01")
        self.assertEqual(feedback.resource_id, "device-01")

    def test_insufficient_cpu(self) -> None:
        resource = IoTDeviceResource(
            id="device-02",
            cpu_capacity=0.5,
            memory_capacity=1024.0,
            latency=5.0,
            bandwidth=50.0,
            energy_level=100.0,
        )

        feedback = self.executor.execute(
            self.workload,
            resource,
        )

        self.assertFalse(feedback.success)

    def test_insufficient_memory(self) -> None:
        resource = IoTDeviceResource(
            id="device-03",
            cpu_capacity=2.0,
            memory_capacity=128.0,
            latency=5.0,
            bandwidth=50.0,
            energy_level=100.0,
        )

        feedback = self.executor.execute(
            self.workload,
            resource,
        )

        self.assertFalse(feedback.success)

    def test_execution_feedback_fields(self) -> None:
        resource = IoTDeviceResource(
            id="device-04",
            cpu_capacity=2.0,
            memory_capacity=1024.0,
            latency=5.0,
            bandwidth=50.0,
            energy_level=100.0,
        )

        feedback = self.executor.execute(
            self.workload,
            resource,
        )

        self.assertEqual(feedback.workload_id, self.workload.id)
        self.assertEqual(feedback.resource_id, resource.id)
        self.assertTrue(feedback.success)
        self.assertGreater(feedback.execution_time, 0.0)
        self.assertGreater(feedback.latency, 0.0)
        self.assertEqual(feedback.cpu_used, 1.0)
        self.assertEqual(feedback.memory_used, 256.0)
        self.assertGreater(feedback.energy_used, 0.0)
        self.assertEqual(feedback.data_transferred, 10.0)
        self.assertEqual(
            feedback.model_confidence,
            self.workload.model_confidence,
        )

    def test_resource_differences_affect_metrics(self) -> None:
        slow_resource = IoTDeviceResource(
            id="device-slow",
            cpu_capacity=1.0,
            memory_capacity=1024.0,
            latency=20.0,
            bandwidth=20.0,
            energy_level=100.0,
        )

        fast_resource = CloudServer(
            id="cloud-fast",
            cpu_capacity=8.0,
            memory_capacity=8192.0,
            latency=50.0,
            bandwidth=200.0,
            energy_level=100.0,
        )

        slow_feedback = self.executor.execute(
            self.workload,
            slow_resource,
        )

        fast_feedback = self.executor.execute(
            self.workload,
            fast_resource,
        )

        self.assertTrue(slow_feedback.success)
        self.assertTrue(fast_feedback.success)

        self.assertGreater(
            slow_feedback.execution_time,
            fast_feedback.execution_time,
        )

        self.assertGreater(
            slow_feedback.latency,
            fast_feedback.latency,
        )


if __name__ == "__main__":
    unittest.main()