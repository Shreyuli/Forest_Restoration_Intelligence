"""Fixed causal-chain templates for the forest-restoration domain.

Two paths are defined, per the brief:

PRIMARY  (climate/water-stress driven):
  deforestation + temperature_increase + rainfall_decrease
      -> water_stress -> vegetation_stress -> habitat_degradation -> biodiversity_decline

SECONDARY (fragmentation driven, no climate signal required):
  deforestation / agricultural_expansion -> fragmentation
      -> habitat_degradation -> biodiversity_decline

Each entry's ``tag`` is the chain-link tag used to filter retrieval so that
evidence is bound per-edge, not just to the final recommendation.
"""

PRIMARY_CHAIN = [
    {
        "node": "trigger",
        "label": "Deforestation + Temperature Increase + Rainfall Decrease",
        "tag": "trigger",
    },
    {
        "node": "water_stress",
        "label": "Water Stress",
        "tag": "deforestation_temp_rainfall->water_stress",
    },
    {
        "node": "vegetation_stress",
        "label": "Vegetation Stress",
        "tag": "water_stress->vegetation_stress",
    },
    {
        "node": "habitat_degradation",
        "label": "Habitat Degradation",
        "tag": "vegetation_stress->habitat_degradation",
    },
    {
        "node": "biodiversity_decline",
        "label": "Biodiversity Decline",
        "tag": "habitat_degradation->biodiversity_decline",
    },
]

SECONDARY_CHAIN = [
    {
        "node": "trigger",
        "label": "Deforestation / Agricultural Expansion",
        "tag": "deforestation_agri->fragmentation",
    },
    {
        "node": "fragmentation",
        "label": "Habitat Fragmentation",
        "tag": "deforestation_agri->fragmentation",
    },
    {
        "node": "habitat_degradation",
        "label": "Habitat Degradation",
        "tag": "fragmentation->habitat_degradation",
    },
    {
        "node": "biodiversity_decline",
        "label": "Biodiversity Decline",
        "tag": "habitat_degradation->biodiversity_decline",
    },
]

# Recommendation strategies, each tagged with the edge they primarily address.
# The engine prefers the strategy addressing the most upstream broken link.
INTERVENTIONS = [
    {
        "what_to_do": "Assisted natural regeneration with native pioneer species",
        "addresses_link": "water_stress->vegetation_stress",
        "retrieval_tag": "regeneration->vegetation_recovery",
        "time_horizon": "medium",
        "why_template": (
            "Restores canopy cover and evapotranspiration, which lowers surface "
            "temperature and reduces moisture loss, directly interrupting the "
            "water-stress link upstream of vegetation and habitat decline."
        ),
    },
    {
        "what_to_do": "Water-retention and soil-moisture measures (mulching, contour trenching, riparian buffers)",
        "addresses_link": "water_stress->vegetation_stress",
        # No dedicated corpus chunks for this specific intervention (as opposed
        # to regeneration in general) — its citation comes only from the
        # matching EvidenceCoefficient row, so we deliberately don't borrow
        # retrieval hits tagged for a different intervention.
        "retrieval_tag": "",
        "time_horizon": "short",
        "why_template": (
            "Increases soil moisture retention at the site level, buying vegetation "
            "time to recover while canopy cover is rebuilt, easing the water-stress "
            "to vegetation-stress transition."
        ),
    },
    {
        "what_to_do": "Native species reintroduction / enrichment planting",
        "addresses_link": "habitat_degradation->biodiversity_decline",
        "retrieval_tag": "reintroduction->biodiversity_recovery",
        "time_horizon": "long",
        "why_template": (
            "Rebuilds habitat structure and food resources for forest-dependent "
            "fauna, directly counteracting species loss once habitat quality has "
            "already degraded."
        ),
    },
    {
        "what_to_do": "Corridor restoration and buffer planting to reconnect fragments",
        "addresses_link": "fragmentation->habitat_degradation",
        "retrieval_tag": "connectivity->habitat_recovery",
        "time_horizon": "medium",
        "why_template": (
            "Reduces isolation between fragments, restoring species movement and "
            "gene flow, which interrupts the fragmentation-to-habitat-degradation "
            "link before it compounds into biodiversity decline."
        ),
    },
]

CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}
