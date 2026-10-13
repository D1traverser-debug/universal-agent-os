from __future__ import annotations
from dataclasses import replace
from .models import FailureClass, Incident


class EvolutionCatalog:
    def __init__(self) -> None:
        self._incidents: dict[str, Incident] = {}
        self._failure_classes: dict[str, FailureClass] = {}

    def add_incident(self, incident: Incident) -> None:
        if incident.incident_id in self._incidents:
            raise ValueError(f"duplicate incident_id: {incident.incident_id}")
        self._incidents[incident.incident_id] = incident

    def matching_incidents(self, fingerprint: str) -> tuple[Incident, ...]:
        return tuple(sorted((i for i in self._incidents.values() if i.fingerprint == fingerprint), key=lambda i: i.incident_id))

    def add_failure_class(self, failure_class: FailureClass) -> None:
        if failure_class.failure_class_id in self._failure_classes:
            raise ValueError(f"duplicate failure_class_id: {failure_class.failure_class_id}")
        missing = set(failure_class.incident_ids) - set(self._incidents)
        if missing:
            raise ValueError(f"failure class references unknown incidents: {sorted(missing)}")
        self._failure_classes[failure_class.failure_class_id] = failure_class

    def attach_incident(self, failure_class_id: str, incident_id: str) -> FailureClass:
        if incident_id not in self._incidents:
            raise ValueError(f"unknown incident: {incident_id}")
        current = self._failure_classes[failure_class_id]
        if incident_id in current.incident_ids:
            return current
        updated = replace(current, incident_ids=(*current.incident_ids, incident_id))
        self._failure_classes[failure_class_id] = updated
        return updated

    def repeat_count(self, failure_class_id: str) -> int:
        return len(self._failure_classes[failure_class_id].incident_ids)

    def is_systemic(self, failure_class_id: str, *, threshold: int = 2) -> bool:
        return self.repeat_count(failure_class_id) >= threshold
