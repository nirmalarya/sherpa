#!/usr/bin/env python3
"""
Test script for ConfigManager
Tests all configuration management functionality
"""

import json
import sys
from pathlib import Path

# Add sherpa to path
sys.path.insert(0, str(Path(__file__).parent))

from sherpa.core.config_manager import ConfigManager, SherpaConfig, BedrockConfig


def test_config_manager():
    """Test ConfigManager functionality"""

    print("=" * 60)
    print("Configuration Manager Test")
    print("=" * 60)
    print()

    # Use a test config path
    test_config_path = Path("sherpa/test_config.json")
    config_manager = ConfigManager(test_config_path)

    # Clean up any existing test config
    if test_config_path.exists():
        test_config_path.unlink()

    # Test 1: Check exists (should be False initially)
    print("Test 1: Check config file exists (should be False)")
    exists = config_manager.exists()
    print(f"  Result: {exists}")
    assert not exists, "Config should not exist initially"
    print("  ✓ PASS\n")

    # Test 2: Create config
    print("Test 2: Create configuration")
    config = SherpaConfig(
        organization="TestOrg",
        bedrock=BedrockConfig(
            knowledge_base_id="test-kb-123",
            region="us-east-1",
            enabled=True
        ),
        auto_continue_delay=5,
        max_iterations=50
    )
    config_manager.save(config)
    print(f"  Saved config to: {test_config_path}")
    print(f"  ✓ PASS\n")

    # Test 3: Verify file created
    print("Test 3: Verify config.json created")
    exists = config_manager.exists()
    print(f"  File exists: {exists}")
    assert exists, "Config file should exist after save"
    print("  ✓ PASS\n")

    # Test 4: Load config
    print("Test 4: Load configuration")
    loaded_config = config_manager.load()
    print(f"  Organization: {loaded_config.organization}")
    print(f"  Bedrock KB ID: {loaded_config.bedrock.knowledge_base_id}")
    print(f"  Bedrock Region: {loaded_config.bedrock.region}")
    print(f"  Auto-continue delay: {loaded_config.auto_continue_delay}")
    assert loaded_config.organization == "TestOrg", "Organization should match"
    assert loaded_config.bedrock.knowledge_base_id == "test-kb-123", "KB ID should match"
    print("  ✓ PASS\n")

    # Test 5: Update config
    print("Test 5: Update configuration")
    updated_config = config_manager.update({
        "organization": "UpdatedOrg",
        "bedrock": {"region": "us-west-2"},
        "auto_continue_delay": 10
    })
    print(f"  Updated organization: {updated_config.organization}")
    print(f"  Updated region: {updated_config.bedrock.region}")
    print(f"  Updated delay: {updated_config.auto_continue_delay}")
    assert updated_config.organization == "UpdatedOrg", "Organization should be updated"
    assert updated_config.bedrock.region == "us-west-2", "Region should be updated"
    assert updated_config.bedrock.knowledge_base_id == "test-kb-123", "KB ID should be preserved"
    print("  ✓ PASS\n")

    # Test 6: Verify changes persisted
    print("Test 6: Verify changes persisted to file")
    with open(test_config_path, 'r') as f:
        file_data = json.load(f)
    print(f"  File organization: {file_data['organization']}")
    print(f"  File bedrock region: {file_data['bedrock']['region']}")
    assert file_data['organization'] == "UpdatedOrg", "Changes should be persisted"
    print("  ✓ PASS\n")

    # Test 7: Validate config
    print("Test 7: Validate configuration")
    is_valid, error_msg = config_manager.validate()
    print(f"  Valid: {is_valid}")
    if error_msg:
        print(f"  Error: {error_msg}")
    assert is_valid, "Config should be valid"
    print("  ✓ PASS\n")

    # Test 8: Test validation failure
    print("Test 8: Test validation with invalid config")
    invalid_config = SherpaConfig(
        bedrock=BedrockConfig(
            knowledge_base_id="",  # Empty KB ID
            region="us-east-1",
            enabled=True
        )
    )
    config_manager.save(invalid_config)
    is_valid, error_msg = config_manager.validate()
    print(f"  Valid: {is_valid}")
    print(f"  Error: {error_msg}")
    assert not is_valid, "Config should be invalid with empty KB ID"
    print("  ✓ PASS\n")

    # Test 9: Helper methods
    print("Test 9: Test helper methods")
    config_manager.set_bedrock_config("new-kb-456", "eu-west-1", enabled=True)
    bedrock_config = config_manager.get_bedrock_config()
    print(f"  Bedrock KB ID: {bedrock_config.knowledge_base_id}")
    print(f"  Bedrock Region: {bedrock_config.region}")
    assert bedrock_config.knowledge_base_id == "new-kb-456", "KB ID should be updated"
    assert bedrock_config.region == "eu-west-1", "Region should be updated"
    print("  ✓ PASS\n")

    # Clean up
    print("Cleanup: Removing test config file")
    if test_config_path.exists():
        test_config_path.unlink()
    print("  ✓ Done\n")

    print("=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    print()

    return True


if __name__ == "__main__":
    try:
        test_config_manager()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
