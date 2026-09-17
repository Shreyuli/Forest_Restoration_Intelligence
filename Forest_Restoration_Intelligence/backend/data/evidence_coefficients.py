"""Quantified intervention-effect coefficients extracted from the seed corpus.

Used for the "impacted metric, by how much" part of every recommendation,
since free-text retrieval alone is not reliable for numeric claims.
"""

EVIDENCE_COEFFICIENTS = [
    {
        "intervention": "Assisted natural regeneration with native pioneer species",
        "addresses_link": "water_stress->vegetation_stress",
        "effect_metric": "canopy_cover_recovery",
        "effect_size": "70-80% of reference forest value",
        "effect_range": "within ~20 years",
        "biome": "tropical_moist_broadleaf",
        "source_id": "crouzeilles2017",
    },
    {
        "intervention": "Assisted natural regeneration with native pioneer species",
        "addresses_link": "vegetation_stress->habitat_degradation",
        "effect_metric": "aboveground_biomass",
        "effect_size": "~66% of old-growth biomass",
        "effect_range": "by year 20",
        "biome": "tropical_moist_broadleaf",
        "source_id": "chazdon2008",
    },
    {
        "intervention": "Active enrichment planting on severely degraded sites",
        "addresses_link": "water_stress->vegetation_stress",
        "effect_metric": "canopy_closure_time",
        "effect_size": "faster canopy closure than passive regeneration",
        "effect_range": "on degraded soils, 3-7 years",
        "biome": "general_tropical",
        "source_id": "holl_aide2011",
    },
    {
        "intervention": "Water-retention and soil-moisture measures (mulching, contour trenching, riparian buffers)",
        "addresses_link": "water_stress->vegetation_stress",
        "effect_metric": "soil_moisture",
        "effect_size": "+15-30% relative soil moisture retention",
        "effect_range": "first 1-3 years post-intervention",
        "biome": "dry_tropical_forest",
        "source_id": "ellison2017",
    },
    {
        "intervention": "Native species reintroduction / enrichment planting",
        "addresses_link": "habitat_degradation->biodiversity_decline",
        "effect_metric": "species_richness",
        "effect_size": "notable increase vs. unassisted recovery (site-dependent)",
        "effect_range": "5-15 years",
        "biome": "tropical_moist_broadleaf",
        "source_id": "lamb2005",
    },
    {
        "intervention": "Corridor restoration and buffer planting to reconnect fragments",
        "addresses_link": "fragmentation->habitat_degradation",
        "effect_metric": "patch_connectivity",
        "effect_size": "restores species movement and gene flow between fragments",
        "effect_range": "5-10 years",
        "biome": "general_tropical",
        "source_id": "tambosi2014",
    },
    {
        "intervention": "Corridor restoration and buffer planting to reconnect fragments",
        "addresses_link": "fragmentation->habitat_degradation",
        "effect_metric": "species_persistence",
        "effect_size": "reduces fragmentation-driven extinction debt",
        "effect_range": "long-term (decades)",
        "biome": "general",
        "source_id": "haddad2015",
    },
]
