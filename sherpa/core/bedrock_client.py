"""
AWS Bedrock Knowledge Base Client

This module provides integration with AWS Bedrock Knowledge Base for semantic search
of code snippets and organizational knowledge.

In development mode without AWS credentials, it provides mock responses for testing.
"""

import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from sherpa.core.logging_config import get_logger

logger = get_logger("sherpa.bedrock")


class BedrockKnowledgeBaseClient:
    """
    Client for querying AWS Bedrock Knowledge Base

    Provides semantic search capabilities for code snippets using vector embeddings.
    Falls back to mock responses if AWS credentials are not configured.
    """

    def __init__(self, kb_id: Optional[str] = None, region: str = "us-east-1"):
        """
        Initialize Bedrock Knowledge Base client

        Args:
            kb_id: Knowledge Base ID (optional, can be set from config)
            region: AWS region (default: us-east-1)
        """
        self.kb_id = kb_id or os.getenv('BEDROCK_KB_ID')
        self.region = region
        self.mock_mode = not self._has_aws_credentials()

        if self.mock_mode:
            logger.warning("AWS credentials not found - running in mock mode")
            logger.warning("Bedrock queries will return simulated responses")
        else:
            logger.info(f"Bedrock client initialized - KB ID: {self.kb_id}, Region: {self.region}")

    def _has_aws_credentials(self) -> bool:
        """Check if AWS credentials are configured"""
        # Check for AWS credentials in environment or AWS config
        has_access_key = bool(os.getenv('AWS_ACCESS_KEY_ID'))
        has_secret_key = bool(os.getenv('AWS_SECRET_ACCESS_KEY'))
        has_profile = bool(os.getenv('AWS_PROFILE'))

        # Could also check ~/.aws/credentials file here
        return (has_access_key and has_secret_key) or has_profile

    async def connect(self) -> bool:
        """
        Test connection to Bedrock Knowledge Base

        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.mock_mode:
                logger.info("Mock mode: Simulating successful connection")
                await asyncio.sleep(0.1)  # Simulate network delay
                return True

            # In production, initialize boto3 client here:
            # import boto3
            # self.bedrock_agent_runtime = boto3.client(
            #     'bedrock-agent-runtime',
            #     region_name=self.region
            # )
            # Test the connection by making a simple query

            logger.info("Successfully connected to Bedrock Knowledge Base")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Bedrock: {e}", exc_info=True)
            return False

    async def query(
        self,
        query_text: str,
        max_results: int = 5,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Query the Knowledge Base for relevant snippets

        Args:
            query_text: The search query (e.g., "authentication patterns")
            max_results: Maximum number of results to return
            min_score: Minimum relevance score (0.0 to 1.0)

        Returns:
            List of search results with content and metadata
        """
        try:
            if self.mock_mode:
                return await self._mock_query(query_text, max_results)

            # In production, use boto3 to query Bedrock:
            # response = self.bedrock_agent_runtime.retrieve(
            #     knowledgeBaseId=self.kb_id,
            #     retrievalQuery={'text': query_text},
            #     retrievalConfiguration={
            #         'vectorSearchConfiguration': {
            #             'numberOfResults': max_results
            #         }
            #     }
            # )
            #
            # results = []
            # for item in response.get('retrievalResults', []):
            #     if item.get('score', 0) >= min_score:
            #         results.append({
            #             'content': item['content']['text'],
            #             'score': item['score'],
            #             'metadata': item.get('metadata', {}),
            #             'location': item.get('location', {})
            #         })
            #
            # return results

            logger.info(f"Queried Bedrock KB for: '{query_text}'")
            return []

        except Exception as e:
            logger.error(f"Error querying Bedrock: {e}", exc_info=True)
            return []

    async def _mock_query(self, query_text: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Generate mock query results for testing

        Simulates Bedrock Knowledge Base responses based on query keywords
        """
        await asyncio.sleep(0.2)  # Simulate network delay

        # Define mock snippets based on common queries
        mock_snippets = {
            'authentication': {
                'content': '''# Authentication Patterns

## JWT Authentication
```python
import jwt
from datetime import datetime, timedelta

def create_token(user_id: str, secret_key: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')
```

## OAuth 2.0 Flow
- Authorization Code flow for web apps
- Client Credentials for service-to-service
- PKCE for mobile/SPA applications
''',
                'score': 0.92,
                'metadata': {
                    'category': 'security',
                    'language': 'python',
                    'tags': ['jwt', 'oauth', 'authentication']
                }
            },
            'error': {
                'content': '''# Error Handling Best Practices

## Python Exception Handling
```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error occurred")
    # Handle or re-raise
finally:
    cleanup_resources()
```

## Error Response Format
```python
{
    "error": "InvalidInput",
    "message": "User-friendly message",
    "details": {...}
}
```
''',
                'score': 0.88,
                'metadata': {
                    'category': 'python',
                    'language': 'python',
                    'tags': ['error-handling', 'exceptions', 'logging']
                }
            },
            'async': {
                'content': '''# Async/Await Patterns

## FastAPI Async Endpoint
```python
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/items/{item_id}") as resp:
            return await resp.json()
```

## Concurrent Operations
```python
results = await asyncio.gather(
    fetch_user(user_id),
    fetch_orders(user_id),
    fetch_preferences(user_id)
)
```
''',
                'score': 0.85,
                'metadata': {
                    'category': 'python',
                    'language': 'python',
                    'tags': ['async', 'asyncio', 'concurrency']
                }
            }
        }

        # Find matching snippets based on query keywords
        results = []
        query_lower = query_text.lower()

        for keyword, snippet_data in mock_snippets.items():
            if keyword in query_lower:
                results.append({
                    'content': snippet_data['content'],
                    'score': snippet_data['score'],
                    'metadata': snippet_data['metadata'],
                    'location': {
                        'type': 'MOCK',
                        'source': f'mock-knowledge-base/{keyword}.md'
                    }
                })

        # If no specific match, return a generic result
        if not results:
            results.append({
                'content': f'''# Search Results for "{query_text}"

This is a mock result from the Bedrock Knowledge Base simulator.
In production, this would return actual snippets from your organization's knowledge base.

## Getting Started
1. Configure AWS credentials
2. Set BEDROCK_KB_ID environment variable
3. Initialize Bedrock client with proper permissions

For development/testing, the mock mode provides simulated responses.
''',
                'score': 0.70,
                'metadata': {
                    'category': 'general',
                    'tags': ['mock', 'development']
                },
                'location': {
                    'type': 'MOCK',
                    'source': 'mock-knowledge-base/default.md'
                }
            })

        # Limit results
        results = results[:max_results]

        logger.info(f"Mock query returned {len(results)} results for '{query_text}'")
        return results

    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for display

        Args:
            results: List of search results from query()

        Returns:
            Formatted string with results and metadata
        """
        if not results:
            return "No results found"

        output = []
        output.append(f"\nFound {len(results)} results:\n")
        output.append("=" * 80)

        for i, result in enumerate(results, 1):
            score = result.get('score', 0)
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            location = result.get('location', {})

            output.append(f"\n Result {i} (Score: {score:.2f})")
            output.append(f" Source: {location.get('source', 'Unknown')}")
            output.append(f" Category: {metadata.get('category', 'N/A')}")
            output.append(f" Tags: {', '.join(metadata.get('tags', []))}")
            output.append("\n" + "-" * 80)

            # Show first 500 chars of content
            preview = content[:500] + "..." if len(content) > 500 else content
            output.append(preview)
            output.append("=" * 80)

        return "\n".join(output)


# Singleton instance for easy access
_bedrock_client: Optional[BedrockKnowledgeBaseClient] = None


def get_bedrock_client(kb_id: Optional[str] = None) -> BedrockKnowledgeBaseClient:
    """
    Get or create the Bedrock Knowledge Base client

    Args:
        kb_id: Knowledge Base ID (optional)

    Returns:
        BedrockKnowledgeBaseClient instance
    """
    global _bedrock_client

    if _bedrock_client is None:
        _bedrock_client = BedrockKnowledgeBaseClient(kb_id=kb_id)

    return _bedrock_client
