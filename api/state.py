"""Persistent simulation and application state container.

Holds the current state of resources, devices, workloads, decisions,
execution feedback, events, and derived metrics for the I3 orchestrator.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from devices.device_manager import DeviceManager
from devices.event_detector import SensorEvent
from devices.industrial_sensor import IndustrialSensor
from infrastructure.resource_manager import InfrastructureResourceManager
from infrastructure.resources import CloudServer, EdgeNode
from infrastructure.workload_executor import WorkloadExecutor
from orchestrator.engine import Orchestrator
from shared.schemas import ComputeResource, ExecutionFeedback, OrchestrationDecision, Workload


class SimulationState:
    """Manages persistent state across devices, infrastructure, orchestrator, and execution."""

    def __init__(self) -> None:
        self.resource_manager = InfrastructureResourceManager()
        self.device_manager = DeviceManager()
        self.orchestrator = Orchestrator()
        self.executor = WorkloadExecutor()

        self.resources: Dict[str, ComputeResource] = self.resource_manager.resources
        self.devices: List[IndustrialSensor] = self.device_manager.devices
        self.workloads: List[Workload] = []
        self.decisions: List[OrchestrationDecision] = []
        self.execution_feedback: List[ExecutionFeedback] = []
        self.events: List[SensorEvent] = []
        self.updated_at: datetime = datetime.now(timezone.utc)

        self.initialize_default_simulation()

    def initialize_default_simulation(self) -> None:
        """Set up baseline resources, virtual sensor, and run initial simulation step."""
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
        sensor = IndustrialSensor(device_id="sensor-milling-01", demo_mode=False)
        self.device_manager.add_device(sensor)

        # 3. Perform initial complete simulation step
        self.step()

    def step(self, workload: Optional[Workload] = None) -> Dict[str, Any]:
        """Perform one complete simulation cycle:
        sensor/event -> workload -> orchestration -> reservation -> execution -> feedback -> release.
        """
        workloads_to_process: List[Workload] = []

        if workload is not None:
            workloads_to_process = [workload]
        else:
            # 1. Generate/get workload using existing DeviceManager
            self.device_manager.update_devices()
            events = self.device_manager.detect_events()
            if not events:
                # Ensure an event is detected by putting the sensor into an abnormal condition
                for device in self.devices:
                    device.state = "anomaly"
                    device.temperature = max(72.0, getattr(device, "temperature", 30.0) + 5.0)
                    device.vibration = max(2.1, getattr(device, "vibration", 0.2) + 0.3)
                events = self.device_manager.detect_events()

            self.events.extend(events)
            generated = self.device_manager.generate_workloads(events)
            workloads_to_process.extend(generated)

        # 2. Process each workload through orchestration, reservation, execution, and release
        for wl in workloads_to_process:
            self.workloads.append(wl)

            # 2. Get available resources from InfrastructureResourceManager
            available_resources = self.resource_manager.get_available_resources()

            # 3. Ask the existing Orchestrator for the destination
            decision = self.orchestrator.decide(wl, available_resources)
            self.decisions.append(decision)

            # If the orchestrator returns no destination, do not execute
            if not decision.destination:
                continue

            # 4. Resolve decision.destination to the actual ComputeResource
            try:
                resource = self.resource_manager.get_resource(decision.destination)
            except KeyError:
                continue

            # If the selected resource cannot execute the workload, do not execute
            if not self.resource_manager.can_execute(
                resource.id,
                wl.cpu_required,
                wl.memory_required,
            ):
                continue

            # 5. Validate/reserve resources using InfrastructureResourceManager
            reserved = self.resource_manager.reserve_resources(
                resource.id,
                wl.cpu_required,
                wl.memory_required,
            )
            if not reserved:
                continue

            # 6. Execute the workload using the existing WorkloadExecutor
            # 7. Receive an ExecutionFeedback object
            try:
                feedback = self.executor.execute(wl, resource)
                # 9. Store the execution feedback in SimulationState
                self.execution_feedback.append(feedback)
            finally:
                # 8. Release the reserved CPU/memory after execution
                self.resource_manager.release_resources(
                    resource.id,
                    wl.cpu_required,
                    wl.memory_required,
                )

        self.updated_at = datetime.now(timezone.utc)
        return self.get_snapshot()

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

        feedback_list = [
            {
                "workload_id": fb.workload_id,
                "resource_id": fb.resource_id,
                "success": fb.success,
                "execution_time": fb.execution_time,
                "latency": fb.latency,
                "cpu_used": fb.cpu_used,
                "memory_used": fb.memory_used,
                "energy_used": fb.energy_used,
                "data_transferred": fb.data_transferred,
                "model_confidence": fb.model_confidence,
            }
            for fb in self.execution_feedback
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
            "executionFeedback": feedback_list,
            "events": events_list,
            "metrics": metrics_list,
            "updatedAt": self.updated_at.isoformat(),
        }


# Global singleton simulation state
simulation_state = SimulationState()
