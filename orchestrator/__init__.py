"""I3 Orchestrator Module.

Provides workload placement decisions for IoT-Edge-Cloud orchestration.

Example:
    from orchestrator import Orchestrator, ScoringConfig
    from shared.schemas import Workload, ComputeResource

    orchestrator = Orchestrator(ScoringConfig())
    decision = orchestrator.decide(workload, resources)
"""

from orchestrator.engine import Orchestrator
from orchestrator.scoring import ScoringConfig, compute_score

__all__ = [
    "Orchestrator",
    "ScoringConfig",
    "compute_score",
]