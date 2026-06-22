import os
import math
import sqlite3
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/facilities", tags=["Facilities"])

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface
    using the Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@router.get("/nearby")
def get_nearby_facilities(lat: float, lon: float, limit: int = 3):
    """
    Queries the SQLite database, calculates haversine distance for every row,
    and returns the closest `limit` facilities with all columns plus `distance_km`.
    """
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "phc_database.sqlite"
    )
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Database file not found.")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, district, state, pincode, lat, lon, phone FROM facilities")
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
    finally:
        conn.close()

    results = []
    for row in rows:
        row_dict = dict(row)
        dist = haversine(lat, lon, row_dict["lat"], row_dict["lon"])
        row_dict["distance_km"] = round(dist, 1)
        results.append(row_dict)

    # Sort by distance in ascending order
    results.sort(key=lambda x: x["distance_km"])
    return results[:limit]

@router.get("/by-pincode")
def get_facilities_by_pincode(pincode: str, limit: int = 3):
    """
    Returns facilities matching the specified pincode from the SQLite database.
    """
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "phc_database.sqlite"
    )
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Database file not found.")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, type, district, state, pincode, lat, lon, phone FROM facilities WHERE pincode = ? LIMIT ?",
            (pincode, limit)
        )
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
    finally:
        conn.close()

    return [dict(row) for row in rows]


