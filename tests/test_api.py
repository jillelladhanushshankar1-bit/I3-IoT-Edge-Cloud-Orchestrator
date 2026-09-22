"""Unit tests for the FastAPI state and simulation endpoints."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.app import app
from api.state import simulation_state
from shared.schemas import Workload


class TestStateEndpoint(unittest.TestCase):
    """Test suite for /api/state and /api/simulation/step endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_get_state_returns_200_and_expected_fields(self) -> None:
        response = self.client.get("/api/state")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        expected_fields = [
            "resources",
            "workloads",
            "decisions",
            "executionFeedback",
            "events",
            "metrics",
            "updatedAt",
        ]

        # 1. Verify all expected top-level fields exist
        for field in expected_fields:
            self.assertIn(field, data, f"Missing required field: {field}")

        # 2. Verify types and constraints
        self.assertIsInstance(data["resources"], list)
        self.assertIsInstance(data["workloads"], list)
        self.assertIsInstance(data["decisions"], list)
        self.assertIsInstance(data["events"], list)
        self.assertIsInstance(data["metrics"], list)
        self.assertIsInstance(data["updatedAt"], str)
        self.assertIsInstance(data["executionFeedback"], list)

        # 3. Verify ExecutionFeedback appears in API state
        self.assertGreater(len(data["executionFeedback"]), 0)
        feedback = data["executionFeedback"][0]
        for key in [
            "workload_id",
            "resource_id",
            "success",
            "execution_time",
            "latency",
            "cpu_used",
            "memory_used",
            "energy_used",
            "data_transferred",
            "model_confidence",
        ]:
            self.assertIn(key, feedback)

        # 4. Verify resources structure
        self.assertGreater(len(data["resources"]), 0)
        first_resource = data["resources"][0]
        for key in [
            "id",
            "type",
            "cpu_capacity",
            "available_cpu",
            "cpu_utilization",
            "memory_capacity",
            "available_memory",
            "memory_utilization",
            "latency",
            "bandwidth",
            "energy_level",
        ]:
            self.assertIn(key, first_resource)

    def test_simulation_step_endpoint(self) -> None:
        """POST /api/simulation/step performs one cycle and returns updated state."""
        prev_feedback_count = len(simulation_state.execution_feedback)
        prev_workload_count = len(simulation_state.workloads)

        response = self.client.post("/api/simulation/step")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("executionFeedback", data)
        self.assertGreater(len(data["workloads"]), prev_workload_count)
        self.assertGreater(len(data["executionFeedback"]), prev_feedback_count)

        latest_feedback = data["executionFeedback"][-1]
        self.assertIn("workload_id", latest_feedback)
        self.assertIn("resource_id", latest_feedback)
        self.assertTrue(latest_feedback["success"])

    def test_workload_executor_is_called_during_step(self) -> None:
        """Verify WorkloadExecutor.execute is called during step()."""
        with patch.object(
            simulation_state.executor,
            "execute",
            wraps=simulation_state.executor.execute,
        ) as mock_execute:
            response = self.client.post("/api/simulation/step")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(mock_execute.called)

            # Check that the first argument was a Workload and second was a ComputeResource
            called_workload, called_resource = mock_execute.call_args[0]
            self.assertIsInstance(called_workload, Workload)
            self.assertEqual(called_resource.id, simulation_state.decisions[-1].destination)

    def test_resources_released_correctly_after_execution(self) -> None:
        """Verify reserved CPU and memory are released after execution completes."""
        # Perform a step
        simulation_state.step()

        # All resources should have their reserved capacity released
        for res in simulation_state.resource_manager.get_all_resources():
            self.assertEqual(
                res.available_cpu,
                res.cpu_capacity,
                f"Resource {res.id} available_cpu did not return to capacity",
            )
            self.assertEqual(
                res.available_memory,
                res.memory_capacity,
                f"Resource {res.id} available_memory did not return to capacity",
            )

    def test_infeasible_workload_skips_execution(self) -> None:
        """Verify that an infeasible workload (no destination) is not executed."""
        infeasible_workload = Workload(
            id="impossible-workload",
            source_device_id="sensor-test",
            type="sensor_analysis",
            cpu_required=9999.0,  # exceeds all capacity
            memory_required=999999.0,
            data_size=10.0,
            latency_requirement=5.0,
            energy_requirement=10.0,
            priority=5,
            model_confidence=0.9,
        )

        with patch.object(
            simulation_state.executor,
            "execute",
        ) as mock_execute:
            simulation_state.step(workload=infeasible_workload)
            mock_execute.assert_not_called()

    def test_health_check(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
