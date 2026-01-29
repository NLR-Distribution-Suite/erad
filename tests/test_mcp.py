"""Tests for ERAD MCP Server."""

import json
import tempfile
from pathlib import Path

import pytest
from datetime import datetime
from unittest.mock import Mock, patch


# ========== Fixtures ==========


@pytest.fixture
def sample_model_data():
    """Sample distribution model data."""
    return {
        "name": "test_system",
        "components": [
            {"uuid": "asset_1", "type": "transformer"},
            {"uuid": "asset_2", "type": "line"},
        ],
        "properties": {"voltage_level": "12.47kV"},
    }


@pytest.fixture
def sample_hazard_models():
    """Sample hazard model data."""
    return [
        {
            "name": "earthquake_1",
            "hazard_type": "earthquake_pga",
            "timestamp": datetime.now().isoformat(),
            "model_data": {"data": {"asset_1": 0.5}},
        }
    ]


@pytest.fixture
def mock_cache_models():
    """Mock cached models."""
    temp_dir = Path(tempfile.gettempdir())
    return {
        "test_model": {
            "name": "test_model",
            "description": "Test model",
            "created_at": datetime.now().isoformat(),
            "file_path": str(temp_dir / "test_model.json"),
        }
    }


# ========== Unit Tests ==========


class TestCacheDirectoryManagement:
    """Tests for cache directory management functions."""

    def test_get_cache_directory(self):
        """Test cache directory creation."""
        from erad.mcp import get_cache_directory

        cache_dir = get_cache_directory()

        assert cache_dir.exists()
        assert cache_dir.is_dir()
        assert "erad" in str(cache_dir)
        assert "distribution_models" in str(cache_dir)

    def test_get_metadata_file(self):
        """Test metadata file path."""
        from erad.mcp import get_metadata_file

        metadata_file = get_metadata_file()

        assert "models_metadata.json" in str(metadata_file)

    def test_load_cached_models(self):
        """Test loading cached models."""
        from erad.mcp import load_cached_models

        models = load_cached_models()

        assert isinstance(models, dict)

    @patch("erad.mcp.load_cached_models")
    def test_load_distribution_system_not_found(self, mock_load):
        """Test loading non-existent model."""
        from erad.mcp import load_distribution_system

        mock_load.return_value = {}

        with pytest.raises(ValueError, match="not found"):
            load_distribution_system("nonexistent_model")


class TestHazardSystemCreation:
    """Tests for hazard system creation."""

    def test_create_hazard_system_unknown_type(self):
        """Test creating hazard system with unknown type."""
        from erad.mcp import create_hazard_system

        hazard_models = [{"name": "test", "hazard_type": "unknown_hazard", "model_data": {}}]

        with pytest.raises(ValueError, match="Unknown hazard type"):
            create_hazard_system(hazard_models)


# ========== Async Tests for MCP Server ==========


@pytest.mark.asyncio
class TestMCPResources:
    """Tests for MCP resource listing and reading."""

    async def test_list_resources(self):
        """Test listing resources."""
        from erad.mcp import list_resources

        resources = await list_resources()

        assert isinstance(resources, list)
        # Should have at least cache info and hazard types
        assert len(resources) >= 2

        # Find cache info resource
        cache_info = [r for r in resources if "cache" in str(r.uri)]
        assert len(cache_info) >= 1

        # Find hazard types resource
        hazard_types = [r for r in resources if "hazards" in str(r.uri)]
        assert len(hazard_types) >= 1

    async def test_list_resource_templates(self):
        """Test listing resource templates."""
        from erad.mcp import list_resource_templates

        templates = await list_resource_templates()

        assert isinstance(templates, list)
        assert len(templates) >= 1

    async def test_read_cache_info_resource(self):
        """Test reading cache info resource."""
        from erad.mcp import read_resource
        from pydantic import AnyUrl

        result = await read_resource(AnyUrl("erad://cache/info"))

        data = json.loads(result)
        assert "cache_directory" in data
        assert "total_models" in data
        assert "total_files" in data

    async def test_read_hazard_types_resource(self):
        """Test reading hazard types resource."""
        from erad.mcp import read_resource
        from pydantic import AnyUrl

        result = await read_resource(AnyUrl("erad://hazards/types"))

        data = json.loads(result)
        assert "hazard_types" in data
        assert "earthquake" in data["hazard_types"]
        assert "flood" in data["hazard_types"]

    async def test_read_unknown_resource(self):
        """Test reading unknown resource."""
        from erad.mcp import read_resource
        from pydantic import AnyUrl

        with pytest.raises(ValueError, match="Unknown resource"):
            await read_resource(AnyUrl("erad://unknown/resource"))


@pytest.mark.asyncio
class TestMCPTools:
    """Tests for MCP tools."""

    async def test_list_tools(self):
        """Test listing available tools."""
        from erad.mcp import list_tools

        tools = await list_tools()

        assert isinstance(tools, list)
        assert len(tools) >= 8  # Should have at least 8 tools

        tool_names = [t.name for t in tools]
        assert "run_simulation" in tool_names
        assert "generate_scenarios" in tool_names
        assert "list_cached_models" in tool_names
        assert "get_model_info" in tool_names
        assert "refresh_cache" in tool_names
        assert "get_cache_info" in tool_names
        assert "list_cached_hazard_models" in tool_names
        assert "get_hazard_model_info" in tool_names

    async def test_call_list_cached_models(self):
        """Test calling list_cached_models tool."""
        from erad.mcp import call_tool

        result = await call_tool("list_cached_models", {})

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "total_models" in data
        assert "models" in data

    async def test_call_get_cache_info(self):
        """Test calling get_cache_info tool."""
        from erad.mcp import call_tool

        result = await call_tool("get_cache_info", {})

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "cache_directory" in data
        assert "total_models" in data
        assert "total_size_bytes" in data

    async def test_call_refresh_cache(self):
        """Test calling refresh_cache tool."""
        from erad.mcp import call_tool

        result = await call_tool("refresh_cache", {})

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert "models" in data

    async def test_call_get_model_info_not_found(self):
        """Test calling get_model_info for non-existent model."""
        from erad.mcp import call_tool

        result = await call_tool("get_model_info", {"model_name": "nonexistent"})

        assert len(result) == 1
        assert "not found" in result[0].text

    async def test_call_get_model_info_missing_arg(self):
        """Test calling get_model_info without model_name."""
        from erad.mcp import call_tool

        result = await call_tool("get_model_info", {})

        assert len(result) == 1
        assert "required" in result[0].text.lower()

    async def test_call_run_simulation_missing_model(self):
        """Test calling run_simulation without distribution_system_name."""
        from erad.mcp import call_tool

        result = await call_tool("run_simulation", {"hazard_system_name": "test_hazard"})

        assert len(result) == 1
        assert "required" in result[0].text.lower()

    async def test_call_run_simulation_missing_hazards(self):
        """Test calling run_simulation without hazard_system_name."""
        from erad.mcp import call_tool

        result = await call_tool("run_simulation", {"distribution_system_name": "test"})

        assert len(result) == 1
        assert "required" in result[0].text.lower()

    async def test_call_generate_scenarios_missing_model(self):
        """Test calling generate_scenarios without distribution_system_name."""
        from erad.mcp import call_tool

        result = await call_tool("generate_scenarios", {"hazard_system_name": "test_hazard"})

        assert len(result) == 1
        assert "required" in result[0].text.lower()

    async def test_call_unknown_tool(self):
        """Test calling unknown tool."""
        from erad.mcp import call_tool

        result = await call_tool("unknown_tool", {})

        assert len(result) == 1
        assert "Unknown tool" in result[0].text

    async def test_call_list_cached_hazard_models(self):
        """Test calling list_cached_hazard_models tool."""
        from erad.mcp import call_tool

        result = await call_tool("list_cached_hazard_models", {})

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "total_models" in data
        assert "models" in data

    async def test_call_get_hazard_model_info_not_found(self):
        """Test calling get_hazard_model_info for non-existent model."""
        from erad.mcp import call_tool

        result = await call_tool("get_hazard_model_info", {"model_name": "nonexistent"})

        assert len(result) == 1
        assert "not found" in result[0].text

    async def test_call_get_hazard_model_info_missing_arg(self):
        """Test calling get_hazard_model_info without model_name."""
        from erad.mcp import call_tool

        result = await call_tool("get_hazard_model_info", {})

        assert len(result) == 1
        assert "required" in result[0].text.lower()


@pytest.mark.asyncio
class TestMCPPrompts:
    """Tests for MCP prompts."""

    async def test_list_prompts(self):
        """Test listing available prompts."""
        from erad.mcp import list_prompts

        prompts = await list_prompts()

        assert isinstance(prompts, list)
        assert len(prompts) >= 2

        prompt_names = [p.name for p in prompts]
        assert "simulate_hazard" in prompt_names
        assert "analyze_vulnerability" in prompt_names

    async def test_get_simulate_hazard_prompt(self):
        """Test getting simulate_hazard prompt."""
        from erad.mcp import get_prompt

        result = await get_prompt(
            "simulate_hazard", {"model_name": "test_model", "hazard_type": "earthquake_pga"}
        )

        assert result.description is not None
        assert len(result.messages) >= 1
        assert "test_model" in result.messages[0].content.text
        assert "earthquake_pga" in result.messages[0].content.text

    async def test_get_analyze_vulnerability_prompt(self):
        """Test getting analyze_vulnerability prompt."""
        from erad.mcp import get_prompt

        result = await get_prompt("analyze_vulnerability", {"model_name": "test_model"})

        assert result.description is not None
        assert len(result.messages) >= 1
        assert "test_model" in result.messages[0].content.text

    async def test_get_unknown_prompt(self):
        """Test getting unknown prompt."""
        from erad.mcp import get_prompt

        with pytest.raises(ValueError, match="Unknown prompt"):
            await get_prompt("unknown_prompt", {})


# ========== Integration Tests ==========


@pytest.mark.integration
@pytest.mark.asyncio
class TestMCPIntegration:
    """Integration tests for MCP server."""

    @patch("erad.mcp.load_cached_models")
    @patch("erad.mcp.load_cached_hazard_models")
    @patch("erad.mcp.load_distribution_system")
    @patch("erad.mcp.load_hazard_system")
    @patch("erad.mcp.AssetSystem")
    @patch("erad.mcp.HazardSimulator")
    async def test_full_simulation_workflow(
        self,
        mock_simulator_class,
        mock_asset_system_class,
        mock_load_hazard_system,
        mock_load_dist,
        mock_load_hazard_models,
        mock_load_models,
    ):
        """Test full simulation workflow with cached models."""
        from erad.mcp import call_tool

        # Setup mocks for distribution model
        temp_dir = Path(tempfile.gettempdir())
        mock_load_models.return_value = {
            "test_model": {"name": "test_model", "file_path": str(temp_dir / "test.json")}
        }

        # Setup mocks for hazard model
        mock_load_hazard_models.return_value = {
            "test_hazard": {"name": "test_hazard", "file_path": str(temp_dir / "hazard.json")}
        }

        mock_dist_system = Mock()
        mock_load_dist.return_value = mock_dist_system

        mock_hazard_system = Mock()
        mock_hazard_system.get_all_components.return_value = [Mock()]
        mock_load_hazard_system.return_value = mock_hazard_system

        mock_asset_system = Mock()
        mock_asset = Mock()
        mock_asset_system.get_components.return_value = [mock_asset]
        mock_asset_system_class.from_gdm.return_value = mock_asset_system

        mock_simulator = Mock()
        mock_simulator.timestamps = [datetime.now()]
        mock_simulator_class.return_value = mock_simulator

        # Call tool
        result = await call_tool(
            "run_simulation",
            {"distribution_system_name": "test_model", "hazard_system_name": "test_hazard"},
        )

        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["distribution_system_name"] == "test_model"
        assert data["hazard_system_name"] == "test_hazard"
