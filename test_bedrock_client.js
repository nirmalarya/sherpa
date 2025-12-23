#!/usr/bin/env node

/**
 * Test AWS Bedrock Knowledge Base Client
 *
 * Feature: AWS Bedrock Knowledge Base client - Client connects to AWS Bedrock and can query knowledge base for code snippets
 *
 * Steps:
 * Step 1: Initialize boto3 Bedrock client with proper credentials
 * Step 2: Verify connection to Bedrock Knowledge Base
 * Step 3: Execute test query for 'authentication' snippets
 * Step 4: Verify semantic search returns relevant results
 * Step 5: Verify results are properly formatted
 */

const { spawn } = require('child_process');

// Test results
const results = {
  passed: [],
  failed: []
};

function runPythonTest(testCode) {
  return new Promise((resolve, reject) => {
    const python = spawn('venv-312/bin/python3', ['-c', testCode]);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      resolve({ code, stdout, stderr });
    });

    python.on('error', (err) => {
      reject(err);
    });
  });
}

async function testStep1_InitializeClient() {
  console.log('\n🔍 Step 1: Initialize boto3 Bedrock client with proper credentials');

  const testCode = `
import sys
sys.path.insert(0, '.')

from sherpa.core.bedrock_client import BedrockKnowledgeBaseClient

# Initialize client
client = BedrockKnowledgeBaseClient(kb_id='test-kb-123', region='us-east-1')

# Verify client was created
assert client is not None, "Client should not be None"
assert client.kb_id == 'test-kb-123', "KB ID should match"
assert client.region == 'us-east-1', "Region should match"

print("✓ Client initialized successfully")
print(f"✓ KB ID: {client.kb_id}")
print(f"✓ Region: {client.region}")
print(f"✓ Mock mode: {client.mock_mode}")
`;

  try {
    const result = await runPythonTest(testCode);

    if (result.code === 0 && result.stdout.includes('Client initialized successfully')) {
      console.log('✅ PASS: Bedrock client initialized');
      console.log(result.stdout.trim());
      results.passed.push('Step 1: Initialize client');
      return true;
    } else {
      console.log('❌ FAIL: Client initialization failed');
      console.log('STDOUT:', result.stdout);
      console.log('STDERR:', result.stderr);
      results.failed.push('Step 1: Initialize client');
      return false;
    }
  } catch (error) {
    console.log('❌ FAIL: Error running test:', error.message);
    results.failed.push('Step 1: Initialize client');
    return false;
  }
}

async function testStep2_VerifyConnection() {
  console.log('\n🔍 Step 2: Verify connection to Bedrock Knowledge Base');

  const testCode = `
import sys
import asyncio
sys.path.insert(0, '.')

from sherpa.core.bedrock_client import BedrockKnowledgeBaseClient

async def test_connection():
    client = BedrockKnowledgeBaseClient(kb_id='test-kb-123')

    # Test connection
    connected = await client.connect()

    assert connected == True, "Connection should succeed"
    print("✓ Successfully connected to Bedrock Knowledge Base")
    print(f"✓ Connection status: {connected}")

asyncio.run(test_connection())
`;

  try {
    const result = await runPythonTest(testCode);

    if (result.code === 0 && result.stdout.includes('Successfully connected')) {
      console.log('✅ PASS: Connection verified');
      console.log(result.stdout.trim());
      results.passed.push('Step 2: Verify connection');
      return true;
    } else {
      console.log('❌ FAIL: Connection verification failed');
      console.log('STDOUT:', result.stdout);
      console.log('STDERR:', result.stderr);
      results.failed.push('Step 2: Verify connection');
      return false;
    }
  } catch (error) {
    console.log('❌ FAIL: Error running test:', error.message);
    results.failed.push('Step 2: Verify connection');
    return false;
  }
}

async function testStep3_ExecuteQuery() {
  console.log('\n🔍 Step 3: Execute test query for \'authentication\' snippets');

  const testCode = `
import sys
import asyncio
sys.path.insert(0, '.')

from sherpa.core.bedrock_client import BedrockKnowledgeBaseClient

async def test_query():
    client = BedrockKnowledgeBaseClient(kb_id='test-kb-123')

    # Execute query
    results = await client.query('authentication', max_results=5)

    assert isinstance(results, list), "Results should be a list"
    assert len(results) > 0, "Should return at least one result"
    print(f"✓ Query executed successfully")
    print(f"✓ Returned {len(results)} results")

    return results

results = asyncio.run(test_query())
`;

  try {
    const result = await runPythonTest(testCode);

    if (result.code === 0 && result.stdout.includes('Query executed successfully')) {
      console.log('✅ PASS: Query executed');
      console.log(result.stdout.trim());
      results.passed.push('Step 3: Execute query');
      return true;
    } else {
      console.log('❌ FAIL: Query execution failed');
      console.log('STDOUT:', result.stdout);
      console.log('STDERR:', result.stderr);
      results.failed.push('Step 3: Execute query');
      return false;
    }
  } catch (error) {
    console.log('❌ FAIL: Error running test:', error.message);
    results.failed.push('Step 3: Execute query');
    return false;
  }
}

async function testStep4_VerifySemanticSearch() {
  console.log('\n🔍 Step 4: Verify semantic search returns relevant results');

  const testCode = `
import sys
import asyncio
sys.path.insert(0, '.')

from sherpa.core.bedrock_client import BedrockKnowledgeBaseClient

async def test_semantic_search():
    client = BedrockKnowledgeBaseClient(kb_id='test-kb-123')

    # Execute query for authentication
    results = await client.query('authentication patterns', max_results=5)

    # Verify results structure
    assert len(results) > 0, "Should return results"

    first_result = results[0]
    assert 'content' in first_result, "Result should have content"
    assert 'score' in first_result, "Result should have score"
    assert 'metadata' in first_result, "Result should have metadata"

    # Verify relevance
    content = first_result['content'].lower()
    assert 'auth' in content or 'jwt' in content or 'oauth' in content, \
        "Content should be relevant to authentication"

    score = first_result['score']
    assert score > 0.5, f"Score should be > 0.5, got {score}"

    print(f"✓ Semantic search returned {len(results)} relevant results")
    print(f"✓ Top result score: {score:.2f}")
    print(f"✓ Content is relevant to query")
    print(f"✓ Result has proper structure (content, score, metadata)")

asyncio.run(test_semantic_search())
`;

  try {
    const result = await runPythonTest(testCode);

    if (result.code === 0 && result.stdout.includes('relevant results')) {
      console.log('✅ PASS: Semantic search verified');
      console.log(result.stdout.trim());
      results.passed.push('Step 4: Verify semantic search');
      return true;
    } else {
      console.log('❌ FAIL: Semantic search verification failed');
      console.log('STDOUT:', result.stdout);
      console.log('STDERR:', result.stderr);
      results.failed.push('Step 4: Verify semantic search');
      return false;
    }
  } catch (error) {
    console.log('❌ FAIL: Error running test:', error.message);
    results.failed.push('Step 4: Verify semantic search');
    return false;
  }
}

async function testStep5_VerifyFormatting() {
  console.log('\n🔍 Step 5: Verify results are properly formatted');

  const testCode = `
import sys
import asyncio
sys.path.insert(0, '.')

from sherpa.core.bedrock_client import BedrockKnowledgeBaseClient

async def test_formatting():
    client = BedrockKnowledgeBaseClient(kb_id='test-kb-123')

    # Execute query
    results = await client.query('authentication', max_results=3)

    # Format results
    formatted = client.format_results(results)

    assert isinstance(formatted, str), "Formatted output should be string"
    assert len(formatted) > 0, "Formatted output should not be empty"
    assert 'Found' in formatted, "Should show result count"
    assert 'Score:' in formatted, "Should show scores"

    print(f"✓ Results formatted successfully")
    print(f"✓ Formatted output length: {len(formatted)} characters")
    print(f"✓ Contains result count, scores, and content")

asyncio.run(test_formatting())
`;

  try {
    const result = await runPythonTest(testCode);

    if (result.code === 0 && result.stdout.includes('Results formatted successfully')) {
      console.log('✅ PASS: Result formatting verified');
      console.log(result.stdout.trim());
      results.passed.push('Step 5: Verify formatting');
      return true;
    } else {
      console.log('❌ FAIL: Result formatting verification failed');
      console.log('STDOUT:', result.stdout);
      console.log('STDERR:', result.stderr);
      results.failed.push('Step 5: Verify formatting');
      return false;
    }
  } catch (error) {
    console.log('❌ FAIL: Error running test:', error.message);
    results.failed.push('Step 5: Verify formatting');
    return false;
  }
}

async function runAllTests() {
  console.log('═══════════════════════════════════════════════════════════════');
  console.log('  AWS Bedrock Knowledge Base Client - Feature Test');
  console.log('═══════════════════════════════════════════════════════════════');

  await testStep1_InitializeClient();
  await testStep2_VerifyConnection();
  await testStep3_ExecuteQuery();
  await testStep4_VerifySemanticSearch();
  await testStep5_VerifyFormatting();

  // Summary
  console.log('\n═══════════════════════════════════════════════════════════════');
  console.log('  TEST SUMMARY');
  console.log('═══════════════════════════════════════════════════════════════');
  console.log(`\n✅ PASSED: ${results.passed.length}/5 tests`);
  results.passed.forEach(test => console.log(`   - ${test}`));

  if (results.failed.length > 0) {
    console.log(`\n❌ FAILED: ${results.failed.length}/5 tests`);
    results.failed.forEach(test => console.log(`   - ${test}`));
    console.log('\n⚠️  Some tests failed!');
    process.exit(1);
  } else {
    console.log('\n🎉 All tests passed! Bedrock client is working correctly.');
    process.exit(0);
  }
}

runAllTests().catch(error => {
  console.error('\n💥 Test suite error:', error);
  process.exit(1);
});
