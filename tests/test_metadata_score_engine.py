from core.engines.metadata_score_engine import MetadataScoreEngine, MetadataSignals


def test_metadata_score_engine_strong_profile() -> None:
    engine = MetadataScoreEngine()
    score = engine.score(
        MetadataSignals(
            has_title=True,
            has_year=True,
            has_overview=True,
            has_poster=True,
            has_backdrop=True,
            has_genres=True,
            has_cast=True,
            has_subtitles=True,
            has_runtime=True,
        )
    )
    assert score >= 80


def test_metadata_score_engine_penalties() -> None:
    engine = MetadataScoreEngine()
    score = engine.score(
        MetadataSignals(
            has_title=True,
            has_year=False,
            has_overview=False,
            has_poster=False,
            has_backdrop=False,
            has_genres=False,
            has_cast=False,
            has_subtitles=False,
            has_runtime=False,
            duplicate_suspected=True,
            bad_filename=True,
        )
    )
    assert score == 0
