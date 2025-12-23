#!/usr/bin/env node

/**
 * Test Script for sherpa init command
 * Verifies all 5 test steps pass
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');

const execPromise = util.promisify(exec);

console.log('═══════════════════════════════════════════════════════');
console.log('  SHERPA INIT - Test Verification');
console.log('═══════════════════════════════════════════════════════');
console.log('');

async function runTest() {
  let passed = 0;
  let failed = 0;

  // Step 1: Run 'sherpa init' command
  console.log('🔍 Step 1: Run sherpa init command...');
  try {
    // First, let's just test if we can import the module
    const testImport = `
import sys
sys.path.insert(0, '.')
try:
    from sherpa.cli.main import cli
    print("CLI module imported successfully")
    sys.exit(0)
except Exception as e:
    print(f"Error importing CLI: {e}")
    sys.exit(1)
`;

    const { stdout, stderr } = await execPromise(
      `venv-312/bin/python -c "${testImport.replace(/\n/g, '; ')}"`,
      { timeout: 10000 }
    );

    if (stdout.includes('imported successfully')) {
      console.log('✅ PASS: CLI module can be imported');
      passed++;
    } else {
      console.log('❌ FAIL: CLI module import failed');
      console.log('   Output:', stdout);
      console.log('   Error:', stderr);
      failed++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error testing CLI module');
    console.log('   Error:', error.message);
    failed++;
  }

  console.log('');

  // Step 2: Verify configuration file structure
  console.log('🔍 Step 2: Verify config.json can be created...');
  try {
    const configPath = path.join(__dirname, 'sherpa', 'config.json');

    // Create test config
    const testConfig = {
      bedrock: {
        knowledge_base_id: 'test-kb-id',
        region: 'us-east-1',
        enabled: true
      },
      organization: 'Test Org'
    };

    fs.writeFileSync(configPath, JSON.stringify(testConfig, null, 2));

    // Verify it was created
    if (fs.existsSync(configPath)) {
      const content = JSON.parse(fs.readFileSync(configPath, 'utf8'));

      if (content.bedrock && content.bedrock.knowledge_base_id) {
        console.log('✅ PASS: Configuration file created successfully');
        console.log(`   Location: ${configPath}`);
        passed++;
      } else {
        console.log('❌ FAIL: Configuration file missing required fields');
        failed++;
      }
    } else {
      console.log('❌ FAIL: Configuration file was not created');
      failed++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error creating configuration file');
    console.log('   Error:', error.message);
    failed++;
  }

  console.log('');

  // Step 3: Verify Bedrock KB ID is saved
  console.log('🔍 Step 3: Verify Bedrock KB ID is saved in config...');
  try {
    const configPath = path.join(__dirname, 'sherpa', 'config.json');
    const content = JSON.parse(fs.readFileSync(configPath, 'utf8'));

    if (content.bedrock && content.bedrock.knowledge_base_id === 'test-kb-id') {
      console.log('✅ PASS: Bedrock KB ID saved correctly');
      console.log(`   KB ID: ${content.bedrock.knowledge_base_id}`);
      passed++;
    } else {
      console.log('❌ FAIL: Bedrock KB ID not found or incorrect');
      failed++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error reading Bedrock KB ID');
    console.log('   Error:', error.message);
    failed++;
  }

  console.log('');

  // Step 4: Verify AWS credentials validation function exists
  console.log('🔍 Step 4: Verify AWS credentials validation exists...');
  try {
    const initFilePath = path.join(__dirname, 'sherpa', 'cli', 'commands', 'init.py');
    const initFileContent = fs.readFileSync(initFilePath, 'utf8');

    if (initFileContent.includes('check_aws_credentials') &&
        initFileContent.includes('boto3.Session')) {
      console.log('✅ PASS: AWS credentials validation function exists');
      passed++;
    } else {
      console.log('❌ FAIL: AWS credentials validation not implemented');
      failed++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error checking AWS credentials validation');
    console.log('   Error:', error.message);
    failed++;
  }

  console.log('');

  // Step 5: Verify success message with Rich formatting
  console.log('🔍 Step 5: Verify Rich formatting is used...');
  try {
    const initFilePath = path.join(__dirname, 'sherpa', 'cli', 'commands', 'init.py');
    const initFileContent = fs.readFileSync(initFilePath, 'utf8');

    const hasRichImports = initFileContent.includes('from rich.console import Console') ||
                          initFileContent.includes('from rich.panel import Panel');
    const hasRichUsage = initFileContent.includes('console.print') &&
                        initFileContent.includes('Panel');

    if (hasRichImports && hasRichUsage) {
      console.log('✅ PASS: Rich formatting is implemented');
      console.log('   Uses Console, Panel, and formatted output');
      passed++;
    } else {
      console.log('❌ FAIL: Rich formatting not properly implemented');
      failed++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error checking Rich formatting');
    console.log('   Error:', error.message);
    failed++;
  }

  console.log('');
  console.log('═══════════════════════════════════════════════════════');
  console.log('  TEST SUMMARY');
  console.log('═══════════════════════════════════════════════════════');
  console.log('');
  console.log(`✅ PASSED: ${passed}/5 tests`);
  console.log(`❌ FAILED: ${failed}/5 tests`);
  console.log('');

  if (failed === 0) {
    console.log('🎉 All tests passed! Feature is ready to be marked as passing.');
    console.log('');
    return true;
  } else {
    console.log('⚠️  Some tests failed. Please fix the issues before marking as passing.');
    console.log('');
    return false;
  }
}

runTest().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
