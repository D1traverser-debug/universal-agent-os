from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC,datetime,timedelta

@dataclass(frozen=True,slots=True)
class OpportunisticMaintenanceDecision:
    due:bool
    run_now:bool
    priority:str
    reasons:tuple[str,...]

def assess_opportunistic_maintenance(*,now:datetime|None=None,last_success:datetime|None,max_interval:timedelta=timedelta(hours=24),unresolved_incidents:int=0,foreground_runnable:int=0,recovery_required:bool=False)->OpportunisticMaintenanceDecision:
    now=now or datetime.now(UTC); reasons=[]
    if recovery_required: reasons.append("recovery required")
    if unresolved_incidents>0: reasons.append(f"{unresolved_incidents} unresolved incident(s)")
    if last_success is None: reasons.append("maintenance has never completed")
    elif now-last_success>=max_interval: reasons.append("maintenance interval elapsed")
    due=bool(reasons); run_now=due and foreground_runnable==0
    if due and foreground_runnable>0: reasons.append("deferred behind foreground work")
    priority="HIGH" if recovery_required else ("MEDIUM" if unresolved_incidents else "LOW")
    return OpportunisticMaintenanceDecision(due,run_now,priority,tuple(reasons))
