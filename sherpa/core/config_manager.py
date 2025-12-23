"""
SHERPA V1 - Configuration Manager
Manages user configuration stored in ./sherpa/config.json

Handles:
- Creating and loading config.json
- Validating configuration values
- Updating configuration
- Persisting changes
- Encrypting/decrypting sensitive credentials
"""

import json
import os
import base64
from pathlib import Path
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field, validator
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend


# Encryption utilities
def _get_encryption_key() -> bytes:
    """
    Get or generate encryption key for credentials

    The key is derived from a machine-specific identifier (hostname + username)
    combined with an optional environment variable salt.

    Returns:
        bytes: Fernet encryption key
    """
    # Get salt from environment or use default
    salt = os.getenv("SHERPA_ENCRYPTION_SALT", "sherpa-v1-default-salt").encode()

    # Create password from machine-specific data
    import socket
    import getpass
    password = f"{socket.gethostname()}-{getpass.getuser()}-sherpa".encode()

    # Derive key using PBKDF2
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt_credential(plaintext: str) -> str:
    """
    Encrypt a credential (e.g., Azure DevOps PAT)

    Args:
        plaintext: The plaintext credential to encrypt

    Returns:
        str: Base64-encoded encrypted credential
    """
    if not plaintext:
        return ""

    key = _get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_credential(encrypted: str) -> str:
    """
    Decrypt a credential

    Args:
        encrypted: Base64-encoded encrypted credential

    Returns:
        str: Decrypted plaintext credential

    Raises:
        ValueError: If decryption fails
    """
    if not encrypted:
        return ""

    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt credential: {e}")


def redact_credential(credential: Optional[str]) -> str:
    """
    Redact a credential for logging/display

    Args:
        credential: The credential to redact

    Returns:
        str: Redacted credential (e.g., "***...abc")
    """
    if not credential:
        return ""

    if len(credential) <= 6:
        return "***"

    # Show last 3 characters for verification
    return f"***...{credential[-3:]}"


class BedrockConfig(BaseModel):
    """Bedrock Knowledge Base configuration"""
    knowledge_base_id: str = Field(..., description="AWS Bedrock Knowledge Base ID")
    region: str = Field(default="us-east-1", description="AWS region")
    enabled: bool = Field(default=True, description="Whether Bedrock is enabled")

    @validator('region')
    def validate_region(cls, v):
        """Validate AWS region format"""
        valid_regions = [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-central-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1'
        ]
        if v not in valid_regions:
            raise ValueError(f"Invalid AWS region. Must be one of: {', '.join(valid_regions)}")
        return v


class AzureDevOpsConfig(BaseModel):
    """Azure DevOps configuration"""
    organization: Optional[str] = Field(None, description="Azure DevOps organization")
    project: Optional[str] = Field(None, description="Azure DevOps project")
    pat_encrypted: Optional[str] = Field(None, description="Encrypted Personal Access Token")


class S3Config(BaseModel):
    """S3 bucket configuration for organizational snippets"""
    bucket_name: Optional[str] = Field(None, description="S3 bucket name")
    prefix: Optional[str] = Field(None, description="S3 key prefix")
    enabled: bool = Field(default=False, description="Whether S3 is enabled")


class SherpaConfig(BaseModel):
    """Complete SHERPA configuration"""
    organization: Optional[str] = Field(None, description="Organization name")
    bedrock: Optional[BedrockConfig] = Field(None, description="Bedrock configuration")
    azure_devops: Optional[AzureDevOpsConfig] = Field(None, description="Azure DevOps configuration")
    s3: Optional[S3Config] = Field(None, description="S3 configuration")
    auto_continue_delay: int = Field(default=3, description="Delay in seconds between autonomous iterations")
    max_iterations: int = Field(default=100, description="Maximum iterations for autonomous harness")

    @validator('auto_continue_delay')
    def validate_delay(cls, v):
        """Validate auto-continue delay"""
        if v < 0 or v > 60:
            raise ValueError("auto_continue_delay must be between 0 and 60 seconds")
        return v

    @validator('max_iterations')
    def validate_iterations(cls, v):
        """Validate max iterations"""
        if v < 1 or v > 1000:
            raise ValueError("max_iterations must be between 1 and 1000")
        return v


class ConfigManager:
    """
    Manages SHERPA configuration file

    The configuration file is stored at ./sherpa/config.json and contains
    settings for Bedrock KB, Azure DevOps, S3, and other system settings.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ConfigManager

        Args:
            config_path: Optional path to config file. Defaults to ./sherpa/config.json
        """
        if config_path is None:
            # Default to ./sherpa/config.json
            self.config_path = Path("sherpa") / "config.json"
        else:
            self.config_path = Path(config_path)

        self._config: Optional[SherpaConfig] = None

    def load(self) -> SherpaConfig:
        """
        Load configuration from file

        Returns:
            SherpaConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)

            # Validate and parse configuration
            self._config = SherpaConfig(**config_data)
            return self._config

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading config: {e}")

    def save(self, config: SherpaConfig) -> None:
        """
        Save configuration to file

        Args:
            config: SherpaConfig instance to save
        """
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict and save
        config_dict = config.dict(exclude_none=True)

        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

        self._config = config

    def get(self) -> SherpaConfig:
        """
        Get current configuration (load if not already loaded)

        Returns:
            SherpaConfig instance
        """
        if self._config is None:
            self._config = self.load()
        return self._config

    def update(self, updates: Dict[str, Any]) -> SherpaConfig:
        """
        Update configuration values

        Args:
            updates: Dictionary of configuration updates

        Returns:
            Updated SherpaConfig instance

        Example:
            config_manager.update({
                "organization": "MyOrg",
                "bedrock": {"region": "us-west-2"}
            })
        """
        # Load current config
        current = self.get()
        current_dict = current.dict()

        # Merge updates
        for key, value in updates.items():
            if key in current_dict and isinstance(current_dict[key], dict) and isinstance(value, dict):
                # Merge nested dicts
                current_dict[key] = {**current_dict[key], **value}
            else:
                current_dict[key] = value

        # Validate and save
        updated_config = SherpaConfig(**current_dict)
        self.save(updated_config)

        return updated_config

    def exists(self) -> bool:
        """
        Check if configuration file exists

        Returns:
            True if config file exists, False otherwise
        """
        return self.config_path.exists()

    def delete(self) -> None:
        """Delete configuration file"""
        if self.config_path.exists():
            self.config_path.unlink()
        self._config = None

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            config = self.get()

            # Validate Bedrock config if enabled
            if config.bedrock and config.bedrock.enabled:
                if not config.bedrock.knowledge_base_id:
                    return False, "Bedrock is enabled but knowledge_base_id is missing"
                if not config.bedrock.region:
                    return False, "Bedrock is enabled but region is missing"

            # Validate S3 config if enabled
            if config.s3 and config.s3.enabled:
                if not config.s3.bucket_name:
                    return False, "S3 is enabled but bucket_name is missing"

            return True, None

        except Exception as e:
            return False, str(e)

    def get_bedrock_config(self) -> Optional[BedrockConfig]:
        """
        Get Bedrock configuration

        Returns:
            BedrockConfig instance or None if not configured
        """
        config = self.get()
        return config.bedrock

    def get_azure_devops_config(self) -> Optional[AzureDevOpsConfig]:
        """
        Get Azure DevOps configuration

        Returns:
            AzureDevOpsConfig instance or None if not configured
        """
        config = self.get()
        return config.azure_devops

    def get_s3_config(self) -> Optional[S3Config]:
        """
        Get S3 configuration

        Returns:
            S3Config instance or None if not configured
        """
        config = self.get()
        return config.s3

    def set_bedrock_config(self, kb_id: str, region: str, enabled: bool = True) -> None:
        """
        Set Bedrock configuration

        Args:
            kb_id: Knowledge Base ID
            region: AWS region
            enabled: Whether Bedrock is enabled
        """
        self.update({
            "bedrock": {
                "knowledge_base_id": kb_id,
                "region": region,
                "enabled": enabled
            }
        })

    def set_azure_devops_config(self, organization: str, project: str, pat: Optional[str] = None) -> None:
        """
        Set Azure DevOps configuration

        Args:
            organization: Azure DevOps organization
            project: Azure DevOps project
            pat: Personal Access Token (will be encrypted before storage)
        """
        config_dict = {
            "organization": organization,
            "project": project
        }
        if pat:
            # Encrypt the PAT before storing
            config_dict["pat_encrypted"] = encrypt_credential(pat)

        self.update({"azure_devops": config_dict})

    def get_azure_devops_pat(self) -> Optional[str]:
        """
        Get decrypted Azure DevOps PAT

        Returns:
            Decrypted PAT or None if not configured
        """
        config = self.get_azure_devops_config()
        if config and config.pat_encrypted:
            return decrypt_credential(config.pat_encrypted)
        return None

    def set_s3_config(self, bucket_name: str, prefix: Optional[str] = None, enabled: bool = True) -> None:
        """
        Set S3 configuration

        Args:
            bucket_name: S3 bucket name
            prefix: S3 key prefix
            enabled: Whether S3 is enabled
        """
        config_dict = {
            "bucket_name": bucket_name,
            "enabled": enabled
        }
        if prefix:
            config_dict["prefix"] = prefix

        self.update({"s3": config_dict})


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    Get global ConfigManager instance

    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
