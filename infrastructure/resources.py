"""Concrete infrastructure resource definitions.

This module provides concrete resource types used by the infrastructure
layer. All resources are represented using the shared ComputeResource
schema.
"""

from shared.schemas import ComputeResource


class EdgeNode(ComputeResource):
    """Represents a virtual edge-computing node."""

    def __init__(
        self,
        id: str,
        cpu_capacity: float,
        memory_capacity: float,
        latency: float,
        bandwidth: float,
        energy_level: float = 100.0,
    ) -> None:
        super().__init__(
            id=id,
            type="edge",
            cpu_capacity=cpu_capacity,
            memory_capacity=memory_capacity,
            latency=latency,
            bandwidth=bandwidth,
            energy_level=energy_level,
        )


class CloudServer(ComputeResource):
    """Represents a cloud-computing server."""

    def __init__(
        self,
        id: str,
        cpu_capacity: float,
        memory_capacity: float,
        latency: float,
        bandwidth: float,
        energy_level: float = 100.0,
    ) -> None:
        super().__init__(
            id=id,
            type="cloud",
            cpu_capacity=cpu_capacity,
            memory_capacity=memory_capacity,
            latency=latency,
            bandwidth=bandwidth,
            energy_level=energy_level,
        )