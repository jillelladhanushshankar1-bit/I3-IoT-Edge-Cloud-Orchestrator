"""Infrastructure-side workload execution simulation.

This module simulates workload execution on a selected ComputeResource.
It does not perform placement or scoring decisions.
"""

from shared.schemas import ComputeResource, ExecutionFeedback, Workload


class WorkloadExecutor:
    """Simulates execution of workloads on selected compute resources."""

    def execute(
        self,
        workload: Workload,
        resource: ComputeResource,
    ) -> ExecutionFeedback:
        """Execute a workload simulation on a selected resource."""

        # Check basic resource availability.
        if (
            resource.available_cpu < workload.cpu_required
            or resource.available_memory < workload.memory_required
            or resource.cpu_capacity <= 0
            or resource.memory_capacity <= 0
            or resource.bandwidth <= 0
            or resource.energy_level <= 0
        ):
            return self._failed_feedback(workload, resource)

        # CPU utilization relative to total resource capacity.
        cpu_utilization = (
            workload.cpu_required / resource.cpu_capacity
        )

        # Simulated compute time.
        # More CPU capacity means lower execution time.
        compute_time = (
            cpu_utilization * 1000.0
        )

        # Simulated data transfer time.
        # Bandwidth is defined as MB/s, so convert seconds to milliseconds.
        transfer_time = (
            workload.data_size / resource.bandwidth
        ) * 1000.0

        # End-to-end latency includes resource latency and data transfer.
        latency = resource.latency + transfer_time

        # Total simulated execution time.
        execution_time = (
            compute_time
            + transfer_time
            + resource.latency
        )

        # CPU and memory consumed by the workload.
        cpu_used = workload.cpu_required
        memory_used = workload.memory_required

        # Lower energy level slightly increases simulated energy consumption.
        energy_factor = (
            1.0 + (100.0 - resource.energy_level) / 200.0
        )

        energy_used = (
            workload.energy_requirement
            * cpu_utilization
            * energy_factor
        )

        # Treat the workload's energy requirement as its execution budget.
        if energy_used > workload.energy_requirement:
            return self._failed_feedback(
                workload,
                resource,
                latency=latency,
            )

        return ExecutionFeedback(
            workload_id=workload.id,
            resource_id=resource.id,
            success=True,
            execution_time=execution_time,
            latency=latency,
            cpu_used=cpu_used,
            memory_used=memory_used,
            energy_used=energy_used,
            data_transferred=workload.data_size,
            model_confidence=workload.model_confidence,
        )

    @staticmethod
    def _failed_feedback(
        workload: Workload,
        resource: ComputeResource,
        latency: float = 0.0,
    ) -> ExecutionFeedback:
        """Create deterministic feedback for a failed execution."""

        return ExecutionFeedback(
            workload_id=workload.id,
            resource_id=resource.id,
            success=False,
            execution_time=0.0,
            latency=latency,
            cpu_used=0.0,
            memory_used=0.0,
            energy_used=0.0,
            data_transferred=0.0,
            model_confidence=workload.model_confidence,
        )