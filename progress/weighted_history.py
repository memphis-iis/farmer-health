"""Weighted history scoring (placeholder weights, pending client / math input)."""

IMPROVING = "IMPROVING"
STABLE = "STABLE"
WORSENING = "WORSENING"


class WeightedHistoryModel:
    version = "weighted-history-placeholder"

    def __init__(self, today_weight=0.5, half_life_days=90, trend_window=3,
                 baselines=None, trend_threshold=0.25):
        if not 0 <= today_weight <= 1:
            raise ValueError("today_weight must be between 0 and 1.")
        if half_life_days <= 0:
            raise ValueError("half_life_days must be greater than 0.")
        self.today_weight = today_weight
        self.half_life_days = half_life_days
        self.trend_window = trend_window
        self.trend_threshold = trend_threshold
        # {month number: expected average score}; empty means no seasonal change.
        self.baselines = baselines or {}

    def decay_weight(self, age_days):
        """Return how much a result counts: 1.0 today, 0.5 after one half-life."""
        if age_days < 0:
            raise ValueError("age_days cannot be negative.")
        return 0.5 ** (age_days / self.half_life_days)

    def weighted_history(self, past_results, today):
        """Return the decay-weighted average of (date, score) pairs, or None."""
        weights = []
        total = 0.0
        for when, score in past_results:
            weight = self.decay_weight((today - when).days)
            weights.append(weight)
            total += weight * score
        if not weights or sum(weights) == 0:
            return None
        return total / sum(weights)

    def blended_score(self, today_score, today, past_results):
        """Blend today's score with the weighted history."""
        history = self.weighted_history(past_results, today)
        if history is None:
            return float(today_score)
        return self.today_weight * today_score + (1 - self.today_weight) * history

    def seasonal_adjust(self, score, month):
        """Remove the expected seasonal swing from a score."""
        if not self.baselines or month not in self.baselines:
            return score
        average = sum(self.baselines.values()) / len(self.baselines)
        return score - (self.baselines[month] - average)

    def trend_direction(self, scores):
        """Compare the latest scores (oldest to newest) with the ones before them."""
        recent = scores[-self.trend_window:]
        earlier = scores[:-self.trend_window]
        if not earlier:
            return STABLE
        change = sum(recent) / len(recent) - sum(earlier) / len(earlier)
        if change > self.trend_threshold:
            return WORSENING  # a higher score means more stress
        if change < -self.trend_threshold:
            return IMPROVING
        return STABLE
