"""
Simulation tools for ERAD MCP Server.
"""

from datetime import datetime
from pathlib import Path

from loguru import logger
from gdm.distribution import DistributionSystem

from erad.runner import HazardSimulator, HazardScenarioGenerator
from erad.systems.asset_system import AssetSystem
from erad.systems.hazard_system import HazardSystem
from erad.constants import HAZARD_TYPES

from .state import state
from .helpers import get_cache_directory, load_metadata


async def load_distribution_model_tool(args: dict) -> dict:
    """Load a distribution model from file or cache."""
    source = args["source"]
    from_cache = args.get("from_cache", False)

    try:
        if from_cache:
            # Load from cache
            cache_dir = get_cache_directory()
            metadata = load_metadata(cache_dir)

            if source not in metadata:
                return {"error": f"Model '{source}' not found in cache"}

            file_path = cache_dir / metadata[source]["filename"]
        else:
            # Load from file path
            file_path = Path(source)
            if not file_path.exists():
                return {"error": f"File not found: {source}"}

        # Load the distribution system
        logger.info(f"Loading distribution model from {file_path}")
        dist_system = DistributionSystem.from_json(file_path)

        # Create asset system
        asset_system = AssetSystem.from_gdm(dist_system)

        # Store in state
        system_id = state.generate_id()
        state.asset_systems[system_id] = asset_system

        from erad.models.asset import Asset

        asset_count = len(list(asset_system.get_components(Asset)))

        logger.info(f"Loaded asset system {system_id} with {asset_count} assets")

        return {
            "success": True,
            "system_id": system_id,
            "asset_count": asset_count,
            "source": str(file_path),
        }

    except Exception as e:
        logger.error(f"Error loading distribution model: {e}")
        return {"error": str(e)}


async def load_hazard_model_tool(args: dict) -> dict:
    """Load a hazard model from JSON file."""
    file_path = Path(args["file_path"])

    try:
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        logger.info(f"Loading hazard model from {file_path}")
        hazard_system = HazardSystem.from_json(file_path)

        # Store in state
        system_id = state.generate_id()
        state.hazard_systems[system_id] = hazard_system

        # Count hazard models
        hazard_count = sum(
            len(list(hazard_system.get_components(hazard_type))) for hazard_type in HAZARD_TYPES
        )

        logger.info(f"Loaded hazard system {system_id} with {hazard_count} hazard models")

        return {
            "success": True,
            "system_id": system_id,
            "hazard_count": hazard_count,
            "source": str(file_path),
        }

    except Exception as e:
        logger.error(f"Error loading hazard model: {e}")
        return {"error": str(e)}


async def create_hazard_system_tool(args: dict) -> dict:
    """Create a new empty hazard system."""
    try:
        hazard_system = HazardSystem(auto_add_composed_components=True)
        system_id = state.generate_id()
        state.hazard_systems[system_id] = hazard_system

        logger.info(f"Created new hazard system {system_id}")

        return {
            "success": True,
            "system_id": system_id,
            "message": "Empty hazard system created. Use load_historic_* tools to add hazards.",
        }

    except Exception as e:
        logger.error(f"Error creating hazard system: {e}")
        return {"error": str(e)}


async def run_simulation_tool(args: dict) -> dict:
    """Run a hazard simulation."""
    asset_system_id = args["asset_system_id"]
    hazard_system_id = args["hazard_system_id"]
    curve_set = args.get("curve_set", "DEFAULT_CURVES")

    try:
        # Validate systems exist
        if asset_system_id not in state.asset_systems:
            return {"error": f"Asset system not found: {asset_system_id}"}
        if hazard_system_id not in state.hazard_systems:
            return {"error": f"Hazard system not found: {hazard_system_id}"}

        asset_system = state.asset_systems[asset_system_id]
        hazard_system = state.hazard_systems[hazard_system_id]

        # Create simulator
        logger.info(
            f"Running simulation: asset={asset_system_id}, hazard={hazard_system_id}, curves={curve_set}"
        )
        simulator = HazardSimulator(asset_system)

        # Run simulation
        simulator.run(hazard_system, curve_set)

        # Store results
        simulation_id = state.generate_id()
        state.hazard_simulators[simulation_id] = simulator
        state.simulation_results[simulation_id] = {
            "asset_system_id": asset_system_id,
            "hazard_system_id": hazard_system_id,
            "curve_set": curve_set,
            "timestamp": datetime.now().isoformat(),
            "asset_count": len(simulator.assets),
            "timestamps": [ts.isoformat() for ts in simulator.timestamps],
        }

        logger.info(
            f"Simulation {simulation_id} completed with {len(simulator.timestamps)} timesteps"
        )

        return {
            "success": True,
            "simulation_id": simulation_id,
            "asset_count": len(simulator.assets),
            "timesteps": len(simulator.timestamps),
            "timestamps": [ts.isoformat() for ts in simulator.timestamps],
        }

    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        return {"error": str(e)}


async def generate_scenarios_tool(args: dict) -> dict:
    """Generate Monte Carlo scenarios from simulation."""
    simulation_id = args["simulation_id"]
    num_samples = args.get("num_samples", 1)
    seed = args.get("seed", 0)

    try:
        if simulation_id not in state.simulation_results:
            return {"error": f"Simulation not found: {simulation_id}"}

        sim_info = state.simulation_results[simulation_id]
        asset_system_id = sim_info["asset_system_id"]
        hazard_system_id = sim_info["hazard_system_id"]
        curve_set = sim_info["curve_set"]

        asset_system = state.asset_systems[asset_system_id]
        hazard_system = state.hazard_systems[hazard_system_id]

        logger.info(f"Generating {num_samples} scenarios for simulation {simulation_id}")

        # Generate scenarios
        generator = HazardScenarioGenerator(asset_system, hazard_system, curve_set)
        tracked_changes = generator.samples(num_samples, seed)

        # Store tracked changes
        state.simulation_results[simulation_id]["tracked_changes"] = tracked_changes

        # Summarize results
        scenarios = {}
        for change in tracked_changes:
            if change.scenario_name not in scenarios:
                scenarios[change.scenario_name] = {"outages": 0, "timestamps": set()}
            scenarios[change.scenario_name]["outages"] += len(change.edits)
            scenarios[change.scenario_name]["timestamps"].add(change.timestamp.isoformat())

        # Convert sets to lists for JSON serialization
        for scenario in scenarios.values():
            scenario["timestamps"] = sorted(list(scenario["timestamps"]))

        logger.info(
            f"Generated {num_samples} scenarios with total {len(tracked_changes)} tracked changes"
        )

        return {
            "success": True,
            "simulation_id": simulation_id,
            "num_samples": num_samples,
            "total_tracked_changes": len(tracked_changes),
            "scenarios": scenarios,
        }

    except Exception as e:
        logger.error(f"Error generating scenarios: {e}")
        return {"error": str(e)}
