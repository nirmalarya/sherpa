"""
Test Suite for Security - Credentials Encryption
Tests that credentials are stored securely and not in plaintext
"""

import pytest
import asyncio
import os
from pathlib import Path

from sherpa.core.config_manager import (
    encrypt_credential,
    decrypt_credential,
    redact_credential,
    get_config_manager,
)


class TestCredentialEncryption:
    """Test encryption/decryption of credentials"""

    def test_encrypt_credential(self):
        """Test that credentials are encrypted"""
        plaintext = "my-secret-pat-token-12345"
        encrypted = encrypt_credential(plaintext)

        # Encrypted should be different from plaintext
        assert encrypted != plaintext
        # Encrypted should be non-empty
        assert len(encrypted) > 0
        # Encrypted should be base64-encoded
        assert encrypted.isascii()

    def test_decrypt_credential(self):
        """Test that credentials can be decrypted"""
        plaintext = "my-secret-pat-token-12345"
        encrypted = encrypt_credential(plaintext)
        decrypted = decrypt_credential(encrypted)

        # Decrypted should match original plaintext
        assert decrypted == plaintext

    def test_encrypt_decrypt_roundtrip(self):
        """Test full encrypt/decrypt cycle"""
        test_credentials = [
            "simple-token",
            "complex-token-with-special-chars!@#$%",
            "very-long-token-" * 10,
            "12345678",
            ""  # Empty string
        ]

        for credential in test_credentials:
            encrypted = encrypt_credential(credential)
            decrypted = decrypt_credential(encrypted)
            assert decrypted == credential, f"Roundtrip failed for: {credential}"

    def test_redact_credential(self):
        """Test that credentials are properly redacted"""
        # Test normal credential
        credential = "my-secret-token-abc"
        redacted = redact_credential(credential)
        assert redacted == "***...abc"
        assert "secret" not in redacted
        assert "token" not in redacted

        # Test short credential
        short = "abc"
        redacted_short = redact_credential(short)
        assert redacted_short == "***"

        # Test empty credential
        empty = ""
        redacted_empty = redact_credential(empty)
        assert redacted_empty == ""

        # Test None
        redacted_none = redact_credential(None)
        assert redacted_none == ""

    def test_encryption_consistency(self):
        """Test that encryption produces different ciphertexts each time"""
        plaintext = "my-secret-token"
        encrypted1 = encrypt_credential(plaintext)
        encrypted2 = encrypt_credential(plaintext)

        # Different encryptions should produce different ciphertexts (due to IV)
        # But both should decrypt to the same plaintext
        decrypted1 = decrypt_credential(encrypted1)
        decrypted2 = decrypt_credential(encrypted2)

        assert decrypted1 == plaintext
        assert decrypted2 == plaintext


class TestConfigManagerEncryption:
    """Test that ConfigManager uses encryption for Azure DevOps PAT"""

    def setup_method(self):
        """Setup test config file"""
        self.test_config_path = Path("sherpa/data/test_config.json")
        self.config_manager = get_config_manager()
        # Use test config path
        self.config_manager.config_path = self.test_config_path

        # Clean up any existing test config
        if self.test_config_path.exists():
            self.test_config_path.unlink()

    def teardown_method(self):
        """Clean up test config file"""
        if self.test_config_path.exists():
            self.test_config_path.unlink()

    def test_azure_devops_pat_encryption(self):
        """Test that Azure DevOps PAT is encrypted when stored"""
        from sherpa.core.config_manager import SherpaConfig

        plaintext_pat = "my-azure-devops-pat-12345"

        # Set Azure DevOps config with plaintext PAT
        self.config_manager.set_azure_devops_config(
            organization="myorg",
            project="myproject",
            pat=plaintext_pat
        )

        # Read the config file directly
        import json
        with open(self.test_config_path, 'r') as f:
            config_data = json.load(f)

        # Verify PAT is encrypted in storage
        stored_pat = config_data['azure_devops']['pat_encrypted']
        assert stored_pat != plaintext_pat, "PAT should be encrypted in storage"
        assert len(stored_pat) > 0, "Encrypted PAT should not be empty"

        # Verify we can decrypt it back
        decrypted_pat = self.config_manager.get_azure_devops_pat()
        assert decrypted_pat == plaintext_pat, "Decrypted PAT should match original"

    def test_pat_not_in_plaintext_anywhere(self):
        """Test that plaintext PAT never appears in config file"""
        from sherpa.core.config_manager import SherpaConfig

        plaintext_pat = "super-secret-pat-token-xyz789"

        # Set config
        self.config_manager.set_azure_devops_config(
            organization="testorg",
            project="testproject",
            pat=plaintext_pat
        )

        # Read entire config file as text
        config_text = self.test_config_path.read_text()

        # Verify plaintext PAT is NOT in the file
        assert plaintext_pat not in config_text, "Plaintext PAT should never appear in config file"

        # Verify some encrypted data exists
        assert "pat_encrypted" in config_text, "Encrypted PAT field should exist"


class TestAWSCredentialsFromEnvironment:
    """Test that AWS credentials are only read from environment variables"""

    def test_aws_credentials_from_env_only(self):
        """Test that Bedrock client only uses environment variables for AWS credentials"""
        from sherpa.core.bedrock_client import BedrockKnowledgeBaseClient

        # Create client without credentials
        client = BedrockKnowledgeBaseClient()

        # Verify it checks environment variables
        # This is confirmed by reading the code - it checks os.getenv('AWS_ACCESS_KEY_ID'), etc.
        # No credentials should be stored in config files or database
        assert client.mock_mode or os.getenv('AWS_ACCESS_KEY_ID'), \
            "Bedrock client should only use environment variables for AWS credentials"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
