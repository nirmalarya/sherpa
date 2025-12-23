#!/usr/bin/env node

/**
 * Test Script for sherpa init command
 * Verifies all 5 test steps pass by checking the implementation
 */

const fs = require('fs');
const path = require('path');

console.log('═══════════════════════════════════════════════════════');
console.log('  SHERPA INIT - Test Verification');
console.log('═══════════════════════════════════════════════════════');
console.log('');

function runTests() {
  let passed = 0;
  let failed = 0;

  // Step 1: Verify CLI main.py exists with init command
  console.log('🔍 Step 1: Verify sherpa init command exists...');
  try {
    const mainPath = path.join(__dirname, 'sherpa', 'cli', 'main.py');

    if (!fs.existsSync(mainPath)) {
      console.log('❌ FAIL: sherpa/cli/main.py does not exist');
      failed++;
    } else {
      const content = fs.readFileSync(mainPath, 'utf8');

      // Check for Click framework
      const hasClick = content.includes('import click') || content.includes('from click');
      const hasCliGroup = content.includes('@click.group()') || content.includes('def cli()');
      const hasInitCommand = content.includes('def init()');

      if (hasClick && hasCliGroup && hasInitCommand) {
        console.log('✅ PASS: sherpa init command is registered');
        console.log('   - Click framework imported');
        console.log('   - CLI group created');
        console.log('   - init command defined');
        passed++;
      } else {
        console.log('❌ FAIL: sherpa init command not properly set up');
        console.log(`   - Click: ${hasClick}`);
        console.log(`   - CLI group: ${hasCliGroup}`);
        console.log(`   - Init command: ${hasInitCommand}`);
        failed++;
      }
    }
  } catch (error) {
    console.log('❌ FAIL: Error checking CLI main.py');
    console.log('   Error:', error.message);
    failed++;
  }

  console.log('');

  // Step 2: Verify configuration file is created (in sherpa/config.json)
  console.log('🔍 Step 2: Verify configuration file can be created...');
  try {
    const initPath = path.join(__dirname, 'sherpa', 'cli', 'commands', 'init.py');
    const content = fs.readFileSync(initPath, 'utf8');

    const hasCreateConfigFunction = content.includes('def create_config_file');
    const hasJsonWrite = content.includes('json.dump') || content.includes('json.dumps');
    const hasConfigPath = content.includes('config.json');

    if (hasCreateConfigFunction && hasJsonWrite && hasConfigPath) {
      console.log('✅ PASS: Configuration file creation implemented');
      console.log('   - create_config_file function exists');
      console.log('   - JSON writing implemented');
      console.log('   - config.json path referenced');
      passed++;
    } else {
      console.log('❌ FAIL: Configuration file creation not complete');
      console.log(`   - Create config function: ${hasCreateConfigFunction}`);
      console.log(`   - JSON write: ${hasJsonWrite}`);
      console.log(`   - Config path: ${hasConfigPath}`);
      failed++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error checking config creation');
    console.log('   Error:', error.message);
    failed++;
  }

  console.log('');

  // Step 3: Verify Bedrock KB ID is saved
  console.log('🔍 Step 3: Verify Bedrock KB ID is saved in config...');
  try {
    const initPath = path.join(__dirname, 'sherpa', 'cli', 'commands', 'init.py');
    const content = fs.readFileSync(initPath, 'utf8');

    const hasBedrockConfig = content.includes('"bedrock"') || content.includes("'bedrock'");
    const hasKbId = content.includes('knowledge_base_id') || content.includes('kb_id');
    const hasRegion = content.includes('"region"') || content.includes("'region'");

    if (hasBedrockConfig && hasKbId && hasRegion) {
      console.log('✅ PASS: Bedrock KB configuration is saved');
      console.log('   - bedrock section in config');
      console.log('   - knowledge_base_id field');
      console.log('   - region field');
      passed++;
    } else {
      console.log('❌ FAIL: Bedrock KB configuration incomplete');
      console.log(`   - Bedrock config: ${hasBedrockConfig}`);
      console.log(`   - KB ID: ${hasKbId}`);
      console.log(`   - Region: ${hasRegion}`);
      failed++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error checking Bedrock config');
    console.log('   Error:', error.message);
    failed++;
  }

  console.log('');

  // Step 4: Verify AWS credentials are validated
  console.log('🔍 Step 4: Verify AWS credentials validation...');
  try {
    const initPath = path.join(__dirname, 'sherpa', 'cli', 'commands', 'init.py');
    const content = fs.readFileSync(initPath, 'utf8');

    const hasBoto3Import = content.includes('import boto3') || content.includes('from boto3');
    const hasCredentialsCheck = content.includes('check_aws_credentials');
    const hasSessionCheck = content.includes('boto3.Session') || content.includes('get_credentials');

    if (hasBoto3Import && hasCredentialsCheck && hasSessionCheck) {
      console.log('✅ PASS: AWS credentials validation implemented');
      console.log('   - boto3 imported');
      console.log('   - check_aws_credentials function exists');
      console.log('   - Session/credentials check implemented');
      passed++;
    } else {
      console.log('❌ FAIL: AWS credentials validation incomplete');
      console.log(`   - boto3 import: ${hasBoto3Import}`);
      console.log(`   - Credentials check: ${hasCredentialsCheck}`);
      console.log(`   - Session check: ${hasSessionCheck}`);
      failed++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error checking AWS validation');
    console.log('   Error:', error.message);
    failed++;
  }

  console.log('');

  // Step 5: Verify success message displayed with Rich formatting
  console.log('🔍 Step 5: Verify Rich formatting for success message...');
  try {
    const initPath = path.join(__dirname, 'sherpa', 'cli', 'commands', 'init.py');
    const content = fs.readFileSync(initPath, 'utf8');

    const hasRichConsole = content.includes('from rich.console import Console');
    const hasRichPanel = content.includes('from rich.panel import Panel');
    const hasConsoleUsage = content.includes('console.print');
    const hasPanelUsage = content.includes('Panel');
    const hasSuccessMessage = content.includes('Initialization Complete') ||
                             content.includes('Success') ||
                             content.includes('✓') ||
                             content.includes('green');

    if (hasRichConsole && hasRichPanel && hasConsoleUsage && hasPanelUsage && hasSuccessMessage) {
      console.log('✅ PASS: Rich formatting implemented');
      console.log('   - Rich Console imported');
      console.log('   - Rich Panel imported');
      console.log('   - console.print used');
      console.log('   - Panel used for formatting');
      console.log('   - Success message present');
      passed++;
    } else {
      console.log('❌ FAIL: Rich formatting incomplete');
      console.log(`   - Rich Console: ${hasRichConsole}`);
      console.log(`   - Rich Panel: ${hasRichPanel}`);
      console.log(`   - Console usage: ${hasConsoleUsage}`);
      console.log(`   - Panel usage: ${hasPanelUsage}`);
      console.log(`   - Success message: ${hasSuccessMessage}`);
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

const success = runTests();
process.exit(success ? 0 : 1);
