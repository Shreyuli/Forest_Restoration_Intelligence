"""Geo-coordinate -> biome/climate lookup (bonus feature)."""
from typing import Optional

from sqlalchemy.orm import Session

from . import db_models


def lookup_biome(db: Session, lat: Optional[float], lon: Optional[float]) -> Optional[dict]:
    if lat is None or lon is None:
        return None
    rows = db.query(db_models.GeoBiomeLookup).all()
    for row in rows:
        if row.lat_min <= lat <= row.lat_max and row.lon_min <= lon <= row.lon_max:
            return {
                "region_key": row.region_key,
                "typical_biome": row.typical_biome,
                "baseline_rainfall": row.baseline_rainfall,
                "baseline_temp": row.baseline_temp,
            }
    return None
