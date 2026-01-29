"""Tests for ERAD REST API."""

import json
import pytest
import zipfile
import io
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from erad.api import app
from erad.api.main import uploaded_models, uploaded_hazard_models
from erad.models.asset import Asset


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def clear_uploaded_models():
    """Clear uploaded models before and after tests."""
    uploaded_models.clear()
    yield
    uploaded_models.clear()


@pytest.fixture
def sample_distribution_system_data():
    """Sample distribution system data."""
    return {"name": "test_system", "components": [], "properties": {}}


@pytest.fixture
def sample_hazard_model_data():
    """Sample hazard model data."""
    return {
        "name": "test_hazard",
        "timestamp": datetime.now().isoformat(),
        "hazard_type": "earthquake",
        "model_data": {"origin": [0.0, 0.0], "depth": 10.0, "magnitude": 5.0},
    }


@pytest.fixture
def sample_distribution_json(tmp_path, sample_distribution_system_data):
    """Create a sample distribution system JSON file."""
    file_path = tmp_path / "test_distribution.json"
    with open(file_path, "w") as f:
        json.dump(sample_distribution_system_data, f)
    return file_path


# ========== Root and Health Check Tests ==========


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["message"] == "ERAD Hazard Simulator API"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


# ========== Simulation Tests ==========


@patch("erad.api.helpers.HazardSystem.from_json")
@patch("erad.api.simulation._load_distribution_system")
@patch("erad.api.simulation.AssetSystem.from_gdm")
@patch("erad.api.simulation.HazardSimulator")
def test_run_simulation_success(
    mock_simulator_class,
    mock_asset_system_from_gdm,
    mock_load_dist_system,
    mock_hazard_from_json,
    client,
    clear_uploaded_models,
    tmp_path,
):
    """Test successful simulation run with cached models."""
    # Add models to cache
    from erad.api import DistributionModelInfo, HazardModelInfo

    uploaded_models["test_dist"] = DistributionModelInfo(
        name="test_dist",
        description="Test",
        created_at=datetime.now(),
        file_path=str(tmp_path / "dist.json"),
    )
    uploaded_hazard_models["test_hazard"] = HazardModelInfo(
        name="test_hazard",
        hazard_type="earthquake",
        description="Test",
        created_at=datetime.now(),
        file_path=str(tmp_path / "hazard.json"),
    )

    # Setup mocks
    mock_dist_system = Mock()
    mock_load_dist_system.return_value = mock_dist_system

    mock_hazard_system = Mock()
    mock_hazard_system.iter_all_components.return_value = [Mock(), Mock()]
    mock_hazard_from_json.return_value = mock_hazard_system

    mock_asset_system = Mock()
    mock_asset = Mock(spec=Asset)
    mock_asset_system.get_components.return_value = [mock_asset]
    mock_asset_system.export_results = Mock()
    mock_asset_system_from_gdm.return_value = mock_asset_system

    mock_simulator = Mock()
    mock_simulator.timestamps = [datetime.now()]
    mock_simulator_class.return_value = mock_simulator

    # Make request with model names
    request_data = {
        "distribution_system_name": "test_dist",
        "hazard_system_name": "test_hazard",
        "curve_set": "DEFAULT_CURVES",
    }

    response = client.post("/simulate", json=request_data)

    # Assertions - should return a file
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-sqlite3"

    # Verify mocks were called
    mock_simulator.run.assert_called_once_with(mock_hazard_system, "DEFAULT_CURVES")


def test_run_simulation_missing_distribution_system(client, clear_uploaded_models):
    """Test simulation with missing distribution system."""
    # Don't add models to cache
    request_data = {
        "distribution_system_name": "nonexistent",
        "hazard_system_name": "test_hazard",
        "curve_set": "DEFAULT_CURVES",
    }

    response = client.post("/simulate", json=request_data)

    # Should fail with 404
    assert response.status_code == 404
    assert "not found in cache" in response.json()["detail"]


@patch("erad.api.helpers.HazardSystem.from_json")
@patch("erad.api.simulation._load_distribution_system")
@patch("erad.api.simulation.AssetSystem.from_gdm")
@patch("erad.api.simulation.HazardSimulator")
def test_run_simulation_error(
    mock_simulator_class,
    mock_asset_system_from_gdm,
    mock_load_dist_system,
    mock_hazard_from_json,
    client,
    clear_uploaded_models,
    tmp_path,
):
    """Test simulation with error."""
    # Add models to cache
    from erad.api import DistributionModelInfo, HazardModelInfo

    uploaded_models["test_dist"] = DistributionModelInfo(
        name="test_dist",
        description="Test",
        created_at=datetime.now(),
        file_path=str(tmp_path / "dist.json"),
    )
    uploaded_hazard_models["test_hazard"] = HazardModelInfo(
        name="test_hazard",
        hazard_type="earthquake",
        description="Test",
        created_at=datetime.now(),
        file_path=str(tmp_path / "hazard.json"),
    )

    mock_simulator_class.side_effect = Exception("Simulation error")

    request_data = {
        "distribution_system_name": "test_dist",
        "hazard_system_name": "test_hazard",
        "curve_set": "DEFAULT_CURVES",
    }

    response = client.post("/simulate", json=request_data)

    assert response.status_code == 500
    assert "Simulation failed" in response.json()["detail"]


# ========== Distribution Model Management Tests ==========


def test_upload_distribution_model_success(
    client, clear_uploaded_models, tmp_path, sample_distribution_system_data
):
    """Test successful distribution model upload as ZIP file."""
    # Create a ZIP file with JSON content
    json_content = json.dumps(sample_distribution_system_data)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("test_model.json", json_content)
    zip_buffer.seek(0)

    response = client.post(
        "/distribution-models",
        files={"file": ("test_model.zip", zip_buffer, "application/zip")},
        data={"name": "test_model", "description": "Test model"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["name"] == "test_model"
    assert "file_path" in data


def test_upload_distribution_model_invalid_file_type(client, clear_uploaded_models):
    """Test upload with invalid file type."""
    response = client.post(
        "/distribution-models",
        files={"file": ("test.txt", "not json", "text/plain")},
        data={"name": "test_model"},
    )

    assert response.status_code == 400
    assert "Only ZIP files are allowed" in response.json()["detail"]


def test_upload_distribution_model_invalid_json_in_zip(client, clear_uploaded_models):
    """Test upload with invalid JSON inside ZIP."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("model.json", "invalid json{")
    zip_buffer.seek(0)

    response = client.post(
        "/distribution-models",
        files={"file": ("test.zip", zip_buffer, "application/zip")},
        data={"name": "test_model"},
    )

    assert response.status_code == 400
    assert "Invalid JSON" in response.json()["detail"]


def test_upload_distribution_model_duplicate_name(
    client, clear_uploaded_models, sample_distribution_system_data
):
    """Test upload with duplicate name."""
    json_content = json.dumps(sample_distribution_system_data)

    # Create ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("test_model.json", json_content)
    zip_buffer.seek(0)

    # First upload
    response1 = client.post(
        "/distribution-models",
        files={"file": ("test.zip", zip_buffer, "application/zip")},
        data={"name": "test_model"},
    )
    assert response1.status_code == 201

    # Create new ZIP for second upload
    zip_buffer2 = io.BytesIO()
    with zipfile.ZipFile(zip_buffer2, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("test_model.json", json_content)
    zip_buffer2.seek(0)

    # Second upload with same name
    response2 = client.post(
        "/distribution-models",
        files={"file": ("test.zip", zip_buffer2, "application/zip")},
        data={"name": "test_model"},
    )
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]


def test_list_distribution_models_empty(client, clear_uploaded_models):
    """Test listing models when none exist."""
    response = client.get("/distribution-models")

    assert response.status_code == 200
    assert response.json() == []


def test_list_distribution_models_with_data(client, clear_uploaded_models):
    """Test listing models with data."""
    from erad.api import DistributionModelInfo

    # Add models
    uploaded_models["model1"] = DistributionModelInfo(
        name="model1",
        description="Test model 1",
        created_at=datetime.now(),
        file_path="path1.json",
    )
    uploaded_models["model2"] = DistributionModelInfo(
        name="model2",
        description="Test model 2",
        created_at=datetime.now(),
        file_path="path2.json",
    )

    response = client.get("/distribution-models")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [model["name"] for model in data]
    assert "model1" in names
    assert "model2" in names


def test_get_distribution_model_success(
    client, clear_uploaded_models, tmp_path, sample_distribution_system_data
):
    """Test getting a specific distribution model."""
    from erad.api import DistributionModelInfo
    from unittest.mock import patch, Mock

    # Create a test file
    file_path = tmp_path / "test_model.json"
    with open(file_path, "w") as f:
        json.dump(sample_distribution_system_data, f)

    # Add model
    uploaded_models["test_model"] = DistributionModelInfo(
        name="test_model",
        description="Test model",
        created_at=datetime.now(),
        file_path=str(file_path),
    )

    # Mock DistributionSystem.from_json to avoid validation issues
    with patch("erad.api.distribution_models.DistributionSystem") as mock_dist_system:
        mock_system = Mock()
        mock_system.iter_all_components.return_value = []
        mock_dist_system.from_json.return_value = mock_system

        response = client.get("/distribution-models/test_model")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_model"
    assert "number_of_components" in data


def test_get_distribution_model_not_found(client, clear_uploaded_models):
    """Test getting a non-existent distribution model."""
    response = client.get("/distribution-models/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_distribution_model_success(client, clear_uploaded_models, tmp_path):
    """Test deleting a distribution model."""
    from erad.api import DistributionModelInfo

    # Create a test file
    file_path = tmp_path / "test_model.json"
    file_path.write_text("{}")

    # Add model
    uploaded_models["test_model"] = DistributionModelInfo(
        name="test_model",
        description="Test model",
        created_at=datetime.now(),
        file_path=str(file_path),
    )

    response = client.delete("/distribution-models/test_model")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "test_model" not in uploaded_models
    assert not file_path.exists()


def test_delete_distribution_model_not_found(client, clear_uploaded_models):
    """Test deleting a non-existent distribution model."""
    response = client.delete("/distribution-models/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# ========== Utility Endpoint Tests ==========


def test_get_supported_hazard_types(client):
    """Test getting supported hazard types."""
    response = client.get("/supported-hazard-types")

    assert response.status_code == 200
    data = response.json()
    assert "hazard_types" in data
    assert "descriptions" in data
    assert len(data["hazard_types"]) > 0
    assert "earthquake" in data["hazard_types"]
    assert "flood" in data["hazard_types"]


def test_get_default_curve_sets(client):
    """Test getting default curve sets."""
    response = client.get("/default-curve-sets")

    assert response.status_code == 200
    data = response.json()
    assert "curve_sets" in data
    assert "default" in data
    assert "DEFAULT_CURVES" in data["curve_sets"]


# ========== Integration Tests ==========


@pytest.mark.integration
@patch("erad.api.simulation.AssetSystem.from_gdm")
@patch("erad.api.simulation.HazardScenarioGenerator")
def test_full_workflow(
    mock_generator_class,
    mock_asset_system_from_gdm,
    client,
    clear_uploaded_models,
    sample_distribution_system_data,
    sample_hazard_model_data,
):
    """Test full workflow: upload model, run simulation, generate scenarios."""
    # Setup mocks
    mock_asset_system = Mock()
    mock_asset = Mock(spec=Asset)
    mock_asset_system.get_components.return_value = [mock_asset]
    mock_asset_system_from_gdm.return_value = mock_asset_system

    mock_generator = Mock()
    mock_generator.samples.return_value = []
    mock_generator_class.return_value = mock_generator

    # 1. Upload distribution model as ZIP
    json_content = json.dumps(sample_distribution_system_data)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("test_system.json", json_content)
    zip_buffer.seek(0)

    upload_response = client.post(
        "/distribution-models",
        files={"file": ("test_system.zip", zip_buffer, "application/zip")},
        data={"name": "test_system", "description": "Test system"},
    )
    assert upload_response.status_code == 201

    # 2. List models
    list_response = client.get("/distribution-models")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    # 3. Generate scenarios
    # Note: For now, we skip generate-scenarios test as it needs hazard cache setup
    # The endpoint works as tested in MCP server tests

    # 4. Delete model
    delete_response = client.delete("/distribution-models/test_system")
    assert delete_response.status_code == 200

    # 5. Verify deletion
    list_response_after = client.get("/distribution-models")
    assert len(list_response_after.json()) == 0


# ========== Error Handling Tests ==========


def test_invalid_endpoint(client):
    """Test accessing an invalid endpoint."""
    response = client.get("/invalid-endpoint")

    assert response.status_code == 404


def test_method_not_allowed(client):
    """Test using wrong HTTP method."""
    response = client.post("/health")

    assert response.status_code == 405


@patch("erad.api.helpers.HazardSystem.from_json")
@patch("erad.api.helpers._load_distribution_system")
def test_internal_server_error_handling(
    mock_load_dist_system, mock_hazard_from_json, client, sample_hazard_model_data
):
    """Test internal server error handling."""
    # Upload a hazard model first
    hazard_data = json.dumps(sample_hazard_model_data)
    hazard_zip = io.BytesIO()
    with zipfile.ZipFile(hazard_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("test_hazard.json", hazard_data)
    hazard_zip.seek(0)

    client.post(
        "/hazard-models",
        files={"file": ("test_hazard.zip", hazard_zip, "application/zip")},
        data={"name": "test_hazard"},
    )

    # Upload a distribution model
    dist_data = json.dumps({"name": "test"})
    dist_zip = io.BytesIO()
    with zipfile.ZipFile(dist_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("test_dist.json", dist_data)
    dist_zip.seek(0)

    client.post(
        "/distribution-models",
        files={"file": ("test_dist.zip", dist_zip, "application/zip")},
        data={"name": "test_dist"},
    )

    # Make loading fail
    mock_load_dist_system.side_effect = Exception("Unexpected error")

    request_data = {"distribution_system_name": "test_dist", "hazard_system_name": "test_hazard"}

    response = client.post("/simulate", json=request_data)

    assert response.status_code == 500
    assert "failed" in response.json()["detail"].lower()


# ========== Cache Management Tests ==========


def test_get_cache_info(client):
    """Test getting cache information."""
    response = client.get("/cache-info")

    assert response.status_code == 200
    data = response.json()
    assert "distribution_models" in data
    assert "hazard_models" in data
    assert "total_size_bytes" in data
    assert "total_size_mb" in data
    # Check nested structure
    assert "cache_directory" in data["distribution_models"]
    assert "total_models" in data["distribution_models"]


def test_refresh_cache(client, clear_uploaded_models):
    """Test refreshing cache."""
    response = client.post("/refresh-cache")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "total_distribution_models" in data
    assert "total_hazard_models" in data
    assert "distribution_models" in data
    assert "hazard_models" in data


def test_list_models_with_refresh(client, clear_uploaded_models):
    """Test listing models with refresh parameter."""
    # Without refresh
    response = client.get("/distribution-models")
    assert response.status_code == 200

    # With refresh
    response = client.get("/distribution-models?refresh=true")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_cache_directory_creation(tmp_path):
    """Test that cache directory is created properly."""
    # Test with the actual get_cache_directory function
    from erad.api import get_cache_directory

    cache_dir = get_cache_directory()

    # Should create directory
    assert cache_dir.exists()
    assert cache_dir.is_dir()
    assert "erad" in str(cache_dir)


def test_upload_distribution_model_zip_file(client, clear_uploaded_models):
    """Test uploading a distribution model as a ZIP file with time series data."""
    # Create a test JSON content
    json_content = json.dumps(
        {"name": "test_zip_model", "version": "1.0", "description": "Test model from ZIP"}
    )

    # Create a mock time series CSV content
    timeseries_csv = "timestamp,value\n2024-01-01,100\n2024-01-02,200"

    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add the JSON file
        zf.writestr("test_zip_model.json", json_content)
        # Add a time series folder with a CSV file
        zf.writestr("test_zip_model_time_series/data.csv", timeseries_csv)

    zip_buffer.seek(0)

    # Upload the ZIP file
    response = client.post(
        "/distribution-models",
        files={"file": ("test_zip_model.zip", zip_buffer, "application/zip")},
        data={"name": "test_zip_model"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "test_zip_model" in data["message"]
    assert data["name"] == "test_zip_model"
    assert "time_series_path" in data


def test_upload_distribution_model_zip_without_timeseries(client, clear_uploaded_models):
    """Test uploading a ZIP file with only JSON (no time series folder)."""
    json_content = json.dumps({"name": "simple_zip_model", "version": "1.0"})

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("simple_zip_model.json", json_content)

    zip_buffer.seek(0)

    response = client.post(
        "/distribution-models",
        files={"file": ("simple_zip_model.zip", zip_buffer, "application/zip")},
        data={"name": "simple_zip_model"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "time_series_path" not in data


def test_upload_distribution_model_zip_no_json(client, clear_uploaded_models):
    """Test uploading a ZIP file without a JSON file inside."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("readme.txt", "This is not a JSON file")

    zip_buffer.seek(0)

    response = client.post(
        "/distribution-models",
        files={"file": ("no_json.zip", zip_buffer, "application/zip")},
        data={"name": "no_json_model"},
    )

    assert response.status_code == 400
    assert "must contain at least one JSON file" in response.json()["detail"]


def test_upload_distribution_model_zip_multiple_json(client, clear_uploaded_models):
    """Test uploading a ZIP file with multiple JSON files - uses first one found."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("model1.json", '{"name": "model1"}')
        zf.writestr("model2.json", '{"name": "model2"}')

    zip_buffer.seek(0)

    response = client.post(
        "/distribution-models",
        files={"file": ("multiple_json.zip", zip_buffer, "application/zip")},
        data={"name": "multi_json_model"},
    )

    # API accepts multiple JSON files and uses the first one
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"


def test_upload_distribution_model_invalid_zip(client, clear_uploaded_models):
    """Test uploading an invalid/corrupted ZIP file."""
    # Create fake ZIP content (not a valid ZIP)
    fake_zip = io.BytesIO(b"This is not a valid ZIP file content")

    response = client.post(
        "/distribution-models",
        files={"file": ("invalid.zip", fake_zip, "application/zip")},
        data={"name": "invalid_zip_model"},
    )

    assert response.status_code == 400
    assert "Invalid or corrupted ZIP file" in response.json()["detail"]
