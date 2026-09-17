from app import chain_engine, db_models


def test_primary_path_full_chain(db_session):
    """Exact brief scenario: deforestation + temp increase + rainfall decrease."""
    variables = {
        "deforestation": True,
        "temperature_trend": "increasing",
        "rainfall_trend": "decreasing",
        "fragmentation": None,
        "region": None,
    }
    assert chain_engine.determine_path(variables) == "primary"

    result = chain_engine.run_chain_result(db_session, variables, None)
    nodes = [n["node"] for n in result["chain"]]
    assert nodes == [
        "trigger",
        "water_stress",
        "vegetation_stress",
        "habitat_degradation",
        "biodiversity_decline",
    ]

    for node in result["chain"]:
        assert node["evidence_source_ids"], f"No evidence bound for edge into {node['node']}"

    water_stress_recs = [
        r for r in result["recommendations"] if r["addresses_link"] == "water_stress->vegetation_stress"
    ]
    assert water_stress_recs, "Expected at least one recommendation mapped to the water-stress link"


def test_secondary_path_routes_through_fragmentation(db_session):
    """Fragmentation-only scenario, no rainfall/temperature change."""
    variables = {
        "deforestation": None,
        "fragmentation": True,
        "temperature_trend": "stable",
        "rainfall_trend": "stable",
        "region": None,
    }
    assert chain_engine.determine_path(variables) == "secondary"

    result = chain_engine.run_chain_result(db_session, variables, None)
    nodes = [n["node"] for n in result["chain"]]
    assert "fragmentation" in nodes
    assert "water_stress" not in nodes
    assert "vegetation_stress" not in nodes

    frag_recs = [
        r for r in result["recommendations"] if r["addresses_link"] == "fragmentation->habitat_degradation"
    ]
    assert frag_recs, "Expected a recommendation mapped to the fragmentation link"


def test_combined_path_when_both_signals_present(db_session):
    variables = {
        "deforestation": True,
        "fragmentation": True,
        "temperature_trend": "increasing",
        "rainfall_trend": "decreasing",
    }
    assert chain_engine.determine_path(variables) == "combined"
    result = chain_engine.run_chain_result(db_session, variables, None)
    nodes = [n["node"] for n in result["chain"]]
    assert "fragmentation" in nodes
    assert "water_stress" in nodes


def test_every_edge_and_recommendation_has_resolvable_sources(db_session):
    variables = {
        "deforestation": True,
        "temperature_trend": "increasing",
        "rainfall_trend": "decreasing",
    }
    result = chain_engine.run_chain_result(db_session, variables, None)

    for node in result["chain"]:
        assert node["evidence_source_ids"]
        for source_id in node["evidence_source_ids"]:
            assert db_session.query(db_models.Source).filter_by(source_id=source_id).first() is not None

    assert result["recommendations"]
    for rec in result["recommendations"]:
        assert rec["sources"]
        for source_id in rec["sources"]:
            assert db_session.query(db_models.Source).filter_by(source_id=source_id).first() is not None
