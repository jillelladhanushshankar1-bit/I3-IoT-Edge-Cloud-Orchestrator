"""Core orchestration engine for the I3 orchestrator.

Provides the :class:`Orchestrator` class, which filters feasible
resources, scores each one using :func:`orchestrator.scoring.compute_score`,
and returns an :class:`OrchestrationDecision`.

Feasibility rules
-----------------
A resource is rejected when ANY of these hold:

- ``available_cpu < workload.cpu_required``
- ``available_memory < workload.memory_required``
- ``resource.latency > workload.latency_requirement``
- Data cannot be transferred within the latency budget:
  ``(workload.data_size / resource.bandwidth) * 1000 > workload.latency_requirement``
- ``energy_level is None`` (malformed resource)

Note on energy
--------------
``ComputeResource.energy_level`` is a percentage (0–100) while
``Workload.energy_requirement`` is expressed in Joules.  Without
knowing the resource's total energy capacity (not present in the
current schema), a reliable comparison cannot be made, so the
energy check is **documented but not enforced** — energy level
is still used in scoring to prefer higher-level resources.

If no resource is feasible the orchestrator returns an
``OrchestrationDecision`` with ``destination=""``, ``score=-1.0``,
and a reason explaining the rejection.
"""

from dataclasses import dataclass
from typing import List

from shared.schemas import ComputeResource, OrchestrationDecision, Workload
from orchestrator.scoring import ScoringConfig, compute_score


@dataclass
class Orchestrator:
    """Baseline deterministic orchestration engine.

    Parameters
    ----------
    config:
        Scoring weights and parameters (defaults are sensible).
    """

    config: ScoringConfig = None

    def __post_init__(self):
        if self.config is None:
            self.config = ScoringConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decide(
        self,
        workload: Workload,
        resources: List[ComputeResource],
    ) -> OrchestrationDecision:
        """Pick the best resource for *workload* from *resources*.

        Returns
        -------
        OrchestrationDecision
            The highest-scoring feasible resource, or a sentinel
            decision with ``destination=""`` when no resource is
            feasible.
        """
        feasible = self._filter_feasible(workload, resources)

        if not feasible:
            return OrchestrationDecision(
                workload_id=workload.id,
                destination="",
                score=-1.0,
                reason=(
                    f"No feasible resource for workload {workload.id}: "
                    "all candidates violate at least one hard constraint."
                ),
            )

        # Pre-compute maxima for normalisation among feasible resources
        max_latency = max(r.latency for r in feasible)
        max_cpu = max(r.available_cpu for r in feasible)
        max_memory = max(r.available_memory for r in feasible)
        max_bandwidth = max(r.bandwidth for r in feasible)

        # Score each feasible resource
        best_resource = None
        best_score = -1.0
        for res in feasible:
            s = compute_score(
                workload=workload,
                resource=res,
                feasible_max_latency=max_latency,
                feasible_max_cpu=max_cpu,
                feasible_max_memory=max_memory,
                feasible_max_bandwidth=max_bandwidth,
                config=self.config,
            )
            if s > best_score:
                best_score = s
                best_resource = res

        return OrchestrationDecision(
            workload_id=workload.id,
            destination=best_resource.id,
            score=best_score,
            reason=(
                f"Selected {best_resource.id} ({best_resource.type}) "
                f"with score {best_score:.4f} — best among "
                f"{len(feasible)} feasible resource(s)."
            ),
        )

    # ------------------------------------------------------------------
    # Feasibility filtering
    # ------------------------------------------------------------------

    def _filter_feasible(
        self,
        workload: Workload,
        resources: List[ComputeResource],
    ) -> List[ComputeResource]:
        """Return only resources that satisfy all hard constraints."""
        feasible = []
        for res in resources:
            if not self._is_feasible(workload, res):
                continue
            feasible.append(res)
        return feasible

    def _is_feasible(
        self,
        workload: Workload,
        resource: ComputeResource,
    ) -> bool:
        """Return True if *resource* can satisfy all hard requirements
        for *workload*.
        """
        # Hard CPU & memory constraints
        if resource.available_cpu < workload.cpu_required:
            return False
        if resource.available_memory < workload.memory_required:
            return False

        # Latency constraint
        if resource.latency > workload.latency_requirement:
            return False

        # Bandwidth: data must be transferrable within latency budget.
        # data_size is in MB, bandwidth is in MB/s, so transfer time is in
        # seconds; latency_requirement is in milliseconds, so convert.
        if resource.bandwidth <= 0:
            return False
        transfer_time_ms = (workload.data_size / resource.bandwidth) * 1000.0
        if transfer_time_ms > workload.latency_requirement:
            return False

        # Energy level sanity check (not a hard budget — see module docstring)
        if resource.energy_level < 0:
            return False

        return True