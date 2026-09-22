"""Persistent simulation and application state container.

Holds the current state of resources, devices, workloads, decisions,
execution feedback, events, and derived metrics for the I3 orchestrator.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from devices.device_manager import DeviceManager
from devices.event_detector import SensorEvent
from devices.industrial_sensor import IndustrialSensor
from infrastructure.resource_manager import InfrastructureResourceManager
from infrastructure.resources import CloudServer, EdgeNode
from orchestrator.engine import Orchestrator
from shared.schemas import ComputeResource, ExecutionFeedback, OrchestrationDecision, Workload


class SimulationState:
    """Manages persistent state across devices, infrastructure, and orchestrator."""

    def __init__(self) -> None:
        self.resource_manager = InfrastructureResourceManager()
        self.device_manager = DeviceManager()
        self.orchestrator = Orchestrator()

        self.resources: Dict[str, ComputeResource] = self.resource_manager.resources
        self.devices: List[IndustrialSensor] = self.device_manager.devices
        self.workloads: List[Workload] = []
        self.decisions: List[OrchestrationDecision] = []
        self.execution_feedback: List[ExecutionFeedback] = []
        self.events: List[SensorEvent] = []
        self.updated_at: datetime = datetime.now(timezone.utc)

        self.initialize_default_simulation()

    def initialize_default_simulation(self) -> None:
        """Set up baseline resources, virtual sensors, and initial orchestration."""
        # 1. Register compute resources
        edge_1 = EdgeNode(
            id="edge-node-01",
            cpu_capacity=4.0,
            memory_capacity=2048.0,
            latency=15.0,
            bandwidth=100.0,
            energy_level=100.0,
        )
        edge_2 = EdgeNode(
            id="edge-node-02",
            cpu_capacity=2.0,
            memory_capacity=1024.0,
            latency=25.0,
            bandwidth=80.0,
            energy_level=90.0,
        )
        cloud_1 = CloudServer(
            id="cloud-server-01",
            cpu_capacity=16.0,
            memory_capacity=16384.0,
            latency=60.0,
            bandwidth=200.0,
            energy_level=100.0,
        )

        self.resource_manager.register_resource(edge_1)
        self.resource_manager.register_resource(edge_2)
        self.resource_manager.register_resource(cloud_1)

        # 2. Register virtual IoT industrial sensor
        sensor = IndustrialSensor(device_id="sensor-milling-01")
        self.device_manager.add_device(sensor)

        # 3. Simulate critical operating condition to generate baseline event
        sensor.state = "anomaly"
        sensor.temperature = 75.5
        sensor.vibration = 2.45

        # 4. Detect events and generate workload
        detected_events = self.device_manager.detect_events()
        self.events.extend(detected_events)

        generated_workloads = self.device_manager.generate_workloads(detected_events)
        self.workloads.extend(generated_workloads)

        # 5. Run orchestrator decision and resource reservation
        available_resources = self.resource_manager.get_available_resources()
        for workload in generated_workloads:
            decision = self.orchestrator.decide(workload, available_resources)
            self.decisions.append(decision)

            if decision.destination:
                if self.resource_manager.can_execute(
                    decision.destination,
                    workload.cpu_required,
                    workload.memory_required,
                ):
                    self.resource_manager.reserve_resources(
                        decision.destination,
                        workload.cpu_required,
                        workload.memory_required,
                    )

        self.updated_at = datetime.now(timezone.utc)

    def get_snapshot(self) -> Dict[str, Any]:
        """Produce a consistent, serialized snapshot for the dashboard."""
        resources_list: List[Dict[str, Any]] = []
        metrics_list: List[Dict[str, Any]] = []

        for res in self.resource_manager.get_all_resources():
            cpu_util = (
                round((res.cpu_capacity - res.available_cpu) / res.cpu_capacity * 100.0, 2)
                if res.cpu_capacity > 0
                else 0.0
            )
            mem_util = (
                round(
                    (res.memory_capacity - res.available_memory)
                    / res.memory_capacity
                    * 100.0,
                    2,
                )
                if res.memory_capacity > 0
                else 0.0
            )

            resources_list.append(
                {
                    "id": res.id,
                    "type": res.type,
                    "cpu_capacity": res.cpu_capacity,
                    "available_cpu": res.available_cpu,
                    "cpu_utilization": cpu_util,
                    "memory_capacity": res.memory_capacity,
                    "available_memory": res.available_memory,
                    "memory_utilization": mem_util,
                    "latency": res.latency,
                    "bandwidth": res.bandwidth,
                    "energy_level": res.energy_level,
                }
            )

            metrics_list.append(
                {
                    "resource_id": res.id,
                    "type": res.type,
                    "cpu_utilization": cpu_util,
                    "memory_utilization": mem_util,
                }
            )

        workloads_list = [
            {
                "id": w.id,
                "source_device_id": w.source_device_id,
                "type": w.type,
                "cpu_required": w.cpu_required,
                "memory_required": w.memory_required,
                "data_size": w.data_size,
                "latency_requirement": w.latency_requirement,
                "energy_requirement": w.energy_requirement,
                "priority": w.priority,
                "model_confidence": w.model_confidence,
            }
            for w in self.workloads
        ]

        decisions_list = [
            {
                "workload_id": d.workload_id,
                "destination": d.destination,
                "score": d.score,
                "reason": d.reason,
            }
            for d in self.decisions
        ]

        events_list = [
            {
                "event_id": e.event_id,
                "device_id": e.device_id,
                "event_type": e.event_type,
                "severity": e.severity,
                "temperature": e.temperature,
                "vibration": e.vibration,
                "description": e.description,
            }
            for e in self.events
        ]

        return {
            "resources": resources_list,
            "workloads": workloads_list,
            "decisions": decisions_list,
            "executionFeedback": [],
            "events": events_list,
            "metrics": metrics_list,
            "updatedAt": self.updated_at.isoformat(),
        }


# Global singleton simulation state
simulation_state = SimulationState()
