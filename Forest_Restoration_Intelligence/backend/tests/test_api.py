def test_chat_primary_scenario_matches_brief_example(client):
    resp = client.post(
        "/chat",
        json={
            "message": (
                "A forest area has experienced deforestation. Rainfall has "
                "decreased and average temperature has increased."
            )
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "chain_result"
    result = data["result"]
    assert result["path"] == "primary"
    assert len(result["chain"]) == 5
    assert all(node["evidence_source_ids"] for node in result["chain"])
    assert result["recommendations"]
    assert any(r["addresses_link"] == "water_stress->vegetation_stress" for r in result["recommendations"])


def test_chat_fragmentation_scenario(client):
    resp = client.post(
        "/chat",
        json={
            "message": (
                "A forest patch has been isolated by agricultural expansion. "
                "There has been no major change in rainfall or temperature."
            )
        },
    )
    data = resp.json()
    assert data["type"] == "chain_result"
    assert data["result"]["path"] == "secondary"
    nodes = [n["node"] for n in data["result"]["chain"]]
    assert "fragmentation" in nodes
    assert "water_stress" not in nodes


def test_chat_incomplete_input_triggers_clarifying_question(client):
    resp = client.post("/chat", json={"message": "Biodiversity in this area is declining."})
    data = resp.json()
    assert data["type"] == "clarifying_question"
    assert data["message"]
    assert data["result"] is None


def test_analyze_structured_input_matches_brief_example(client):
    resp = client.post(
        "/analyze",
        json={"deforestation": True, "temperature_trend": "increasing", "rainfall_trend": "decreasing"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "chain_result"
    result = data["result"]
    assert result["path"] == "primary"
    assert all(n["evidence_source_ids"] for n in result["chain"])
    assert all(r["sources"] for r in result["recommendations"])


def test_analyze_incomplete_input_triggers_clarifying_question(client):
    resp = client.post("/analyze", json={"region": "Amazon"})
    data = resp.json()
    assert data["type"] == "clarifying_question"


def test_chain_evidence_endpoint_returns_citation_trail(client):
    resp = client.post(
        "/analyze",
        json={"deforestation": True, "temperature_trend": "increasing", "rainfall_trend": "decreasing"},
    )
    result_id = resp.json()["result"]["result_id"]

    ev = client.get(f"/chain-evidence/{result_id}")
    assert ev.status_code == 200
    body = ev.json()
    assert body["chain_evidence"]
    assert body["recommendation_sources"]
    for _, sources in body["chain_evidence"].items():
        for src in sources:
            assert "title" in src and "url" in src


def test_session_state_persists_and_context_carries_over(client):
    first = client.post("/chat", json={"message": "A forest area has experienced deforestation."})
    first_data = first.json()
    assert first_data["type"] == "clarifying_question"
    session_id = first_data["session_id"]

    second = client.post(
        "/chat",
        json={"message": "Rainfall has decreased.", "session_id": session_id},
    )
    second_data = second.json()
    assert second_data["type"] == "chain_result"
    assert second_data["result"]["path"] == "primary"

    state = client.get(f"/session/{session_id}")
    assert state.status_code == 200
    assert state.json()["variables"]["deforestation"] is True


def test_unknown_session_returns_404(client):
    resp = client.get("/session/does-not-exist")
    assert resp.status_code == 404
