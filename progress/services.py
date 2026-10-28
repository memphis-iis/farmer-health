from dataclasses import dataclass
from datetime import date
from statistics import mean


@dataclass(frozen=True)
class ProgressPoint:
    date: date
    average_score: float
    weight_score: float
    tier: str

class ProgressService:
    def __init__(self, model, repository):
        self.model = model
        self.repository = repository

def _history(self, user):
    return sorted((a for a in self.repository.get_history(user) if a.completed_at),
            key=lambda a: a.completed_at,)

def weighted_trend(self, user) ->list[ProgressPoint]:
    points = []
    for a in self._history(user):
        result = self.model.score(user, a)
        points.append(ProgressPoint(
            date=a.completed_at.date(),
            average_score=result.average_score,
            weight_score=result.weight_score,
            tier=result.tier
        ))
    return points

def current_weighted_score(self, user) -> float | None:
    history = self._history(user)
    if not history:
        return None
    return self.model.score(user, history[-1]).weighted_score

def trend_direction(self, user):
    history = self._history(user)
    if not history:
        return None
    return self.model.score(user, history[-1]).trend_direction

def assessements_in_month(self, user, year: int, month: int) -> list:
    return [
        a for a in self._history(user)
        if a.completed_at.year == year and a.completed_at.month == month
    ]

def monthly_average(self, user, year: int, month: int) -> float | None:
        scores = [a.average_score for a in self.assessments_in_month(user, year, month)]
        return mean(scores) if scores else None