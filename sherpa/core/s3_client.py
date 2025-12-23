"""
S3 Client for SHERPA V1

This module handles fetching organizational snippets from S3 buckets.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import os

from sherpa.core.logging_config import get_logger

logger = get_logger("sherpa.s3_client")

# Try to import boto3, but make it optional
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not installed - S3 snippet fetching will not be available")

    # Create dummy exceptions for type hints
    class ClientError(Exception):
        pass

    class NoCredentialsError(Exception):
        pass


class S3Client:
    """
    S3 client for fetching organizational code snippets

    Connects to AWS S3 to download snippets from a configured bucket.
    Supports caching and incremental updates.
    """

    def __init__(
        self,
        bucket_name: str,
        prefix: str = "snippets/",
        region: str = "us-east-1",
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize S3 client

        Args:
            bucket_name: Name of S3 bucket
            prefix: Key prefix for snippets (default: "snippets/")
            region: AWS region (default: "us-east-1")
            cache_dir: Local directory for caching (default: sherpa/data/cache/s3/)
        """
        # Check if boto3 is available
        if not BOTO3_AVAILABLE:
            logger.error("boto3 is not installed. Install with: pip install boto3")
            raise ImportError("boto3 is required for S3 snippet fetching")

        self.bucket_name = bucket_name
        self.prefix = prefix
        self.region = region

        # Setup cache directory
        if cache_dir is None:
            cache_dir = Path.cwd() / "sherpa" / "data" / "cache" / "s3"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3', region_name=region)
            logger.info(f"Initialized S3 client for bucket: {bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Configure AWS credentials first.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def fetch_snippets(self, use_cache: bool = True) -> List[Path]:
        """
        Fetch all snippet files from S3 bucket

        Args:
            use_cache: Whether to use cached files (default: True)

        Returns:
            List of paths to downloaded snippet files
        """
        snippet_files = []

        try:
            logger.info(f"Fetching snippets from S3 bucket: {self.bucket_name}")

            # List all objects in the bucket with the prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.prefix)

            file_count = 0
            for page in pages:
                if 'Contents' not in page:
                    continue

                for obj in page['Contents']:
                    key = obj['Key']

                    # Skip if not a markdown file
                    if not key.endswith('.md'):
                        continue

                    # Skip if it's just the prefix (directory marker)
                    if key == self.prefix:
                        continue

                    # Download the file
                    local_file = self._download_snippet(key, use_cache=use_cache)
                    if local_file:
                        snippet_files.append(local_file)
                        file_count += 1

            logger.info(f"Fetched {file_count} snippets from S3")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                logger.error(f"S3 bucket not found: {self.bucket_name}")
            else:
                logger.error(f"S3 error: {e}")
        except Exception as e:
            logger.error(f"Error fetching snippets from S3: {e}")

        return snippet_files

    def _download_snippet(self, key: str, use_cache: bool = True) -> Optional[Path]:
        """
        Download a single snippet file from S3

        Args:
            key: S3 object key
            use_cache: Whether to use cached version if available

        Returns:
            Path to downloaded file or None on error
        """
        try:
            # Calculate local file path (preserve directory structure)
            relative_path = key.replace(self.prefix, '', 1)
            local_file = self.cache_dir / relative_path
            local_file.parent.mkdir(parents=True, exist_ok=True)

            # Check cache if enabled
            if use_cache and local_file.exists():
                # Check if file is up to date
                try:
                    head_response = self.s3_client.head_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    s3_modified = head_response['LastModified']
                    local_modified = os.path.getmtime(local_file)

                    # If S3 file is not newer, use cached version
                    if s3_modified.timestamp() <= local_modified:
                        logger.debug(f"Using cached snippet: {relative_path}")
                        return local_file
                except Exception as e:
                    logger.warning(f"Error checking cache freshness: {e}")

            # Download from S3
            logger.debug(f"Downloading snippet from S3: {key}")
            self.s3_client.download_file(
                self.bucket_name,
                key,
                str(local_file)
            )

            return local_file

        except ClientError as e:
            logger.error(f"Error downloading {key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading {key}: {e}")
            return None

    def invalidate_cache(self) -> None:
        """Clear all cached snippet files"""
        try:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                logger.info("S3 cache cleared")
        except Exception as e:
            logger.error(f"Error clearing S3 cache: {e}")

    def test_connection(self) -> bool:
        """
        Test S3 connection and bucket access

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to list objects in the bucket (limit to 1)
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.prefix,
                MaxKeys=1
            )
            logger.info(f"S3 connection test successful for bucket: {self.bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"S3 connection test failed: {error_code}")
            return False
        except Exception as e:
            logger.error(f"S3 connection test failed: {e}")
            return False


# Singleton instance
_s3_client: Optional[S3Client] = None


def get_s3_client(
    bucket_name: Optional[str] = None,
    prefix: str = "snippets/",
    region: str = "us-east-1"
) -> Optional[S3Client]:
    """
    Get or create S3 client singleton

    Args:
        bucket_name: S3 bucket name (required on first call)
        prefix: Key prefix for snippets
        region: AWS region

    Returns:
        S3Client instance or None if not configured
    """
    global _s3_client

    if _s3_client is None and bucket_name:
        try:
            _s3_client = S3Client(
                bucket_name=bucket_name,
                prefix=prefix,
                region=region
            )
        except Exception as e:
            logger.error(f"Failed to create S3 client: {e}")
            return None

    return _s3_client
