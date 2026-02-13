"""
Historic hazard tools for ERAD MCP Server.
"""

import sqlite3

from loguru import logger

from erad.models.hazard.wind import WindModel
from erad.models.hazard.earthquake import EarthQuakeModel
from erad.models.hazard.wild_fire import FireModel

from .state import state
from .helpers import get_historic_hazard_db


async def list_historic_hurricanes_tool(args: dict) -> dict:
    """List historic hurricanes from database."""
    year = args.get("year")
    limit = args.get("limit", 50)

    try:
        db_path = get_historic_hazard_db()
        if not db_path.exists():
            return {"error": f"Historic hazard database not found at {db_path}"}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = 'SELECT DISTINCT "SID ", "NAME ", "SEASON (Year)" FROM historic_hurricanes'
        params = []

        if year:
            query += ' WHERE "SEASON (Year)" = ?'
            params.append(year)

        query += ' ORDER BY "SEASON (Year)" DESC, "NAME " LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        hurricanes = [{"sid": row[0], "name": row[1], "season": row[2]} for row in results]

        logger.info(f"Found {len(hurricanes)} historic hurricanes")

        return {"success": True, "count": len(hurricanes), "hurricanes": hurricanes}

    except Exception as e:
        logger.error(f"Error listing hurricanes: {e}")
        return {"error": str(e)}


async def list_historic_earthquakes_tool(args: dict) -> dict:
    """List historic earthquakes from database."""
    min_magnitude = args.get("min_magnitude")
    limit = args.get("limit", 50)

    try:
        db_path = get_historic_hazard_db()
        if not db_path.exists():
            return {"error": f"Historic hazard database not found at {db_path}"}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = "SELECT ID, Date, Magnitude, Latitude, Longitude FROM historic_earthquakes"
        params = []

        if min_magnitude:
            query += " WHERE Magnitude >= ?"
            params.append(min_magnitude)

        query += " ORDER BY Magnitude DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        earthquakes = [
            {
                "code": row[0],
                "date": row[1],
                "magnitude": row[2],
                "latitude": row[3],
                "longitude": row[4],
            }
            for row in results
        ]

        logger.info(f"Found {len(earthquakes)} historic earthquakes")

        return {"success": True, "count": len(earthquakes), "earthquakes": earthquakes}

    except Exception as e:
        logger.error(f"Error listing earthquakes: {e}")
        return {"error": str(e)}


async def list_historic_wildfires_tool(args: dict) -> dict:
    """List historic wildfires from database."""
    year = args.get("year")
    limit = args.get("limit", 50)

    try:
        db_path = get_historic_hazard_db()
        if not db_path.exists():
            return {"error": f"Historic hazard database not found at {db_path}"}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = "SELECT DISTINCT firename, fireyear FROM historic_fires"
        params = []

        if year:
            query += " WHERE fireyear = ?"
            params.append(year)

        query += " ORDER BY fireyear DESC, firename LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        wildfires = [{"fire_name": row[0], "fire_year": row[1]} for row in results]

        logger.info(f"Found {len(wildfires)} historic wildfires")

        return {"success": True, "count": len(wildfires), "wildfires": wildfires}

    except Exception as e:
        logger.error(f"Error listing wildfires: {e}")
        return {"error": str(e)}


async def load_historic_hurricane_tool(args: dict) -> dict:
    """Load historic hurricane into hazard system."""
    hazard_system_id = args["hazard_system_id"]
    hurricane_sid = args["hurricane_sid"]

    try:
        if hazard_system_id not in state.hazard_systems:
            return {"error": f"Hazard system not found: {hazard_system_id}"}

        hazard_system = state.hazard_systems[hazard_system_id]

        logger.info(f"Loading hurricane {hurricane_sid}")
        wind_models = WindModel.from_hurricane_sid(hurricane_sid)

        if not wind_models:
            return {"error": f"No wind models found for hurricane {hurricane_sid}"}

        # Add all timesteps to hazard system
        for wind_model in wind_models:
            hazard_system.add_component(wind_model)

        return {
            "success": True,
            "hurricane_sid": hurricane_sid,
            "timesteps_loaded": len(wind_models),
            "first_timestamp": wind_models[0].timestamp.isoformat(),
            "last_timestamp": wind_models[-1].timestamp.isoformat(),
            "message": f"Hurricane {hurricane_sid} with {len(wind_models)} timesteps added to hazard system {hazard_system_id}",
        }

    except Exception as e:
        logger.error(f"Error loading hurricane: {e}")
        return {"error": str(e)}


async def load_historic_earthquake_tool(args: dict) -> dict:
    """Load historic earthquake into hazard system."""
    hazard_system_id = args["hazard_system_id"]
    earthquake_code = args["earthquake_code"]

    try:
        if hazard_system_id not in state.hazard_systems:
            return {"error": f"Hazard system not found: {hazard_system_id}"}

        hazard_system = state.hazard_systems[hazard_system_id]

        logger.info(f"Loading earthquake {earthquake_code}")
        earthquake_model = EarthQuakeModel.from_earthquake_code(earthquake_code)
        hazard_system.add_component(earthquake_model)

        return {
            "success": True,
            "earthquake_code": earthquake_code,
            "magnitude": float(earthquake_model.magnitude),
            "timestamp": earthquake_model.timestamp.isoformat(),
            "message": f"Earthquake {earthquake_code} added to hazard system {hazard_system_id}",
        }

    except Exception as e:
        logger.error(f"Error loading earthquake: {e}")
        return {"error": str(e)}


async def load_historic_wildfire_tool(args: dict) -> dict:
    """Load historic wildfire into hazard system."""
    hazard_system_id = args["hazard_system_id"]
    wildfire_name = args["wildfire_name"]

    try:
        if hazard_system_id not in state.hazard_systems:
            return {"error": f"Hazard system not found: {hazard_system_id}"}

        hazard_system = state.hazard_systems[hazard_system_id]

        logger.info(f"Loading wildfire {wildfire_name}")
        fire_model = FireModel.from_wildfire_name(wildfire_name)
        hazard_system.add_component(fire_model)

        return {
            "success": True,
            "wildfire_name": wildfire_name,
            "timestamp": fire_model.timestamp.isoformat(),
            "affected_areas_count": len(fire_model.affected_areas),
            "message": f"Wildfire {wildfire_name} with {len(fire_model.affected_areas)} affected areas added to hazard system {hazard_system_id}",
        }

    except Exception as e:
        logger.error(f"Error loading wildfire: {e}")
        return {"error": str(e)}
