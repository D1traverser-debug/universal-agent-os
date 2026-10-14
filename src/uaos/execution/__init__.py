"""Execution Fabric: capability discovery, routing, approval and adapters."""

from .approvals import ApprovalGate, ApprovalGrant, ApprovalRequired
from .coordinator import ActionCoordinator, CoordinatedExecution
from .host import HostCallableExecutor, HostCapabilitySpec, register_host_capability
from .models import (
    CapabilityAvailability,
    CapabilityCostClass,
    CapabilityHealth,
    CapabilityObservation,
    ExecutionDisposition,
    ExecutionOutcome,
    ExecutionRequest,
)
from .openai_agents import OpenAIAgentSpec, OpenAIAgentsExecutor
from .registry import CapabilityRegistry, CapabilityRouter, CapabilityUnavailable, RegisteredCapability
from .retry import RetryDecision, RetryPolicy, assess_retry

__all__ = [
    "ActionCoordinator",
    "ApprovalGate",
    "ApprovalGrant",
    "ApprovalRequired",
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
    "OpenAIAgentSpec",
    "OpenAIAgentsExecutor",
    "RegisteredCapability",
    "RetryDecision",
    "RetryPolicy",
    "assess_retry",
    "register_host_capability",
]
