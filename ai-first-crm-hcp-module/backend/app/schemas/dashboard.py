from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DashboardMeeting(BaseModel):
    id: int
    hcp_name: str
    interaction_date: datetime
    follow_up_date: Optional[datetime] = None
    summary: Optional[str] = None


class DashboardSummary(BaseModel):
    total_hcps: int
    total_interactions: int
    todays_meetings: int
    pending_follow_ups: int
    upcoming_meetings: List[DashboardMeeting]
    recent_ai_summaries: List[DashboardMeeting]
