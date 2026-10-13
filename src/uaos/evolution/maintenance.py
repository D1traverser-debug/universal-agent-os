from __future__ import annotations
from .models import MaintenanceDecision, MaintenanceRequest, MaintenanceRisk


def assess_maintenance(request: MaintenanceRequest) -> MaintenanceDecision:
    reasons: list[str] = []
    if request.trigger == "IDLE" and not request.background_capability_available:
        reasons.append("no real background/scheduler capability")
    if request.foreground_priority_active:
        reasons.append("foreground work has priority")
    if request.production_mutation_requested:
        if request.risk is MaintenanceRisk.HIGH and not request.explicit_approval_id:
            reasons.append("high-risk production maintenance requires explicit approval")
        mode = "CONTROLLED_MUTATION"
    else:
        mode = "DIAGNOSE_AND_PROPOSE"
    return MaintenanceDecision(not reasons, mode, tuple(reasons))
