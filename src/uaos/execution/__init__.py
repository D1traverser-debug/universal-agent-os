"""Execution Fabric: capability discovery, routing, approval and adapters."""

from .approvals import ApprovalGate, ApprovalGrant, ApprovalRequired
from .authority import AuthorityScopeGate, AuthorityScopeViolation
from .coordinator import ActionCoordinator, CoordinatedExecution, ExecutionAdmissionReceipt
from .host import HostCallableExecutor, HostCapabilitySpec, register_host_capability
from .local_workspace import LocalWorkspaceExecutor, register_local_workspace_capability
from .models import (
    CapabilityAvailability,
    CapabilityCostClass,
    CapabilityHealth,
    CapabilityObservation,
    ExecutionDisposition,
    ExecutionOutcome,
    ExecutionRequest,
)
from .openai_agents import OpenAIAgentSpec, OpenAIAgentsExecutor, build_uaos_output_guardrail
from .persistent_assets import (
    AssetLifecycle,
    AssetReconciliationReport,
    AssetRole,
    CrudOperation,
    MigrationObservation,
    MutationContract,
    MutationPersistence,
    PersistentAssetCatalog,
    PersistentAssetDescriptor,
    PersistentAssetGate,
    PersistentAssetRequest,
    PersistentAssetViolation,
    PersistentSurface,
    reconcile_asset_inventory,
)
from .registry import (
    CapabilityRegistry,
    CapabilityRouter,
    CapabilityUnavailable,
    RegisteredCapability,
    TargetCanonicalizer,
)
from .retry import RetryDecision, RetryPolicy, assess_retry

__all__ = [
    "ActionCoordinator",
    "ApprovalGate",
    "ApprovalGrant",
    "ApprovalRequired",
    "AssetLifecycle",
    "AssetReconciliationReport",
    "AssetRole",
    "AuthorityScopeGate",
    "AuthorityScopeViolation",
    "CapabilityAvailability",
    "CapabilityCostClass",
    "CapabilityHealth",
    "CapabilityObservation",
    "CapabilityRegistry",
    "CapabilityRouter",
    "CapabilityUnavailable",
    "CoordinatedExecution",
    "CrudOperation",
    "ExecutionAdmissionReceipt",
    "ExecutionDisposition",
    "ExecutionOutcome",
    "ExecutionRequest",
    "HostCallableExecutor",
    "HostCapabilitySpec",
    "LocalWorkspaceExecutor",
    "MigrationObservation",
    "MutationContract",
    "MutationPersistence",
    "OpenAIAgentSpec",
    "OpenAIAgentsExecutor",
    "PersistentAssetCatalog",
    "PersistentAssetDescriptor",
    "PersistentAssetGate",
    "PersistentAssetRequest",
    "PersistentAssetViolation",
    "PersistentSurface",
    "RegisteredCapability",
    "RetryDecision",
    "RetryPolicy",
    "TargetCanonicalizer",
    "assess_retry",
    "build_uaos_output_guardrail",
    "reconcile_asset_inventory",
    "register_host_capability",
    "register_local_workspace_capability",
]
