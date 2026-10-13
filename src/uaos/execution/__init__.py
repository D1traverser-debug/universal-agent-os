"""Execution Fabric: capability discovery, routing, approval and adapters."""

from .approvals import ApprovalGate, ApprovalGrant, ApprovalRequired
from .coordinator import ActionCoordinator, CoordinatedExecution
from .models import CapabilityHealth, CapabilityObservation, ExecutionDisposition, ExecutionOutcome, ExecutionRequest
from .openai_agents import OpenAIAgentSpec, OpenAIAgentsExecutor
from .registry import CapabilityRegistry, CapabilityRouter, CapabilityUnavailable, RegisteredCapability

__all__ = [
    "ActionCoordinator",
    "ApprovalGate",
    "ApprovalGrant",
    "ApprovalRequired",
    "CapabilityHealth",
    "CapabilityObservation",
    "CapabilityRegistry",
    "CapabilityRouter",
    "CapabilityUnavailable",
    "CoordinatedExecution",
    "ExecutionDisposition",
    "ExecutionOutcome",
    "ExecutionRequest",
    "OpenAIAgentSpec",
    "OpenAIAgentsExecutor",
    "RegisteredCapability",
]
