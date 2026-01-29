"""
MCP (Model Context Protocol) Server for ERAD Hazard Simulator.

This module provides an MCP server that exposes:
- Cached distribution models as resources
- Simulation and scenario generation as tools
- Hazard types and curve sets as prompts

Usage:
    python -m erad.mcp

Or with uvx:
    uvx mcp run erad.mcp:mcp
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    ResourceTemplate,
    Tool,
    TextContent,
    Prompt,
    PromptMessage,
    PromptArgument,
    GetPromptResult,
)
from pydantic import AnyUrl

from gdm.distribution import DistributionSystem
from erad.runner import HazardSimulator, HazardScenarioGenerator
from erad.systems.asset_system import AssetSystem
from erad.systems.hazard_system import HazardSystem
from erad.models.asset import Asset

logger = logging.getLogger(__name__)


# ========== Cache Directory Management ==========


def get_cache_directory() -> Path:
    """Get the standard cache directory for ERAD distribution models."""
    if os.name == "nt":  # Windows
        cache_base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:  # Unix-like (Linux, macOS)
        cache_base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))

    cache_dir = cache_base / "erad" / "distribution_models"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_hazard_cache_directory() -> Path:
    """Get the standard cache directory for ERAD hazard models."""
    if os.name == "nt":  # Windows
        cache_base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:  # Unix-like (Linux, macOS)
        cache_base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))

    cache_dir = cache_base / "erad" / "hazard_models"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_metadata_file() -> Path:
    """Get the metadata file path for distribution models."""
    return get_cache_directory() / "models_metadata.json"


def get_hazard_metadata_file() -> Path:
    """Get the metadata file path for hazard models."""
    return get_hazard_cache_directory() / "models_metadata.json"


def load_cached_models() -> dict[str, dict]:
    """Load all cached models with their metadata."""
    metadata_file = get_metadata_file()
    models = {}

    if metadata_file.exists():
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                for name, info in metadata.items():
                    file_path = Path(info.get("file_path", ""))
                    if file_path.exists():
                        models[name] = {
                            "name": name,
                            "description": info.get("description"),
                            "created_at": info.get("created_at"),
                            "file_path": str(file_path),
                        }
        except Exception as e:
            logger.warning(f"Failed to load distribution models metadata: {e}")

    # Also scan directory for files not in metadata
    cache_dir = get_cache_directory()
    for file_path in cache_dir.glob("*.json"):
        if file_path.name == "models_metadata.json":
            logger.info("Skipping metadata file")
            continue

        # Extract model name
        filename = file_path.stem
        parts = filename.rsplit("_", 1)
        if len(parts) == 2 and parts[1].replace(".", "").isdigit():
            model_name = parts[0]
        else:
            model_name = filename

        if model_name not in models:
            try:
                # Validate it's a valid distribution system
                with open(file_path, "r") as f:
                    data = json.load(f)
                _ = DistributionSystem(**data)

                stats = file_path.stat()
                models[model_name] = {
                    "name": model_name,
                    "description": f"Loaded from {file_path.name}",
                    "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    "file_path": str(file_path),
                }
            except Exception:  # noqa: B112
                logger.info(f"Skipping invalid distribution model file: {file_path}")
                continue

    return models


def load_cached_hazard_models() -> dict[str, dict]:
    """Load all cached hazard models with their metadata."""
    metadata_file = get_hazard_metadata_file()
    models = {}

    if metadata_file.exists():
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                for name, info in metadata.items():
                    file_path = Path(info.get("file_path", ""))
                    if file_path.exists():
                        models[name] = {
                            "name": name,
                            "description": info.get("description"),
                            "created_at": info.get("created_at"),
                            "file_path": str(file_path),
                        }
        except Exception as e:
            logger.warning(f"Failed to load hazard models metadata: {e}")

    # Also scan directory for files not in metadata
    cache_dir = get_hazard_cache_directory()
    for file_path in cache_dir.glob("*.json"):
        if file_path.name == "models_metadata.json":
            logger.info("Skipping metadata file")
            continue

        # Extract model name
        filename = file_path.stem
        parts = filename.rsplit("_", 1)
        if len(parts) == 2 and parts[1].replace(".", "").isdigit():
            model_name = parts[0]
        else:
            model_name = filename

        if model_name not in models:
            try:
                # Validate it's a valid hazard system
                with open(file_path, "r") as f:
                    data = json.load(f)
                _ = HazardSystem.from_json(data)

                stats = file_path.stat()
                models[model_name] = {
                    "name": model_name,
                    "description": f"Loaded from {file_path.name}",
                    "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    "file_path": str(file_path),
                }
            except Exception:  # noqa: B112
                logger.info(f"Skipping invalid hazard model file: {file_path}")
                continue

    return models


def load_distribution_system(model_name: str) -> DistributionSystem:
    """Load a distribution system by name."""
    models = load_cached_models()
    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not found in cache")

    file_path = models[model_name]["file_path"]
    with open(file_path, "r") as f:
        data = json.load(f)
    return DistributionSystem(**data)


def load_hazard_system(model_name: str) -> HazardSystem:
    """Load a hazard system by name."""
    models = load_cached_hazard_models()
    if model_name not in models:
        raise ValueError(f"Hazard model '{model_name}' not found in cache")

    file_path = models[model_name]["file_path"]
    with open(file_path, "r") as f:
        data = json.load(f)
    return HazardSystem.from_json(data)


def create_hazard_system(hazard_models: list[dict]) -> HazardSystem:
    """Create a hazard system from hazard model data."""
    from erad.models.hazard import (
        EarthQuakeModel,
        FloodModel,
        FloodModelArea,
        WindModel,
        FireModel,
        FireModelArea,
    )

    hazard_type_mapping = {
        "earthquake": EarthQuakeModel,
        "flood": FloodModel,
        "flood_area": FloodModelArea,
        "wind": WindModel,
        "fire": FireModel,
        "fire_area": FireModelArea,
    }

    hazard_system = HazardSystem()

    for model_data in hazard_models:
        hazard_type = model_data.get("hazard_type", "").lower()
        hazard_class = hazard_type_mapping.get(hazard_type)

        if not hazard_class:
            raise ValueError(f"Unknown hazard type: {hazard_type}")

        # Parse timestamp
        timestamp = model_data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()

        hazard_model = hazard_class(
            name=model_data.get("name", "hazard"),
            timestamp=timestamp,
            **model_data.get("model_data", {}),
        )
        hazard_system.add_component(hazard_model)

    return hazard_system


# ========== MCP Server ==========

mcp = Server("erad-hazard-simulator")


@mcp.list_resources()
async def list_resources() -> list[Resource]:
    """List all cached distribution models and hazard models as resources."""
    dist_models = load_cached_models()
    hazard_models = load_cached_hazard_models()
    resources = []

    # Add distribution models
    for name, info in dist_models.items():
        resources.append(
            Resource(
                uri=AnyUrl(f"erad://models/{name}"),
                name=f"Distribution Model: {name}",
                description=info.get("description") or f"Distribution system model '{name}'",
                mimeType="application/json",
            )
        )

    # Add hazard models
    for name, info in hazard_models.items():
        resources.append(
            Resource(
                uri=AnyUrl(f"erad://hazards/{name}"),
                name=f"Hazard Model: {name}",
                description=info.get("description") or f"Hazard system model '{name}'",
                mimeType="application/json",
            )
        )

    # Add cache info resource
    resources.append(
        Resource(
            uri=AnyUrl("erad://cache/info"),
            name="Cache Information",
            description="Information about the ERAD model cache directory",
            mimeType="application/json",
        )
    )

    # Add supported hazard types resource
    resources.append(
        Resource(
            uri=AnyUrl("erad://hazards/types"),
            name="Supported Hazard Types",
            description="List of supported hazard types for simulation",
            mimeType="application/json",
        )
    )

    return resources


@mcp.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    """List resource templates for dynamic model access."""
    return [
        ResourceTemplate(
            uriTemplate="erad://models/{model_name}",
            name="Distribution Model",
            description="Access a specific distribution system model by name",
            mimeType="application/json",
        ),
        ResourceTemplate(
            uriTemplate="erad://models/{model_name}/summary",
            name="Model Summary",
            description="Get a summary of a distribution system model",
            mimeType="text/plain",
        ),
        ResourceTemplate(
            uriTemplate="erad://hazards/{model_name}",
            name="Hazard Model",
            description="Access a specific hazard system model by name",
            mimeType="application/json",
        ),
        ResourceTemplate(
            uriTemplate="erad://hazards/{model_name}/summary",
            name="Hazard Model Summary",
            description="Get a summary of a hazard system model",
            mimeType="text/plain",
        ),
    ]


def _read_cache_info() -> str:
    """Read cache information resource."""
    cache_dir = get_cache_directory()
    models = load_cached_models()
    model_files = list(cache_dir.glob("*.json"))
    model_files = [f for f in model_files if f.name != "models_metadata.json"]
    total_size = sum(f.stat().st_size for f in model_files)

    return json.dumps(
        {
            "cache_directory": str(cache_dir),
            "metadata_file": str(get_metadata_file()),
            "total_models": len(models),
            "total_files": len(model_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "models": list(models.keys()),
        },
        indent=2,
    )


def _read_hazard_types() -> str:
    """Read hazard types resource."""
    return json.dumps(
        {
            "hazard_types": ["earthquake", "flood", "flood_area", "wind", "fire", "fire_area"],
            "descriptions": {
                "earthquake": "Earthquake Model (EarthQuakeModel)",
                "flood": "Flood Model (FloodModel)",
                "flood_area": "Flood Area Model (FloodModelArea)",
                "wind": "Wind Model (WindModel)",
                "fire": "Fire Model (FireModel)",
                "fire_area": "Fire Area Model (FireModelArea)",
            },
        },
        indent=2,
    )


def _create_model_summary(model_name: str, model_info: dict, data: dict) -> str:
    """Create a summary for a distribution model."""
    summary_lines = [
        f"# Distribution System: {model_name}",
        "",
        f"**Created**: {model_info.get('created_at', 'Unknown')}",
        f"**Description**: {model_info.get('description', 'No description')}",
        f"**File**: {model_info['file_path']}",
        "",
        "## Content Summary",
        f"- Keys: {', '.join(data.keys()) if isinstance(data, dict) else 'N/A'}",
    ]

    if isinstance(data, dict):
        if "components" in data:
            summary_lines.append(f"- Components: {len(data.get('components', []))}")
        if "name" in data:
            summary_lines.append(f"- System Name: {data['name']}")

    return "\n".join(summary_lines)


def _create_hazard_model_summary(model_name: str, model_info: dict, data: dict) -> str:
    """Create a summary for a hazard model."""
    summary_lines = [
        f"# Hazard System: {model_name}",
        "",
        f"**Created**: {model_info.get('created_at', 'Unknown')}",
        f"**Description**: {model_info.get('description', 'No description')}",
        f"**File**: {model_info['file_path']}",
        "",
        "## Content Summary",
        f"- Keys: {', '.join(data.keys()) if isinstance(data, dict) else 'N/A'}",
    ]

    if isinstance(data, dict):
        if "models" in data:
            summary_lines.append(f"- Hazard models: {len(data.get('models', []))}")
        if "timestamps" in data:
            summary_lines.append(f"- Timestamps: {len(data.get('timestamps', []))}")

    return "\n".join(summary_lines)


def _read_distribution_model(uri_str: str) -> str:
    """Read a distribution model resource."""
    path_parts = uri_str.replace("erad://models/", "").split("/")
    model_name = path_parts[0]

    models = load_cached_models()
    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not found")

    file_path = models[model_name]["file_path"]

    # Check if summary requested
    if len(path_parts) > 1 and path_parts[1] == "summary":
        with open(file_path, "r") as f:
            data = json.load(f)
        return _create_model_summary(model_name, models[model_name], data)

    # Return full model content
    with open(file_path, "r") as f:
        return f.read()


def _read_hazard_model(uri_str: str) -> str:
    """Read a hazard model resource."""
    # Check if it's the types resource
    if uri_str == "erad://hazards/types":
        return _read_hazard_types()

    path_parts = uri_str.replace("erad://hazards/", "").split("/")
    model_name = path_parts[0]

    models = load_cached_hazard_models()
    if model_name not in models:
        raise ValueError(f"Hazard model '{model_name}' not found")

    file_path = models[model_name]["file_path"]

    # Check if summary requested
    if len(path_parts) > 1 and path_parts[1] == "summary":
        with open(file_path, "r") as f:
            data = json.load(f)
        return _create_hazard_model_summary(model_name, models[model_name], data)

    # Return full model content
    with open(file_path, "r") as f:
        return f.read()


@mcp.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read a resource by URI."""
    uri_str = str(uri)

    # Handle cache info
    if uri_str == "erad://cache/info":
        return _read_cache_info()

    # Handle hazard types
    if uri_str == "erad://hazards/types":
        return _read_hazard_types()

    # Handle distribution model resources
    if uri_str.startswith("erad://models/"):
        return _read_distribution_model(uri_str)

    # Handle hazard model resources
    if uri_str.startswith("erad://hazards/"):
        return _read_hazard_model(uri_str)

    raise ValueError(f"Unknown resource URI: {uri_str}")


@mcp.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="run_simulation",
            description="Run a hazard simulation on a distribution system model using cached models. Loads distribution and hazard systems from cache by name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "distribution_system_name": {
                        "type": "string",
                        "description": "Name of the cached distribution system model",
                    },
                    "hazard_system_name": {
                        "type": "string",
                        "description": "Name of the cached hazard system model",
                    },
                    "curve_set": {
                        "type": "string",
                        "description": "Fragility curve set to use (default: DEFAULT_CURVES)",
                        "default": "DEFAULT_CURVES",
                    },
                },
                "required": ["distribution_system_name", "hazard_system_name"],
            },
        ),
        Tool(
            name="generate_scenarios",
            description="Generate Monte Carlo hazard scenarios using cached models. Returns scenario data with tracked changes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "distribution_system_name": {
                        "type": "string",
                        "description": "Name of the cached distribution system model",
                    },
                    "hazard_system_name": {
                        "type": "string",
                        "description": "Name of the cached hazard system model",
                    },
                    "number_of_samples": {
                        "type": "integer",
                        "description": "Number of scenarios to generate",
                        "default": 1,
                        "minimum": 1,
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Random seed for reproducibility",
                        "default": 0,
                    },
                    "curve_set": {
                        "type": "string",
                        "description": "Fragility curve set to use",
                        "default": "DEFAULT_CURVES",
                    },
                },
                "required": ["distribution_system_name", "hazard_system_name"],
            },
        ),
        Tool(
            name="list_cached_models",
            description="List all distribution system models available in the cache.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_model_info",
            description="Get detailed information about a specific cached model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the model to get info for",
                    }
                },
                "required": ["model_name"],
            },
        ),
        Tool(
            name="refresh_cache",
            description="Refresh the model cache by scanning the cache directory for new or updated models.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_cache_info",
            description="Get information about the cache directory including location, size, and model count.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="list_cached_hazard_models",
            description="List all hazard system models available in the cache.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_hazard_model_info",
            description="Get detailed information about a specific cached hazard model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the hazard model to get info for",
                    }
                },
                "required": ["model_name"],
            },
        ),
    ]


def _tool_list_cached_models() -> list[TextContent]:
    """Handle list_cached_models tool."""
    models = load_cached_models()
    result = {
        "total_models": len(models),
        "models": [
            {
                "name": info["name"],
                "description": info.get("description"),
                "created_at": info.get("created_at"),
            }
            for info in models.values()
        ],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def _tool_get_model_info(model_name: str) -> list[TextContent]:
    """Handle get_model_info tool."""
    if not model_name:
        return [TextContent(type="text", text="Error: model_name is required")]

    models = load_cached_models()
    if model_name not in models:
        return [TextContent(type="text", text=f"Error: Model '{model_name}' not found")]

    info = models[model_name]

    try:
        file_path = info["file_path"]
        with open(file_path, "r") as f:
            data = json.load(f)

        file_size = Path(file_path).stat().st_size

        result = {
            "name": model_name,
            "description": info.get("description"),
            "created_at": info.get("created_at"),
            "file_path": file_path,
            "file_size_bytes": file_size,
            "content_keys": list(data.keys()) if isinstance(data, dict) else None,
            "component_count": len(data.get("components", [])) if isinstance(data, dict) else None,
        }
    except Exception as e:
        result = {"name": model_name, "error": str(e), **info}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def _tool_refresh_cache() -> list[TextContent]:
    """Handle refresh_cache tool."""
    models = load_cached_models()
    result = {
        "status": "success",
        "message": "Cache refreshed",
        "total_models": len(models),
        "models": list(models.keys()),
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def _tool_get_cache_info() -> list[TextContent]:
    """Handle get_cache_info tool."""
    cache_dir = get_cache_directory()
    models = load_cached_models()
    model_files = list(cache_dir.glob("*.json"))
    model_files = [f for f in model_files if f.name != "models_metadata.json"]
    total_size = sum(f.stat().st_size for f in model_files)

    result = {
        "cache_directory": str(cache_dir),
        "metadata_file": str(get_metadata_file()),
        "total_models": len(models),
        "total_files": len(model_files),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def _tool_run_simulation(dist_name: str, hazard_name: str, curve_set: str) -> list[TextContent]:
    """Handle run_simulation tool."""
    if not dist_name:
        return [TextContent(type="text", text="Error: distribution_system_name is required")]

    if not hazard_name:
        return [TextContent(type="text", text="Error: hazard_system_name is required")]

    try:
        # Load distribution system from cache
        dist_system = load_distribution_system(dist_name)

        # Create asset system
        asset_system = AssetSystem.from_gdm(dist_system)

        # Load hazard system from cache
        hazard_system = load_hazard_system(hazard_name)

        # Run simulation
        simulator = HazardSimulator(asset_system)
        simulator.run(hazard_system, curve_set)

        # Get results
        assets = list(asset_system.get_components(Asset))
        timestamps = simulator.timestamps

        result = {
            "status": "success",
            "message": "Simulation completed successfully",
            "distribution_system_name": dist_name,
            "hazard_system_name": hazard_name,
            "asset_count": len(assets),
            "hazard_count": len(list(hazard_system.get_all_components())),
            "timestamps": [t.isoformat() for t in timestamps],
            "curve_set": curve_set,
        }

    except Exception as e:
        result = {
            "status": "error",
            "message": f"Simulation failed: {str(e)}",
            "distribution_system_name": dist_name,
            "hazard_system_name": hazard_name,
        }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def _tool_generate_scenarios(
    dist_name: str, hazard_name: str, number_of_samples: int, seed: int, curve_set: str
) -> list[TextContent]:
    """Handle generate_scenarios tool."""
    if not dist_name:
        return [TextContent(type="text", text="Error: distribution_system_name is required")]

    if not hazard_name:
        return [TextContent(type="text", text="Error: hazard_system_name is required")]

    try:
        # Load distribution system from cache
        dist_system = load_distribution_system(dist_name)

        # Create asset system
        asset_system = AssetSystem.from_gdm(dist_system)

        # Load hazard system from cache
        hazard_system = load_hazard_system(hazard_name)

        # Generate scenarios
        generator = HazardScenarioGenerator(
            asset_system=asset_system, hazard_system=hazard_system, curve_set=curve_set
        )

        tracked_changes = generator.samples(number_of_samples=number_of_samples, seed=seed)

        # Format results
        scenarios = []
        for change in tracked_changes:
            scenarios.append(
                {
                    "scenario_name": change.scenario_name,
                    "timestamp": change.timestamp.isoformat(),
                    "edits": [
                        {
                            "component_uuid": edit.component_uuid,
                            "name": edit.name,
                            "value": edit.value,
                        }
                        for edit in change.edits
                    ],
                }
            )

        result = {
            "status": "success",
            "message": "Scenarios generated successfully",
            "distribution_system_name": dist_name,
            "hazard_system_name": hazard_name,
            "number_of_samples": number_of_samples,
            "seed": seed,
            "total_scenarios": len(scenarios),
            "scenarios": scenarios,
        }

    except Exception as e:
        result = {
            "status": "error",
            "message": f"Scenario generation failed: {str(e)}",
            "distribution_system_name": dist_name,
            "hazard_system_name": hazard_name,
        }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def _tool_list_cached_hazard_models() -> list[TextContent]:
    """Handle list_cached_hazard_models tool."""
    models = load_cached_hazard_models()
    result = {
        "total_models": len(models),
        "models": [
            {
                "name": info["name"],
                "description": info.get("description"),
                "created_at": info.get("created_at"),
            }
            for info in models.values()
        ],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def _tool_get_hazard_model_info(model_name: str) -> list[TextContent]:
    """Handle get_hazard_model_info tool."""
    if not model_name:
        return [TextContent(type="text", text="Error: model_name is required")]

    models = load_cached_hazard_models()
    if model_name not in models:
        return [TextContent(type="text", text=f"Error: Hazard model '{model_name}' not found")]

    info = models[model_name]

    try:
        file_path = info["file_path"]
        with open(file_path, "r") as f:
            data = json.load(f)

        file_size = Path(file_path).stat().st_size

        result = {
            "name": model_name,
            "description": info.get("description"),
            "created_at": info.get("created_at"),
            "file_path": file_path,
            "file_size_bytes": file_size,
            "content_keys": list(data.keys()) if isinstance(data, dict) else None,
            "hazard_model_count": len(data.get("models", [])) if isinstance(data, dict) else None,
            "timestamp_count": len(data.get("timestamps", [])) if isinstance(data, dict) else None,
        }
    except Exception as e:
        result = {"name": model_name, "error": str(e), **info}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


@mcp.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""

    if name == "list_cached_models":
        return _tool_list_cached_models()

    elif name == "get_model_info":
        return _tool_get_model_info(arguments.get("model_name"))

    elif name == "refresh_cache":
        return _tool_refresh_cache()

    elif name == "get_cache_info":
        return _tool_get_cache_info()

    elif name == "run_simulation":
        return _tool_run_simulation(
            arguments.get("distribution_system_name"),
            arguments.get("hazard_system_name"),
            arguments.get("curve_set", "DEFAULT_CURVES"),
        )

    elif name == "generate_scenarios":
        return _tool_generate_scenarios(
            arguments.get("distribution_system_name"),
            arguments.get("hazard_system_name"),
            arguments.get("number_of_samples", 1),
            arguments.get("seed", 0),
            arguments.get("curve_set", "DEFAULT_CURVES"),
        )

    elif name == "list_cached_hazard_models":
        return _tool_list_cached_hazard_models()

    elif name == "get_hazard_model_info":
        return _tool_get_hazard_model_info(arguments.get("model_name"))

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


@mcp.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompts."""
    return [
        Prompt(
            name="simulate_hazard",
            description="Generate a prompt for running a hazard simulation on a distribution system",
            arguments=[
                PromptArgument(
                    name="model_name",
                    description="Name of the distribution system model",
                    required=True,
                ),
                PromptArgument(
                    name="hazard_type",
                    description="Type of hazard (earthquake, flood, wind, fire, etc.)",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="analyze_vulnerability",
            description="Generate a prompt for analyzing system vulnerability to hazards",
            arguments=[
                PromptArgument(
                    name="model_name",
                    description="Name of the distribution system model",
                    required=True,
                )
            ],
        ),
    ]


@mcp.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific prompt."""

    if name == "simulate_hazard":
        model_name = arguments.get("model_name", "unknown") if arguments else "unknown"
        hazard_type = arguments.get("hazard_type", "earthquake") if arguments else "earthquake"

        return GetPromptResult(
            description=f"Simulate {hazard_type} hazard on {model_name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I want to run a hazard simulation on the distribution system model '{model_name}'.

Please help me:
1. First, check if the model '{model_name}' exists in the cache using the list_cached_models tool
2. Get information about the model using get_model_info
3. Set up a {hazard_type} hazard scenario with appropriate parameters
4. Run the simulation using run_simulation
5. Explain the results and what they mean for system resilience

The hazard type '{hazard_type}' should use realistic parameters for the simulation.""",
                    ),
                )
            ],
        )

    elif name == "analyze_vulnerability":
        model_name = arguments.get("model_name", "unknown") if arguments else "unknown"

        return GetPromptResult(
            description=f"Analyze vulnerability of {model_name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I want to analyze the vulnerability of the distribution system '{model_name}' to various natural hazards.

Please help me:
1. First, load the model information using get_model_info for '{model_name}'
2. Run simulations for multiple hazard types (earthquake, flood, wind, fire)
3. Generate scenario samples to understand potential outage patterns
4. Summarize which hazards pose the greatest risk
5. Provide recommendations for improving system resilience

Use realistic hazard parameters and generate at least 10 scenario samples for each hazard type.""",
                    ),
                )
            ],
        )

    raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
