"""Infrastructure resource manager.

Manages virtual Edge Nodes and Cloud Servers available to the orchestrator.
"""

from typing import Dict, List

from infrastructure.resources import ComputeResource


class InfrastructureResourceManager:
    def __init__(self) -> None:
        """Initialize the infrastructure resource manager."""
        self.resources: Dict[str, ComputeResource] = {}

    def register_resource(self, resource: ComputeResource) -> None:
        """Register a compute resource."""
        self.resources[resource.id] = resource

    def get_resource(self, resource_id: str) -> ComputeResource:
        """Get a resource by its ID."""
        if resource_id not in self.resources:
            raise KeyError(f"Resource not found: {resource_id}")

        return self.resources[resource_id]

    def get_all_resources(self) -> List[ComputeResource]:
        """Get all registered resources."""
        return list(self.resources.values())

    def get_resources_by_type(
        self,
        resource_type: str,
    ) -> List[ComputeResource]:
        """Get resources matching a specific type."""
        return [
            resource
            for resource in self.resources.values()
            if resource.type == resource_type
        ]

    def get_available_resources(self) -> List[ComputeResource]:
        """Get resources that currently have available CPU and memory."""
        return [
            resource
            for resource in self.resources.values()
            if resource.available_cpu > 0
            and resource.available_memory > 0
        ]

    def update_resource_availability(
        self,
        resource_id: str,
        available_cpu: float,
        available_memory: float,
    ) -> None:
        """Update currently available CPU and memory."""
        resource = self.get_resource(resource_id)

        resource.available_cpu = max(
            0.0,
            min(available_cpu, resource.cpu_capacity),
        )

        resource.available_memory = max(
            0.0,
            min(available_memory, resource.memory_capacity),
        )

    def can_execute(
        self,
        resource_id: str,
        required_cpu: float,
        required_memory: float,
    ) -> bool:
        """Check whether a resource has enough CPU and memory."""
        resource = self.get_resource(resource_id)

        return (
            resource.available_cpu >= required_cpu
            and resource.available_memory >= required_memory
        )

    def reserve_resources(
        self,
        resource_id: str,
        required_cpu: float,
        required_memory: float,
    ) -> bool:
        """Reserve CPU and memory for a task."""
        if not self.can_execute(
            resource_id,
            required_cpu,
            required_memory,
        ):
            return False

        resource = self.get_resource(resource_id)

        resource.available_cpu -= required_cpu
        resource.available_memory -= required_memory

        return True

    def release_resources(
        self,
        resource_id: str,
        released_cpu: float,
        released_memory: float,
    ) -> None:
        """Release previously reserved CPU and memory."""
        resource = self.get_resource(resource_id)

        resource.available_cpu = min(
            resource.cpu_capacity,
            resource.available_cpu + released_cpu,
        )

        resource.available_memory = min(
            resource.memory_capacity,
            resource.available_memory + released_memory,
        )

    def remove_resource(self, resource_id: str) -> None:
        """Remove a resource from infrastructure."""
        self.resources.pop(resource_id, None)