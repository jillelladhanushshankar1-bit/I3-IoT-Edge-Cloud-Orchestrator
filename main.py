"""I3 — Predictive IoT-Edge-Cloud Resource Orchestration.

End-to-End Integration Demo:
IndustrialSensor -> DeviceManager -> EventDetector -> WorkloadGenerator
-> Workload -> Orchestrator.decide() -> InfrastructureResourceManager
"""

import sys
from devices.industrial_sensor import IndustrialSensor
from devices.device_manager import DeviceManager
from infrastructure.resources import EdgeNode, CloudServer
from infrastructure.resource_manager import InfrastructureResourceManager
from orchestrator.engine import Orchestrator


def print_section(title: str) -> None:
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def setup_infrastructure() -> InfrastructureResourceManager:
    """Initialize and register compute resources across edge and cloud tiers."""
    rm = InfrastructureResourceManager()

    # Tier 1: Local Edge Nodes (low latency, moderate compute)
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

    # Tier 2: Cloud Server (high capacity, higher latency)
    cloud_1 = CloudServer(
        id="cloud-server-01",
        cpu_capacity=16.0,
        memory_capacity=16384.0,
        latency=60.0,
        bandwidth=200.0,
        energy_level=100.0,
    )

    rm.register_resource(edge_1)
    rm.register_resource(edge_2)
    rm.register_resource(cloud_1)

    return rm


def main() -> None:
    print_section("I3 ORCHESTRATOR -- END-TO-END INTEGRATION DEMO")

    # ------------------------------------------------------------------
    # 1. Initialize Infrastructure
    # ------------------------------------------------------------------
    print_section("1. INFRASTRUCTURE SETUP")
    resource_manager = setup_infrastructure()
    all_resources = resource_manager.get_all_resources()

    print(f"Registered {len(all_resources)} compute resource(s):")
    for res in all_resources:
        print(
            f"  - [{res.id}] Type: {res.type:<5} | "
            f"CPU: {res.available_cpu:.1f}/{res.cpu_capacity:.1f} cores | "
            f"Memory: {res.available_memory:.0f}/{res.memory_capacity:.0f} MB | "
            f"Latency: {res.latency:.1f} ms | "
            f"Bandwidth: {res.bandwidth:.1f} MB/s"
        )

    # ------------------------------------------------------------------
    # 2. Virtual IoT Sensor & Condition Triggering
    # ------------------------------------------------------------------
    print_section("2. IOT SENSOR READINGS & ANOMALY TRIGGER")
    sensor = IndustrialSensor(device_id="sensor-milling-01")
    device_manager = DeviceManager()
    device_manager.add_device(sensor)

    # Simulate sensor operating in critical condition
    sensor.state = "anomaly"
    sensor.temperature = 75.5  # abnormal (threshold >= 70.0)
    sensor.vibration = 2.45    # abnormal (threshold >= 2.0)

    print(f"Device ID   : {sensor.device_id}")
    print(f"State       : {sensor.state.upper()}")
    print(f"Temperature : {sensor.temperature:.2f} C (Threshold: >= 70.0 C)")
    print(f"Vibration   : {sensor.vibration:.2f} mm/s (Threshold: >= 2.00 mm/s)")

    # ------------------------------------------------------------------
    # 3. Event Detection & Workload Generation
    # ------------------------------------------------------------------
    print_section("3. EVENT DETECTION & WORKLOAD GENERATION")
    events = device_manager.detect_events()
    if not events:
        print("No events detected. Exiting demo.")
        return

    detected_event = events[0]
    print(f"Event ID    : {detected_event.event_id}")
    print(f"Type        : {detected_event.event_type}")
    print(f"Severity    : {detected_event.severity.upper()}")
    print(f"Description : {detected_event.description}")

    workloads = device_manager.generate_workloads(events)
    workload = workloads[0]

    print("\nGenerated Canonical Workload:")
    print(f"  ID                 : {workload.id}")
    print(f"  Source Device      : {workload.source_device_id}")
    print(f"  Workload Type      : {workload.type}")
    print(f"  CPU Required       : {workload.cpu_required:.2f} cores")
    print(f"  Memory Required    : {workload.memory_required:.1f} MB")
    print(f"  Data Size          : {workload.data_size:.1f} MB")
    print(f"  Latency Requirement: {workload.latency_requirement:.1f} ms")
    print(f"  Energy Budget      : {workload.energy_requirement:.1f} J")
    print(f"  Priority           : {workload.priority}")
    print(f"  Model Confidence   : {workload.model_confidence:.2f}")

    # ------------------------------------------------------------------
    # 4. Orchestrator Decision
    # ------------------------------------------------------------------
    print_section("4. ORCHESTRATION DECISION")
    available_resources = resource_manager.get_available_resources()
    print(f"Evaluating {len(available_resources)} candidate resource(s)...")

    orchestrator = Orchestrator()
    decision = orchestrator.decide(workload=workload, resources=available_resources)

    print(f"Decision Result:")
    print(f"  Destination Resource : {decision.destination or 'NONE (Rejected)'}")
    print(f"  Placement Score      : {decision.score:.4f}")
    print(f"  Reason               : {decision.reason}")

    # ------------------------------------------------------------------
    # 5. Resource Verification & Reservation
    # ------------------------------------------------------------------
    print_section("5. RESOURCE VERIFICATION & RESERVATION")

    if not decision.destination:
        print(f"No placement made for workload {workload.id}. Resource reservation skipped.")
        return

    selected_res = resource_manager.get_resource(decision.destination)

    print(f"Selected Resource: [{selected_res.id}] ({selected_res.type})")
    print(
        f"  Pre-Reservation Capacity : "
        f"CPU = {selected_res.available_cpu:.2f}/{selected_res.cpu_capacity:.2f} cores | "
        f"Memory = {selected_res.available_memory:.1f}/{selected_res.memory_capacity:.1f} MB"
    )

    can_exec = resource_manager.can_execute(
        resource_id=selected_res.id,
        required_cpu=workload.cpu_required,
        required_memory=workload.memory_required,
    )
    print(f"  can_execute() check      : {'PASSED' if can_exec else 'FAILED'}")

    if can_exec:
        reserved = resource_manager.reserve_resources(
            resource_id=selected_res.id,
            required_cpu=workload.cpu_required,
            required_memory=workload.memory_required,
        )
        print(f"  reserve_resources()      : {'SUCCESS' if reserved else 'FAILED'}")

        print(
            f"  Post-Reservation Capacity: "
            f"CPU = {selected_res.available_cpu:.2f}/{selected_res.cpu_capacity:.2f} cores "
            f"(-{workload.cpu_required:.2f}) | "
            f"Memory = {selected_res.available_memory:.1f}/{selected_res.memory_capacity:.1f} MB "
            f"(-{workload.memory_required:.1f} MB)"
        )
    else:
        print("  Insufficient resources to reserve.")

    print_section("END-TO-END PIPELINE RUN COMPLETE")


if __name__ == "__main__":
    main()
