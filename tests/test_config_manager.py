"""
Unit tests for the ConfigManager module
"""
import pytest
import os
import json
from sherpa.core.config_manager import ConfigManager


@pytest.mark.unit
class TestConfigManager:
    """Test cases for ConfigManager"""

    def test_create_config_manager(self, temp_config_dir):
        """Test creating a ConfigManager instance"""
        config_path = os.path.join(temp_config_dir, 'config.json')
        config = ConfigManager(config_path=config_path)

        assert config is not None
        assert config.config_path == config_path

    def test_set_and_get_config(self, mock_config):
        """Test setting and getting configuration values"""
        mock_config.set('test_key', 'test_value')
        value = mock_config.get('test_key')

        assert value == 'test_value'

    def test_get_nonexistent_key(self, mock_config):
        """Test getting a key that doesn't exist"""
        value = mock_config.get('nonexistent_key')
        assert value is None

    def test_get_with_default(self, mock_config):
        """Test getting a key with default value"""
        value = mock_config.get('nonexistent_key', default='default_value')
        assert value == 'default_value'

    def test_update_existing_key(self, mock_config):
        """Test updating an existing configuration key"""
        mock_config.set('update_test', 'original_value')
        assert mock_config.get('update_test') == 'original_value'

        mock_config.set('update_test', 'new_value')
        assert mock_config.get('update_test') == 'new_value'

    def test_config_persists(self, temp_config_dir):
        """Test that configuration persists to file"""
        config_path = os.path.join(temp_config_dir, 'config.json')

        # Create and set config
        config1 = ConfigManager(config_path=config_path)
        config1.set('persist_test', 'persistent_value')

        # Create new instance and verify value persists
        config2 = ConfigManager(config_path=config_path)
        value = config2.get('persist_test')

        assert value == 'persistent_value'

    def test_config_file_format(self, temp_config_dir):
        """Test that config file is valid JSON"""
        config_path = os.path.join(temp_config_dir, 'config.json')
        config = ConfigManager(config_path=config_path)
        config.set('json_test', {'nested': 'value'})

        # Read file directly and verify it's valid JSON
        with open(config_path, 'r') as f:
            data = json.load(f)

        assert 'json_test' in data
        assert data['json_test'] == {'nested': 'value'}

    def test_set_complex_values(self, mock_config):
        """Test setting complex data types"""
        # Dictionary
        mock_config.set('dict_value', {'key1': 'val1', 'key2': 'val2'})
        assert mock_config.get('dict_value') == {'key1': 'val1', 'key2': 'val2'}

        # List
        mock_config.set('list_value', [1, 2, 3, 4])
        assert mock_config.get('list_value') == [1, 2, 3, 4]

        # Nested structure
        mock_config.set('nested', {
            'level1': {
                'level2': ['item1', 'item2']
            }
        })
        assert mock_config.get('nested')['level1']['level2'] == ['item1', 'item2']

    def test_get_all_config(self, mock_config):
        """Test getting all configuration values"""
        mock_config.set('key1', 'value1')
        mock_config.set('key2', 'value2')

        all_config = mock_config.get_all()

        assert 'key1' in all_config
        assert 'key2' in all_config
        assert all_config['key1'] == 'value1'
        assert all_config['key2'] == 'value2'

    def test_delete_config_key(self, mock_config):
        """Test deleting a configuration key"""
        mock_config.set('delete_test', 'value')
        assert mock_config.get('delete_test') == 'value'

        mock_config.delete('delete_test')
        assert mock_config.get('delete_test') is None

    def test_has_key(self, mock_config):
        """Test checking if a key exists"""
        mock_config.set('exists_test', 'value')

        assert mock_config.has('exists_test') is True
        assert mock_config.has('nonexistent') is False

    def test_validate_config(self, mock_config):
        """Test configuration validation"""
        # Set required keys
        mock_config.set('bedrock_kb_id', 'kb-123')
        mock_config.set('aws_region', 'us-east-1')

        is_valid = mock_config.validate()
        assert is_valid is True

    def test_default_values(self, temp_config_dir):
        """Test that default values are set on initialization"""
        config_path = os.path.join(temp_config_dir, 'new_config.json')
        config = ConfigManager(config_path=config_path)

        # Check if default values exist
        assert config.get('version') is not None or config.get('created_at') is not None
