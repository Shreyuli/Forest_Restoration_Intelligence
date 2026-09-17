from app import completeness


def test_missing_everything_triggers_question():
    assert completeness.check_completeness({}) is not None


def test_biodiversity_mention_alone_triggers_question():
    # No deforestation/fragmentation, no climate trend — must ask, not guess.
    assert completeness.check_completeness({"region": "Amazon"}) is not None


def test_deforestation_alone_triggers_question():
    variables = {"deforestation": True}
    assert completeness.check_completeness(variables) is not None


def test_deforestation_plus_climate_is_complete():
    variables = {
        "deforestation": True,
        "temperature_trend": "increasing",
        "rainfall_trend": "decreasing",
    }
    assert completeness.check_completeness(variables) is None


def test_fragmentation_alone_is_complete():
    variables = {"fragmentation": True}
    assert completeness.check_completeness(variables) is None


def test_region_note_only_appears_when_region_and_geo_missing():
    assert completeness.region_note({"region": "Amazon"}, None) is None
    assert completeness.region_note({}, {"typical_biome": "tropical_moist_broadleaf"}) is None
    assert completeness.region_note({}, None) is not None
