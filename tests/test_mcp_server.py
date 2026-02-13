"""
Tests for ERAD MCP Server
"""

import pytest
from unittest.mock import Mock

# Import from new modular structure
from erad.mcp.state import ServerState, state
from erad.mcp.simulation import (
    create_hazard_system_tool,
    run_simulation_tool,
)
from erad.mcp.assets import (
    query_assets_tool,
    get_asset_statistics_tool,
)
from erad.mcp.utilities import (
    list_asset_types_tool,
    list_loaded_systems_tool,
)
from erad.mcp.cache import get_cache_info_tool
from erad.mcp.fragility import list_fragility_curves_tool


@pytest.fixture
def clean_state():
    """Clean server state before each test."""
    state.clear()
    yield state
    state.clear()


@pytest.fixture
def sample_gdm_model(tmp_path):
    """Create a sample GDM model file."""
    # You would need to create a minimal valid GDM JSON here
    # For now, return None to skip file-based tests
    return None


class TestServerState:
    """Test ServerState class."""

    def test_generate_id(self):
        """Test ID generation."""
        state = ServerState()
        id1 = state.generate_id()
        id2 = state.generate_id()

        assert len(id1) == 8
        assert len(id2) == 8
        assert id1 != id2

    def test_clear(self):
        """Test state clearing."""
        state = ServerState()
        state.asset_systems["test"] = Mock()
        state.hazard_systems["test"] = Mock()
        state.simulation_results["test"] = {}

        state.clear()

        assert len(state.asset_systems) == 0
        assert len(state.hazard_systems) == 0
        assert len(state.simulation_results) == 0


class TestSimulationTools:
    """Test simulation tool functions."""

    @pytest.mark.asyncio
    async def test_create_hazard_system(self, clean_state):
        """Test creating a hazard system."""
        result = await create_hazard_system_tool({})

        assert result["success"] is True
        assert "system_id" in result
        assert result["system_id"] in state.hazard_systems

    @pytest.mark.asyncio
    async def test_run_simulation_missing_systems(self, clean_state):
        """Test simulation with missing systems."""
        result = await run_simulation_tool(
            {"asset_system_id": "nonexistent", "hazard_system_id": "nonexistent"}
        )

        assert "error" in result
        assert "not found" in result["error"].lower()


class TestAssetQueryTools:
    """Test asset query tools."""

    @pytest.mark.asyncio
    async def test_query_assets_missing_system(self, clean_state):
        """Test querying with missing system."""
        result = await query_assets_tool({"asset_system_id": "nonexistent"})

        assert "error" in result
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_get_asset_statistics_missing_system(self, clean_state):
        """Test statistics with missing system."""
        result = await get_asset_statistics_tool({"asset_system_id": "nonexistent"})

        assert "error" in result


class TestUtilityTools:
    """Test utility tools."""

    @pytest.mark.asyncio
    async def test_list_asset_types(self):
        """Test listing asset types."""
        result = await list_asset_types_tool({})

        assert result["success"] is True
        assert "asset_types" in result
        assert len(result["asset_types"]) > 0
        assert "distribution_poles" in result["asset_types"]

    @pytest.mark.asyncio
    async def test_list_loaded_systems_empty(self, clean_state):
        """Test listing systems when empty."""
        result = await list_loaded_systems_tool({})

        assert result["success"] is True
        assert len(result["asset_systems"]) == 0
        assert len(result["hazard_systems"]) == 0
        assert len(result["simulations"]) == 0

    @pytest.mark.asyncio
    async def test_get_cache_info(self):
        """Test getting cache information."""
        result = await get_cache_info_tool({})

        assert result["success"] is True
        assert "distribution_cache" in result
        assert "hazard_cache" in result
        assert "directory" in result["distribution_cache"]

    @pytest.mark.asyncio
    async def test_list_fragility_curves(self):
        """Test listing fragility curves."""
        result = await list_fragility_curves_tool({})

        assert result["success"] is True
        assert "curve_sets" in result
        assert "DEFAULT_CURVES" in result["curve_sets"]
        assert "hazard_types" in result


class TestFragilityCurveTools:
    """Test fragility curve tools."""

    @pytest.mark.asyncio
    async def test_list_curves(self):
        """Test listing available curves."""
        result = await list_fragility_curves_tool({})

        assert result["success"] is True
        assert len(result["hazard_types"]) > 0


class TestStatefulBehavior:
    """Test stateful server behavior."""

    @pytest.mark.asyncio
    async def test_create_and_list_hazard_system(self, clean_state):
        """Test creating system and then listing it."""
        # Create system
        create_result = await create_hazard_system_tool({})
        assert create_result["success"] is True
        system_id = create_result["system_id"]

        # List systems
        list_result = await list_loaded_systems_tool({})
        assert list_result["success"] is True
        assert system_id in list_result["hazard_systems"]


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_invalid_system_id(self, clean_state):
        """Test handling of invalid system IDs."""
        result = await query_assets_tool({"asset_system_id": "invalid-id-12345"})

        assert "error" in result
        assert "not found" in result["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
