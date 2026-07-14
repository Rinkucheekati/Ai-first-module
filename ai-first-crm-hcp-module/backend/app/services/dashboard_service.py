from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.schemas.dashboard import DashboardMeeting, DashboardSummary


class DashboardService:
    """Build the dashboard read model from HCP and interaction records."""

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> DashboardSummary:
        now = datetime.now()
        start_of_today = datetime.combine(now.date(), time.min)
        start_of_tomorrow = start_of_today + timedelta(days=1)

        total_hcps = self.db.query(HCP).count()
        total_interactions = self.db.query(Interaction).count()
        todays_meetings = self.db.query(Interaction).filter(
            Interaction.interaction_date >= start_of_today,
            Interaction.interaction_date < start_of_tomorrow,
        ).count()
        pending_follow_ups = self.db.query(Interaction).filter(
            Interaction.follow_up_date.isnot(None),
            Interaction.follow_up_date <= start_of_tomorrow,
        ).count()

        upcoming_rows = self.db.query(Interaction, HCP.doctor_name).join(HCP).filter(
            Interaction.interaction_date >= start_of_tomorrow,
        ).order_by(Interaction.interaction_date.asc()).limit(5).all()

        summary_rows = self.db.query(Interaction, HCP.doctor_name).join(HCP).filter(
            Interaction.summary.isnot(None),
            Interaction.summary != "",
        ).order_by(Interaction.interaction_date.desc()).limit(5).all()

        return DashboardSummary(
            total_hcps=total_hcps,
            total_interactions=total_interactions,
            todays_meetings=todays_meetings,
            pending_follow_ups=pending_follow_ups,
            upcoming_meetings=[self._meeting(interaction, doctor_name) for interaction, doctor_name in upcoming_rows],
            recent_ai_summaries=[self._meeting(interaction, doctor_name) for interaction, doctor_name in summary_rows],
        )

    @staticmethod
    def _meeting(interaction: Interaction, doctor_name: str) -> DashboardMeeting:
        return DashboardMeeting(
            id=interaction.id,
            hcp_name=doctor_name,
            interaction_date=interaction.interaction_date,
            follow_up_date=interaction.follow_up_date,
            summary=interaction.summary,
        )
