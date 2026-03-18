from dataclasses import dataclass


@dataclass(slots=True)
class MetadataSignals:
    has_title: bool = True
    has_year: bool = True
    has_overview: bool = False
    has_poster: bool = False
    has_backdrop: bool = False
    has_genres: bool = False
    has_cast: bool = False
    has_subtitles: bool = False
    has_runtime: bool = False
    duplicate_suspected: bool = False
    bad_filename: bool = False


class MetadataScoreEngine:
    """Calculate a 0-100 quality score using deterministic weighted signals."""

    WEIGHTS = {
        "has_title": 12,
        "has_year": 8,
        "has_overview": 15,
        "has_poster": 10,
        "has_backdrop": 8,
        "has_genres": 8,
        "has_cast": 8,
        "has_subtitles": 12,
        "has_runtime": 7,
    }
    PENALTIES = {
        "duplicate_suspected": 8,
        "bad_filename": 12,
    }

    def score(self, signals: MetadataSignals) -> int:
        total = 0
        for key, weight in self.WEIGHTS.items():
            if getattr(signals, key):
                total += weight

        for key, penalty in self.PENALTIES.items():
            if getattr(signals, key):
                total -= penalty

        return max(0, min(100, total))
