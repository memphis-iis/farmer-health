from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from assessments.models import TrendDirection
from resources.models import Tier

@dataclass(frozen=True)
class ScoreResult:
    average_score: float
    tier: Tier
    weighted_score: float
    trend_direction: TrendDirection


@dataclass(frozen=True)
class ProgressPoint:
    date: date
    average_score: float
    weighted_score: float
    tier: Tier


class ScoringModel(ABC):
    """Contract every scoring model follows. Does no math itself."""

    version = "base"

    @abstractmethod
    def score(self, user, assessment):
        """Return a ScoreResult for this assessment, in light of the user's history.
        Does not save anything; the caller writes the result onto the Assessment."""

    @abstractmethod
    def weighted_history(self, user):
        """Return one ProgressPoint per completed assessment, oldest first."""

class SimpleAverageModel(ScoringModel):
    version = "simple-average-v1"
    STABLE_THRESHOLD = 0.1

    def score(self, user, assessment):
        if assessment.user_id != user_id:
            raise ValueError("Assessment does not belong to this user")

        today = self._average_of(assessment)
        earlier = self._completed(user).filter(completed__lt=assessment.completed_at)

        averages = [a.average_score for a in earlier]
        average.append(today)


        return ScoreResult(
            average_score=today,
            tier=assessment.tier,
            weighted_score=self._mean(averages),
            trend_direction-self._trend(averages),
        )

    def weighted_history(self, user):
        points =[]
        running = []

        for a in self._completed(user):
            running.append(a.average_score)
            points.append(
                ProgressPoint(
                    date=a.completed_at.date(),
                    average_score=a.average_score,
                    weighted_score=self.mean(running),
                    tier=a.tier
                )
            )
        return points

    def _completed(self, user):
        # Completed and already averaged; a None average would break the math
        return user.assessments.filter(
            completed_at__isnull=False,
            average_score__isnull=False,
        ).order_by("completed_at")

    @staticmethod
    def _average_of(assessment):
        # Prefer the stored value; fall back to computing it from responses
        if assessment.average_score is not None:
            return assessment.average_score
        return assessment.calculate_average()

    @staticmethod
    def _mean(values):
        return sum(values) / len(values) if values else 0.0

    def _trend(self, averages):
        if len(averages) < 2:
            return TrendDirection.STABLE  # first assessment: nothing to compare

        diff = averages[-1] - self._mean(averages[:-1])
        if diff > self.STABLE_THRESHOLD:
            # Higher score = more stress = wellbeing DECLINED
            return TrendDirection.WORSENING
        if diff < -self.STABLE_THRESHOLD:
            return TrendDirection.IMPROVING
        return TrendDirection.STABLE