"""
Example script demonstrating the ERAD REST API usage.

This script shows how to:
1. Upload a distribution system model
2. Run a simulation
3. Generate scenarios
4. Retrieve and manage models
"""

import requests
import json
from datetime import datetime
from pathlib import Path


# Configuration
BASE_URL = "http://localhost:8000"


def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print("✓ API is healthy")
        print(f"  Response: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ API is not reachable: {e}")
        print("  Make sure to start the API server with: python -m erad.api")
        return False


def get_supported_hazard_types():
    """Get list of supported hazard types."""
    response = requests.get(f"{BASE_URL}/supported-hazard-types")
    response.raise_for_status()
    data = response.json()
    print("\n✓ Supported hazard types:")
    for hazard_type in data["hazard_types"]:
        description = data["descriptions"][hazard_type]
        print(f"  - {hazard_type}: {description}")
    return data["hazard_types"]


def create_sample_distribution_system():
    """Create a sample distribution system for testing."""
    return {
        "name": "sample_system",
        "components": [
            {
                "uuid": "asset_1",
                "type": "transformer",
                "properties": {"in_service": True, "latitude": 40.0, "longitude": -105.0},
            },
            {
                "uuid": "asset_2",
                "type": "line",
                "properties": {"in_service": True, "latitude": 40.1, "longitude": -105.1},
            },
        ],
        "properties": {"voltage_level": "12.47kV", "region": "test_region"},
    }


def upload_distribution_system(name, system_data, description=None):
    """Upload a distribution system model."""
    # Save to temporary file
    temp_file = Path(f"/tmp/{name}.json")  # noqa: B108
    with open(temp_file, "w") as f:
        json.dump(system_data, f, indent=2)

    # Upload
    with open(temp_file, "rb") as f:
        files = {"file": (f"{name}.json", f, "application/json")}
        data = {"name": name}
        if description:
            data["description"] = description

        response = requests.post(f"{BASE_URL}/distribution-models", files=files, data=data)
        response.raise_for_status()
        result = response.json()
        print(f"\n✓ Uploaded distribution system '{name}'")
        print(f"  File path: {result['file_path']}")
        return result


def list_distribution_models():
    """List all uploaded distribution models."""
    response = requests.get(f"{BASE_URL}/distribution-models")
    response.raise_for_status()
    models = response.json()
    print(f"\n✓ Found {len(models)} distribution model(s):")
    for model in models:
        print(f"  - {model['name']}: {model.get('description', 'No description')}")
    return models


def run_simulation(distribution_system_name, hazard_models):
    """Run a hazard simulation."""
    request_data = {
        "distribution_system_name": distribution_system_name,
        "hazard_models": hazard_models,
        "curve_set": "DEFAULT_CURVES",
    }

    response = requests.post(f"{BASE_URL}/simulate", json=request_data)
    response.raise_for_status()
    result = response.json()

    print("\n✓ Simulation completed")
    print(f"  Status: {result['status']}")
    print(f"  Assets: {result['asset_count']}")
    print(f"  Hazards: {result['hazard_count']}")
    print(f"  Timestamps: {len(result['timestamps'])}")

    return result


def generate_scenarios(distribution_system_name, hazard_models, num_samples=10, seed=42):
    """Generate hazard scenarios."""
    request_data = {
        "distribution_system_name": distribution_system_name,
        "hazard_models": hazard_models,
        "number_of_samples": num_samples,
        "seed": seed,
        "curve_set": "DEFAULT_CURVES",
    }

    response = requests.post(f"{BASE_URL}/generate-scenarios", json=request_data)
    response.raise_for_status()
    result = response.json()

    print(f"\n✓ Generated {result['number_of_scenarios']} scenario(s)")
    print(f"  Status: {result['status']}")

    # Show first few scenarios
    if result["scenarios"]:
        print("\n  Sample scenarios:")
        for i, scenario in enumerate(result["scenarios"][:3]):
            print(f"    Scenario {i+1}: {scenario['scenario_name']}")
            print(f"      Timestamp: {scenario['timestamp']}")
            print(f"      Edits: {len(scenario['edits'])} asset(s) affected")
            if scenario["edits"]:
                for edit in scenario["edits"][:2]:
                    print(f"        - {edit['component_uuid']}: {edit['name']} = {edit['value']}")

    return result


def delete_distribution_model(name):
    """Delete a distribution model."""
    response = requests.delete(f"{BASE_URL}/distribution-models/{name}")
    response.raise_for_status()
    result = response.json()
    print(f"\n✓ Deleted distribution system '{name}'")
    return result


def main():
    """Main execution flow."""
    print("=" * 60)
    print("ERAD REST API - Example Usage")
    print("=" * 60)

    # Check API health
    if not check_api_health():
        return

    # Get supported hazard types
    get_supported_hazard_types()

    # Create sample data
    print("\n" + "-" * 60)
    print("Step 1: Creating sample distribution system")
    print("-" * 60)
    system_data = create_sample_distribution_system()
    system_name = "example_system"

    # Upload distribution system
    print("\n" + "-" * 60)
    print("Step 2: Uploading distribution system")
    print("-" * 60)
    upload_distribution_system(
        system_name, system_data, description="Example system for API demonstration"
    )

    # List models
    print("\n" + "-" * 60)
    print("Step 3: Listing distribution models")
    print("-" * 60)
    list_distribution_models()

    # Create hazard models
    print("\n" + "-" * 60)
    print("Step 4: Creating hazard models")
    print("-" * 60)
    hazard_models = [
        {
            "name": "earthquake_scenario",
            "timestamp": datetime.now().isoformat(),
            "hazard_type": "earthquake_pga",
            "model_data": {
                "data": {
                    "asset_1": 0.5,  # 0.5g PGA
                    "asset_2": 0.3,  # 0.3g PGA
                }
            },
        }
    ]
    print(f"  Created {len(hazard_models)} hazard model(s)")

    # Run simulation
    print("\n" + "-" * 60)
    print("Step 5: Running simulation")
    print("-" * 60)
    try:
        run_simulation(system_name, hazard_models)
    except requests.exceptions.HTTPError as e:
        print("  Note: Simulation may fail if assets don't match hazard data")
        print(f"  Error: {e.response.json()}")

    # Generate scenarios
    print("\n" + "-" * 60)
    print("Step 6: Generating scenarios")
    print("-" * 60)
    try:
        generate_scenarios(system_name, hazard_models, num_samples=5, seed=42)
    except requests.exceptions.HTTPError as e:
        print("  Note: Scenario generation may fail if assets don't match hazard data")
        print(f"  Error: {e.response.json()}")

    # Cleanup
    print("\n" + "-" * 60)
    print("Step 7: Cleanup")
    print("-" * 60)
    delete_distribution_model(system_name)

    # Verify cleanup
    list_distribution_models()

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
