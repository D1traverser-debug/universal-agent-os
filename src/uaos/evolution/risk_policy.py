from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

class ChangeRisk(StrEnum): LOW="LOW"; MEDIUM="MEDIUM"; HIGH="HIGH"; CRITICAL="CRITICAL"
class SelfChangeDisposition(StrEnum):
    AUTO_APPLY="AUTO_APPLY"
    SANDBOX_EVALUATE="SANDBOX_EVALUATE"
    REQUIRE_EXPLICIT_APPROVAL="REQUIRE_EXPLICIT_APPROVAL"
    APPLY_WITH_APPROVAL="APPLY_WITH_APPROVAL"
    DENY_SELF_ESCALATION="DENY_SELF_ESCALATION"

PROTECTED_SURFACES=frozenset({"requirements_authority","permission_boundary","approval_policy","state_authority","self_change_policy","paid_resource_policy","bulk_delete","secrets_access"})

@dataclass(frozen=True,slots=True)
class ChangeIntent:
    surface:str
    reversible:bool
    rollback_verified:bool
    external_side_effect:bool=False
    expands_authority:bool=False
    enables_paid_resource:bool=False
    destructive:bool=False

@dataclass(frozen=True,slots=True)
class SelfChangeDecision:
    risk:ChangeRisk
    disposition:SelfChangeDisposition
    reasons:tuple[str,...]

def classify_change(intent:ChangeIntent)->ChangeRisk:
    if intent.expands_authority: return ChangeRisk.CRITICAL
    if intent.surface in PROTECTED_SURFACES or intent.enables_paid_resource or intent.destructive: return ChangeRisk.HIGH
    if intent.external_side_effect or not intent.reversible: return ChangeRisk.HIGH
    if not intent.rollback_verified: return ChangeRisk.MEDIUM
    return ChangeRisk.LOW

def decide_self_change(intent:ChangeIntent,*,evaluation_passed:bool,canary_healthy:bool=False,explicit_approval:bool=False)->SelfChangeDecision:
    risk=classify_change(intent); reasons=[]
    if intent.expands_authority: return SelfChangeDecision(risk,SelfChangeDisposition.DENY_SELF_ESCALATION,("system may not grant itself broader authority",))
    if risk is ChangeRisk.HIGH:
        if not evaluation_passed: reasons.append("evaluation has not passed")
        if not explicit_approval: reasons.append("explicit approval required for high-risk change")
        if intent.enables_paid_resource: reasons.append("paid resource use requires explicit approval")
        if evaluation_passed and explicit_approval: return SelfChangeDecision(risk,SelfChangeDisposition.APPLY_WITH_APPROVAL,tuple(reasons))
        return SelfChangeDecision(risk,SelfChangeDisposition.REQUIRE_EXPLICIT_APPROVAL,tuple(reasons))
    if risk is ChangeRisk.MEDIUM:
        if evaluation_passed and canary_healthy and intent.rollback_verified: return SelfChangeDecision(risk,SelfChangeDisposition.AUTO_APPLY,("candidate passed evaluation, canary and rollback checks",))
        return SelfChangeDecision(risk,SelfChangeDisposition.SANDBOX_EVALUATE,("medium-risk change must remain candidate until evaluation/canary/rollback evidence passes",))
    if not evaluation_passed: return SelfChangeDecision(risk,SelfChangeDisposition.SANDBOX_EVALUATE,("evaluation required before auto-apply",))
    return SelfChangeDecision(risk,SelfChangeDisposition.AUTO_APPLY,("low-risk reversible change passed evaluation",))
