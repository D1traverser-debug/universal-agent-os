"""Durable runtime abstraction and adapters."""

from .compatibility import CompatibilityDecision, CompatibilityMode, VersionCompatibilityPolicy
from .dbos_runtime import DBOSRuntime
from .finalization import FinalizationBlocked, FinalizationContext, FinalizationReceipt, admit_final_response
from .policy_activation import (
    REF_CONDITIONAL_POLICY_STATUS,
    PolicyActivationState,
    PolicyActivationViolation,
    ProductionRefIdentity,
    require_active_ref_conditioned_policy,
    resolve_ref_conditioned_policy_activation,
)
from .ports import ControlTopic, DurableRuntime, RuntimeMessage, RuntimeWorkflowStatus, WorkflowNotFound, WorkflowRef, WorkflowSpec, WorkflowStateError
from .reference import InMemoryDurableRuntime
from .sqlite_runtime import SQLiteCheckpointRuntime

__all__ = [
    "CompatibilityDecision",
    "CompatibilityMode",
    "VersionCompatibilityPolicy",
    "ControlTopic",
    "DBOSRuntime",
    "DurableRuntime",
    "FinalizationBlocked",
    "FinalizationContext",
    "FinalizationReceipt",
    "InMemoryDurableRuntime",
    "PolicyActivationState",
    "PolicyActivationViolation",
    "ProductionRefIdentity",
    "REF_CONDITIONAL_POLICY_STATUS",
    "SQLiteCheckpointRuntime",
    "RuntimeMessage",
    "RuntimeWorkflowStatus",
    "WorkflowNotFound",
    "WorkflowRef",
    "WorkflowSpec",
    "WorkflowStateError",
    "admit_final_response",
    "require_active_ref_conditioned_policy",
    "resolve_ref_conditioned_policy_activation",
]
