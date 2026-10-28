from dataclasses import dataclass
from datetime import date
from statistics import mean

from django.utils import timezone



@dataclass(frozen=True)
class ProgressPoint:
    date: date
    average_score: float | None
    weighted_score: float | None
    tier: str

class ProgressService:
    def __init__(self, repository=None):
        self.repository = repository

    def _history(self, user):
        if self.repository is not None:
            rows = self.repository.get_history(user)
        else:
                rows = user.assessments.all()
        return sorted(
                (a for a in rows if a.completed_at),
                key=lambda a: a.completed_at,
            )

    def weighted_trend(self, user) ->list[ProgressPoint]:
        return[
            ProgressPoint(
                date=timezone.localtime(a.completed_at).date(),
                average_score=a.weighted_score,
                weighted_score=a.weighted_score, 
                tier=a.tier,
                )
                for a in self._history(user)
        ]

    def current_weighted_score(self, user) -> float | None:
        history = self._history(user)
        return history[-1].weighted_score if history else None

    def trend_direction(self, user):
        history = self._history(user)
        return history[-1].trend_direction if history else None

    def assessements_in_month(self, user, year: int, month: int) -> list:
        return [
                a for a in self._history(user)
                if timezone.localtime(a.completed_at).year == year
                and timezone.localtime(a.completed_at).month == month
            ]

    def monthly_average(self, user, year: int, month: int) -> float | None:
            scores = [
                a.average_score
                for a in self.assessements_in_month(user, year, month)
                if a.average_score is not None
            ]
            return mean(scores) if scores else None