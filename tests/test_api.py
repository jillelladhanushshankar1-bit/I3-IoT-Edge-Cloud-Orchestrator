"""Unit tests for the FastAPI state endpoint."""

import unittest
from fastapi.testclient import TestClient

from api.app import app


class TestStateEndpoint(unittest.TestCase):
    """Test suite for /api/state endpoint."""

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

        # Verify all expected top-level fields exist
        for field in expected_fields:
            self.assertIn(field, data, f"Missing required field: {field}")

        # Verify types and constraints
        self.assertIsInstance(data["resources"], list)
        self.assertIsInstance(data["workloads"], list)
        self.assertIsInstance(data["decisions"], list)
        self.assertIsInstance(data["events"], list)
        self.assertIsInstance(data["metrics"], list)
        self.assertIsInstance(data["updatedAt"], str)

        # Verify executionFeedback is empty (not invented)
        self.assertEqual(data["executionFeedback"], [])

        # Verify resources structure if present
        if data["resources"]:
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

    def test_health_check(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
