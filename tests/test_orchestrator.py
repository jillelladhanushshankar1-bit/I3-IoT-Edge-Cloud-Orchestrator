"""Unit tests for the I3 orchestrator module.

Tests are deterministic — no randomness, no timing, no external
dependencies.  Uses the standard-library ``unittest`` framework so
no third-party test package is required.
"""

import unittest

from shared.schemas import (
    ComputeResource,
    ExecutionFeedback,
    OrchestrationDecision,
    Workload,
)
from orchestrator import Orchestrator, ScoringConfig
from orchestrator.scoring import (
    compute_score,
    normalize_available,
    normalize_latency,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_workload(
    id="wl-1",
    cpu_required=2,
    memory_required=512,
    data_size=1,
    latency_requirement=5000,
    energy_requirement=50,
    priority=5,
    model_confidence=0.8,
    source_device_id="dev-1",
    type="image_processing",
) -> Workload:
    return Workload(
        id=id,
        source_device_id=source_device_id,
        type=type,
        cpu_required=cpu_required,
        memory_required=memory_required,
        data_size=data_size,
        latency_requirement=latency_requirement,
        energy_requirement=energy_requirement,
        priority=priority,
        model_confidence=model_confidence,
    )


def make_resource(
    id="res-1",
    type="edge",
    cpu_capacity=8,
    available_cpu=8,
    memory_capacity=4096,
    available_memory=4096,
    latency=10,
    bandwidth=100,
    energy_level=100.0,
) -> ComputeResource:
    return ComputeResource(
        id=id,
        type=type,
        cpu_capacity=cpu_capacity,
        available_cpu=available_cpu,
        memory_capacity=memory_capacity,
        available_memory=available_memory,
        latency=latency,
        bandwidth=bandwidth,
        energy_level=energy_level,
    )


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

class TestOrchestrator(unittest.TestCase):
    """Deterministic tests for the baseline orchestration engine."""

    # 1. A workload that can run on multiple resources and verify that one
    # resource is selected.
    def test_multiple_feasible_resources_selects_one(self):
        wl = make_workload()
        resources = [
            make_resource(id="edge-1", latency=10, available_cpu=8, available_memory=4096, bandwidth=50),
            make_resource(id="cloud-1", latency=30, available_cpu=16, available_memory=8192, bandwidth=100),
            make_resource(id="edge-2", latency=20, available_cpu=8, available_memory=4096, bandwidth=50),
        ]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertIsInstance(decision, OrchestrationDecision)
        self.assertIn(decision.destination, ("edge-1", "cloud-1", "edge-2"))
        # The edge node with lowest latency should score highest (lower
        # latency dominates per the configured weights).
        self.assertEqual(decision.destination, "edge-1")

    # 2. A workload that cannot run on a low-powered device but can run on
    # an edge node.
    def test_low_power_device_rejected_edge_accepted(self):
        wl = make_workload(cpu_required=4, memory_required=1024)
        resources = [
            make_resource(id="device-1", type="device", available_cpu=2, available_memory=512, latency=5),
            make_resource(id="edge-1", type="edge", available_cpu=8, available_memory=2048, latency=10),
        ]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertEqual(decision.destination, "edge-1")
        self.assertGreaterEqual(decision.score, 0)

    # 3. A high-latency resource being rejected when the workload has a
    # strict latency requirement.
    def test_high_latency_rejected_strict_latency(self):
        wl = make_workload(latency_requirement=20)
        resources = [
            make_resource(id="fast-1", latency=5),
            make_resource(id="slow-1", latency=50),
        ]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertEqual(decision.destination, "fast-1")

    # 4. A resource with insufficient CPU being rejected.
    def test_insufficient_cpu_rejected(self):
        wl = make_workload(cpu_required=8)
        resources = [
            make_resource(id="weak-1", available_cpu=2),
            make_resource(id="strong-1", available_cpu=16),
        ]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertEqual(decision.destination, "strong-1")

    # 5. A resource with insufficient memory being rejected.
    def test_insufficient_memory_rejected(self):
        wl = make_workload(memory_required=4096)
        resources = [
            make_resource(id="low-mem-1", available_memory=512),
            make_resource(id="high-mem-1", available_memory=8192),
        ]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertEqual(decision.destination, "high-mem-1")

    # 6. A workload for which no resource is feasible.
    def test_no_feasible_resources(self):
        wl = make_workload(cpu_required=16, memory_required=16384, latency_requirement=5)
        resources = [
            make_resource(id="edge-1", available_cpu=4, available_memory=2048, latency=10),
            make_resource(id="cloud-1", available_cpu=8, available_memory=8192, latency=50),
        ]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertIsInstance(decision, OrchestrationDecision)
        self.assertEqual(decision.destination, "")
        self.assertEqual(decision.score, -1.0)
        self.assertIn("No feasible resource", decision.reason)

    # 7. Verify that the returned result is an OrchestrationDecision.
    def test_return_type_is_orchestration_decision(self):
        wl = make_workload()
        resources = [make_resource()]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertIsInstance(decision, OrchestrationDecision)

    # 8. Verify that the selected destination is one of the supplied
    # resources.
    def test_destination_is_supplied_resource(self):
        wl = make_workload()
        resources = [make_resource(id="r1"), make_resource(id="r2")]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertIn(decision.destination, ("r1", "r2"))

    # ------------------------------------------------------------------
    # Bonus edge cases
    # ------------------------------------------------------------------

    def test_empty_resource_list(self):
        wl = make_workload()
        orch = Orchestrator()
        decision = orch.decide(wl, [])

        self.assertEqual(decision.destination, "")
        self.assertEqual(decision.score, -1.0)

    def test_zero_bandwidth_rejected(self):
        wl = make_workload(data_size=10, latency_requirement=100)
        resources = [
            make_resource(id="zero-bw", bandwidth=0),
            make_resource(id="has-bw", bandwidth=200),  # transfer = 50 ms <= 100 ms
        ]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertEqual(decision.destination, "has-bw")

    def test_transfer_time_exceeds_latency_rejected(self):
        """Data size / bandwidth > latency_requirement → rejected."""
        # 10 MB data, bandwidth=5 MB/s → transfer time = 2 s = 2000 ms > 1000 ms budget
        # bandwidth=20 MB/s → transfer time = 0.5 s = 500 ms <= 1000 ms budget
        wl = make_workload(data_size=10, latency_requirement=1000)
        resources = [
            make_resource(id="slow-transfer", bandwidth=5, latency=1),  # 2000 ms > 1000 ms
            make_resource(id="fast-transfer", bandwidth=20, latency=1),  # 500 ms <= 1000 ms
        ]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertEqual(decision.destination, "fast-transfer")

    def test_compute_score_deterministic(self):
        wl = make_workload(priority=5, model_confidence=0.8)
        r1 = make_resource(id="r1", latency=10, available_cpu=8, available_memory=4096, bandwidth=50)
        r2 = make_resource(id="r2", latency=20, available_cpu=8, available_memory=4096, bandwidth=50)

        s1 = compute_score(wl, r1, 20, 8, 4096, 50)
        s2 = compute_score(wl, r2, 20, 8, 4096, 50)

        # Same call returns same score (deterministic).
        self.assertEqual(compute_score(wl, r1, 20, 8, 4096, 50), s1)
        # Lower latency should score higher.
        self.assertGreater(s1, s2)

    def test_normalize_available(self):
        self.assertEqual(normalize_available(8, 8), 1.0)
        self.assertEqual(normalize_available(0, 8), 0.0)
        self.assertEqual(normalize_available(4, 8), 0.5)
        self.assertEqual(normalize_available(9, 8), 1.0)  # clamped

    def test_normalize_latency(self):
        self.assertEqual(normalize_latency(0, 100), 1.0)
        self.assertEqual(normalize_latency(100, 100), 0.0)
        self.assertEqual(normalize_latency(50, 100), 0.5)

    def test_all_resources_feasible_one_selected(self):
        wl = make_workload(cpu_required=1, memory_required=128, data_size=1, latency_requirement=1000)
        resources = [
            make_resource(id="a", latency=10),
            make_resource(id="b", latency=20),
            make_resource(id="c", latency=30),
        ]
        orch = Orchestrator()
        decision = orch.decide(wl, resources)

        self.assertEqual(decision.destination, "a")
        self.assertGreaterEqual(decision.score, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
