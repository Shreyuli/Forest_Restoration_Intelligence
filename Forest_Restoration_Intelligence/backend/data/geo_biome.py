"""Static geo -> biome/climate lookup table (bonus feature).

Scoped to a handful of representative forest regions rather than global
coverage, per the TRD's risk mitigation for this component.
"""

GEO_BIOME_LOOKUP = [
    {
        "region_key": "amazon_basin",
        "lat_min": -10, "lat_max": 5, "lon_min": -75, "lon_max": -50,
        "typical_biome": "tropical_moist_broadleaf",
        "baseline_rainfall": "2000-3000 mm/yr",
        "baseline_temp": "25-27 C",
    },
    {
        "region_key": "congo_basin",
        "lat_min": -5, "lat_max": 5, "lon_min": 10, "lon_max": 30,
        "typical_biome": "tropical_moist_broadleaf",
        "baseline_rainfall": "1600-2000 mm/yr",
        "baseline_temp": "24-26 C",
    },
    {
        "region_key": "sundaland_se_asia",
        "lat_min": -5, "lat_max": 5, "lon_min": 95, "lon_max": 120,
        "typical_biome": "tropical_moist_broadleaf",
        "baseline_rainfall": "2500-3500 mm/yr",
        "baseline_temp": "26-28 C",
    },
    {
        "region_key": "western_ghats_india",
        "lat_min": 8, "lat_max": 21, "lon_min": 73, "lon_max": 77,
        "typical_biome": "tropical_moist_broadleaf_monsoon",
        "baseline_rainfall": "2000-6000 mm/yr (seasonal)",
        "baseline_temp": "20-28 C",
    },
    {
        "region_key": "eastern_himalaya_foothills",
        "lat_min": 26, "lat_max": 29, "lon_min": 88, "lon_max": 97,
        "typical_biome": "subtropical_broadleaf",
        "baseline_rainfall": "2000-4000 mm/yr",
        "baseline_temp": "15-25 C",
    },
    {
        "region_key": "boreal_canada",
        "lat_min": 50, "lat_max": 60, "lon_min": -110, "lon_max": -60,
        "typical_biome": "boreal_coniferous",
        "baseline_rainfall": "400-800 mm/yr",
        "baseline_temp": "-5-15 C",
    },
    {
        "region_key": "mediterranean_south_europe",
        "lat_min": 36, "lat_max": 44, "lon_min": -9, "lon_max": 20,
        "typical_biome": "mediterranean_forest",
        "baseline_rainfall": "400-800 mm/yr",
        "baseline_temp": "12-20 C",
    },
    {
        "region_key": "atlantic_forest_brazil",
        "lat_min": -25, "lat_max": -14, "lon_min": -48, "lon_max": -39,
        "typical_biome": "tropical_moist_broadleaf",
        "baseline_rainfall": "1200-2500 mm/yr",
        "baseline_temp": "18-24 C",
    },
]
