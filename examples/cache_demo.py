#!/usr/bin/env python
"""
Demo script showcasing the new cache functionality for ERAD API.

This demonstrates:
1. Uploading a distribution model to the cache
2. Listing models from cache
3. Getting cache information
4. Refreshing cache from disk
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_cache_info():
    """Get cache information."""
    print_section("Cache Information")
    response = requests.get(f"{BASE_URL}/cache-info")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Cache Directory: {data['cache_directory']}")
        print(f"✓ Metadata File: {data['metadata_file']}")
        print(f"✓ Total Models: {data['total_models']}")
        print(f"✓ Total Files: {data['total_files']}")
        print(f"✓ Cache Size: {data['total_size_mb']} MB")
    else:
        print(f"✗ Failed to get cache info: {response.status_code}")


def demo_list_models():
    """List all cached models."""
    print_section("List Cached Models")
    response = requests.get(f"{BASE_URL}/distribution-models")
    if response.status_code == 200:
        models = response.json()
        print(f"✓ Found {len(models)} model(s) in cache:")
        for model in models:
            print(f"  - {model['name']}")
            print(f"    Created: {model['created_at']}")
            print(f"    Path: {model['file_path']}")
    else:
        print(f"✗ Failed to list models: {response.status_code}")


def demo_upload_model():
    """Upload a sample model to cache."""
    print_section("Upload Distribution Model to Cache")

    # Create sample distribution system
    sample_data = {
        "name": "demo_system",
        "components": [
            {
                "uuid": "asset_1",
                "type": "transformer",
                "properties": {"in_service": True, "latitude": 40.0, "longitude": -105.0},
            }
        ],
        "properties": {"voltage_level": "12.47kV"},
    }

    # Save to temp file
    temp_file = Path("/tmp/demo_system.json")  # noqa: B108
    with open(temp_file, "w") as f:
        json.dump(sample_data, f, indent=2)

    # Upload
    try:
        with open(temp_file, "rb") as f:
            files = {"file": ("demo_system.json", f, "application/json")}
            data = {"name": "demo_system", "description": "Demo system for cache functionality"}
            response = requests.post(f"{BASE_URL}/distribution-models", files=files, data=data)

        if response.status_code == 201:
            result = response.json()
            print(f"✓ Uploaded: {result['name']}")
            print(f"✓ Saved to: {result['file_path']}")
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"  {response.json()}")
    finally:
        temp_file.unlink(missing_ok=True)


def demo_refresh_cache():
    """Refresh cache from disk."""
    print_section("Refresh Cache from Disk")
    response = requests.post(f"{BASE_URL}/refresh-cache")
    if response.status_code == 200:
        data = response.json()
        print("✓ Cache refreshed successfully")
        print(f"✓ Total models: {data['total_models']}")
        print(f"✓ Models: {', '.join(data['models'])}")
    else:
        print(f"✗ Failed to refresh cache: {response.status_code}")


def demo_list_with_refresh():
    """List models with refresh parameter."""
    print_section("List Models with Auto-Refresh")
    response = requests.get(f"{BASE_URL}/distribution-models?refresh=true")
    if response.status_code == 200:
        models = response.json()
        print(f"✓ Listed {len(models)} model(s) after refresh")
        for model in models:
            print(f"  - {model['name']}: {Path(model['file_path']).name}")
    else:
        print(f"✗ Failed to list models: {response.status_code}")


def main():
    """Run the demo."""
    import sys

    print("\n" + "=" * 70)
    print("  ERAD API - Cache Functionality Demo")
    print("=" * 70)
    print("\nNOTE: Make sure the API server is running:")
    print("      python -m erad.api")

    # Only prompt for input if running interactively
    if sys.stdin.isatty():
        print("\nPress Enter to continue...")
        input()
    else:
        print("\nRunning in non-interactive mode...")

    try:
        # Check API is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("✗ API is not responding correctly")
            return
    except requests.exceptions.RequestException:
        print("✗ Cannot connect to API. Make sure it's running on http://localhost:8000")
        return

    print("✓ API is running\n")

    # Demo 1: Show current cache info
    demo_cache_info()

    # Demo 2: List existing models
    demo_list_models()

    # Demo 3: Upload a new model
    demo_upload_model()

    # Demo 4: List models again to see the new one
    demo_list_models()

    # Demo 5: Refresh cache
    demo_refresh_cache()

    # Demo 6: List with auto-refresh
    demo_list_with_refresh()

    # Final cache info
    demo_cache_info()

    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n✓ Models are persistently stored in the cache directory")
    print("✓ They will be available even after restarting the API")
    print("✓ Use /cache-info to see cache location and size")
    print("✓ Use /refresh-cache to scan for new files")
    print()


if __name__ == "__main__":
    main()
