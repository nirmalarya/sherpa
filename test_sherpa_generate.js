#!/usr/bin/env node

/**
 * Test script for sherpa generate command
 * Verifies all aspects of the generate functionality
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧪 Testing sherpa generate command\n');

// Test directory
const testDir = '/tmp/sherpa_generate_test';
const testResultsDir = path.join(process.cwd(), 'test_results_generate');

// Create test results directory
if (!fs.existsSync(testResultsDir)) {
  fs.mkdirSync(testResultsDir);
}

// Clean up test directory
if (fs.existsSync(testDir)) {
  execSync(`rm -rf ${testDir}/*`);
} else {
  fs.mkdirSync(testDir, { recursive: true });
}

let passCount = 0;
let failCount = 0;

function test(description, testFn) {
  try {
    testFn();
    console.log(`✓ ${description}`);
    passCount++;
    return true;
  } catch (error) {
    console.log(`✗ ${description}`);
    console.log(`  Error: ${error.message}`);
    failCount++;
    return false;
  }
}

console.log('Step 1: Run sherpa generate command\n');

try {
  // Run sherpa generate in test directory
  const output = execSync(
    `cd ${testDir} && ${process.cwd()}/venv-312/bin/python -m sherpa.cli.main generate`,
    { encoding: 'utf-8', env: { ...process.env, PYTHONPATH: process.cwd() } }
  );

  console.log('Command output:');
  console.log(output);
  console.log();

  // Save output for verification
  fs.writeFileSync(
    path.join(testResultsDir, 'generate_output.txt'),
    output
  );

} catch (error) {
  console.log('✗ Failed to run sherpa generate command');
  console.log(`  Error: ${error.message}`);
  console.log(`  Output: ${error.stdout}`);
  console.log(`  Stderr: ${error.stderr}`);
  process.exit(1);
}

console.log('Step 2: Verify .cursor/rules/ directory created\n');

test('.cursor/rules/ directory exists', () => {
  const cursorRulesDir = path.join(testDir, '.cursor', 'rules');
  if (!fs.existsSync(cursorRulesDir)) {
    throw new Error('Directory not found: .cursor/rules/');
  }
  if (!fs.statSync(cursorRulesDir).isDirectory()) {
    throw new Error('.cursor/rules/ is not a directory');
  }
});

test('.cursor/rules/00-sherpa-knowledge.md file exists', () => {
  const knowledgeFile = path.join(testDir, '.cursor', 'rules', '00-sherpa-knowledge.md');
  if (!fs.existsSync(knowledgeFile)) {
    throw new Error('File not found: .cursor/rules/00-sherpa-knowledge.md');
  }
});

console.log();
console.log('Step 3: Verify CLAUDE.md file created with injected snippets\n');

test('CLAUDE.md file exists', () => {
  const claudeFile = path.join(testDir, 'CLAUDE.md');
  if (!fs.existsSync(claudeFile)) {
    throw new Error('File not found: CLAUDE.md');
  }
});

test('CLAUDE.md contains "Knowledge Base" section', () => {
  const claudeFile = path.join(testDir, 'CLAUDE.md');
  const content = fs.readFileSync(claudeFile, 'utf-8');
  if (!content.includes('Knowledge Base')) {
    throw new Error('CLAUDE.md does not contain "Knowledge Base" section');
  }
});

test('CLAUDE.md contains snippets content', () => {
  const claudeFile = path.join(testDir, 'CLAUDE.md');
  const content = fs.readFileSync(claudeFile, 'utf-8');

  // Should contain at least some snippet titles or default message
  const hasSnippets = content.includes('Security') ||
                      content.includes('Python') ||
                      content.includes('React') ||
                      content.includes('No custom snippets');

  if (!hasSnippets) {
    throw new Error('CLAUDE.md does not contain snippet content');
  }

  // Save for verification
  fs.writeFileSync(
    path.join(testResultsDir, 'CLAUDE.md'),
    content
  );
});

console.log();
console.log('Step 4: Verify copilot-instructions.md file created\n');

test('copilot-instructions.md file exists', () => {
  const copilotFile = path.join(testDir, 'copilot-instructions.md');
  if (!fs.existsSync(copilotFile)) {
    throw new Error('File not found: copilot-instructions.md');
  }
});

test('copilot-instructions.md contains "Code Patterns" section', () => {
  const copilotFile = path.join(testDir, 'copilot-instructions.md');
  const content = fs.readFileSync(copilotFile, 'utf-8');
  if (!content.includes('Code Patterns')) {
    throw new Error('copilot-instructions.md does not contain "Code Patterns" section');
  }
});

test('copilot-instructions.md has reasonable size', () => {
  const copilotFile = path.join(testDir, 'copilot-instructions.md');
  const stats = fs.statSync(copilotFile);
  if (stats.size < 100) {
    throw new Error('copilot-instructions.md is too small (less than 100 bytes)');
  }

  // Save for verification
  const content = fs.readFileSync(copilotFile, 'utf-8');
  fs.writeFileSync(
    path.join(testResultsDir, 'copilot-instructions.md'),
    content
  );
});

console.log();
console.log('Step 5: Verify all files contain relevant knowledge snippets\n');

test('Knowledge file contains organizational snippets', () => {
  const knowledgeFile = path.join(testDir, '.cursor', 'rules', '00-sherpa-knowledge.md');
  const content = fs.readFileSync(knowledgeFile, 'utf-8');

  // Should contain snippet structure or default message
  const hasContent = content.includes('Knowledge') ||
                     content.includes('Snippet') ||
                     content.includes('Category');

  if (!hasContent) {
    throw new Error('Knowledge file does not contain expected content');
  }

  // Save for verification
  fs.writeFileSync(
    path.join(testResultsDir, '00-sherpa-knowledge.md'),
    content
  );
});

test('Files are properly formatted markdown', () => {
  const files = [
    path.join(testDir, '.cursor', 'rules', '00-sherpa-knowledge.md'),
    path.join(testDir, 'CLAUDE.md'),
    path.join(testDir, 'copilot-instructions.md')
  ];

  files.forEach(file => {
    const content = fs.readFileSync(file, 'utf-8');

    // Basic markdown checks
    if (!content.includes('#')) {
      throw new Error(`${path.basename(file)} does not contain markdown headers`);
    }

    // Should not be empty
    if (content.length < 50) {
      throw new Error(`${path.basename(file)} is too short`);
    }
  });
});

console.log();
console.log('Step 6: Verify success message with file paths displayed\n');

test('Command output contains success message', () => {
  const output = fs.readFileSync(
    path.join(testResultsDir, 'generate_output.txt'),
    'utf-8'
  );

  if (!output.includes('Success') && !output.includes('generated')) {
    throw new Error('Output does not contain success message');
  }
});

test('Command output lists generated files', () => {
  const output = fs.readFileSync(
    path.join(testResultsDir, 'generate_output.txt'),
    'utf-8'
  );

  const expectedFiles = [
    'CLAUDE.md',
    'copilot-instructions.md',
    '00-sherpa-knowledge.md'
  ];

  expectedFiles.forEach(file => {
    if (!output.includes(file) && !output.includes('Created')) {
      throw new Error(`Output does not mention file: ${file}`);
    }
  });
});

// Summary
console.log('\n' + '='.repeat(60));
console.log('Test Summary');
console.log('='.repeat(60));
console.log(`Total tests: ${passCount + failCount}`);
console.log(`Passed: ${passCount}`);
console.log(`Failed: ${failCount}`);
console.log(`Success rate: ${((passCount / (passCount + failCount)) * 100).toFixed(1)}%`);

if (failCount === 0) {
  console.log('\n✓ All tests passed! 🎉');
  console.log(`\nTest results saved to: ${testResultsDir}`);
  process.exit(0);
} else {
  console.log('\n✗ Some tests failed');
  process.exit(1);
}
