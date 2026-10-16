"""Execution Fabric: capability discovery, routing, approval and adapters."""

from .approvals import ApprovalGate, ApprovalGrant, ApprovalRequired
from .authority import AuthorityScopeGate, AuthorityScopeViolation
from .coordinator import ActionCoordinator, CoordinatedExecution
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
from .registry import CapabilityRegistry, CapabilityRouter, CapabilityUnavailable, RegisteredCapability
from .retry import RetryDecision, RetryPolicy, assess_retry

__all__ = [
    "ActionCoordinator",
    "ApprovalGate",
    "ApprovalGrant",
    "ApprovalRequired",
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
    "ExecutionDisposition",
    "ExecutionOutcome",
    "ExecutionRequest",
    "HostCallableExecutor",
    "HostCapabilitySpec",
    "LocalWorkspaceExecutor",
    "OpenAIAgentSpec",
    "OpenAIAgentsExecutor",
    "RegisteredCapability",
    "RetryDecision",
    "RetryPolicy",
    "assess_retry",
    "build_uaos_output_guardrail",
    "register_host_capability",
    "register_local_workspace_capability",
]
