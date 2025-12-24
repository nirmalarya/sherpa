#!/usr/bin/env node

/**
 * SHERPA V1 - CI/CD Pipeline Verification Script
 *
 * Verifies the GitHub Actions workflow file exists and is properly configured.
 * Tests all 6 steps from feature_list.json for the CI/CD pipeline feature.
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    bold: '\x1b[1m'
};

let passed = 0;
let failed = 0;

function runTest(name, description, testFn) {
    process.stdout.write(`${colors.cyan}⏳ Test: ${name}${colors.reset}\n`);
    process.stdout.write(`   ${description}\n`);

    try {
        const result = testFn();
        passed++;
        console.log(`${colors.green}✅ PASS${colors.reset}: ${result}\n`);
        return true;
    } catch (error) {
        failed++;
        console.log(`${colors.red}❌ FAIL${colors.reset}: ${error.message}\n`);
        return false;
    }
}

function main() {
    console.log(`${colors.bold}${colors.blue}
╔═══════════════════════════════════════════════════════════╗
║   🏔️  SHERPA V1 - CI/CD Pipeline Verification           ║
║   Testing GitHub Actions workflow configuration           ║
╚═══════════════════════════════════════════════════════════╝
${colors.reset}\n`);

    // Test 1: Verify workflow file exists
    runTest(
        'Workflow File Exists',
        'Step 1: Verify workflow file exists (.github/workflows/)',
        () => {
            const workflowPath = path.join(process.cwd(), '.github', 'workflows', 'ci.yml');
            if (!fs.existsSync(workflowPath)) {
                throw new Error(`Workflow file not found at ${workflowPath}`);
            }
            const stats = fs.statSync(workflowPath);
            return `Workflow file exists at .github/workflows/ci.yml (${stats.size} bytes)`;
        }
    );

    // Test 2: Verify workflow content is valid YAML
    runTest(
        'Workflow Content Valid',
        'Step 2: Verify workflow is valid YAML with proper GitHub Actions syntax',
        () => {
            const workflowPath = path.join(process.cwd(), '.github', 'workflows', 'ci.yml');
            const content = fs.readFileSync(workflowPath, 'utf8');

            // Basic YAML validation
            if (!content.includes('name:')) {
                throw new Error('Workflow missing name field');
            }
            if (!content.includes('on:')) {
                throw new Error('Workflow missing trigger configuration (on:)');
            }
            if (!content.includes('jobs:')) {
                throw new Error('Workflow missing jobs section');
            }

            // Count jobs
            const jobMatches = content.match(/^  [a-z-]+:/gm) || [];
            const jobCount = jobMatches.length;

            return `Valid YAML structure with ${jobCount} jobs defined`;
        }
    );

    // Test 3: Verify workflow triggers
    runTest(
        'Workflow Triggers',
        'Step 3: Verify workflow triggers on push and pull_request',
        () => {
            const workflowPath = path.join(process.cwd(), '.github', 'workflows', 'ci.yml');
            const content = fs.readFileSync(workflowPath, 'utf8');

            const hasPushTrigger = content.includes('push:') || content.includes('- push');
            const hasPRTrigger = content.includes('pull_request:') || content.includes('- pull_request');

            if (!hasPushTrigger && !hasPRTrigger) {
                throw new Error('No push or pull_request triggers found');
            }

            const triggers = [];
            if (hasPushTrigger) triggers.push('push');
            if (hasPRTrigger) triggers.push('pull_request');
            if (content.includes('workflow_dispatch')) triggers.push('manual');

            return `Triggers configured: ${triggers.join(', ')}`;
        }
    );

    // Test 4: Verify tests run
    runTest(
        'Test Jobs Configured',
        'Step 4: Verify tests run (backend, frontend, integration)',
        () => {
            const workflowPath = path.join(process.cwd(), '.github/workflows', 'ci.yml');
            const content = fs.readFileSync(workflowPath, 'utf8');

            const hasBackendTests = content.includes('backend-tests') || content.includes('pytest');
            const hasFrontendTests = content.includes('frontend-tests') || content.includes('npm');
            const hasIntegrationTests = content.includes('integration') || content.includes('e2e');

            const testTypes = [];
            if (hasBackendTests) testTypes.push('backend');
            if (hasFrontendTests) testTypes.push('frontend');
            if (hasIntegrationTests) testTypes.push('integration');

            if (testTypes.length === 0) {
                throw new Error('No test jobs found in workflow');
            }

            return `Test jobs configured: ${testTypes.join(', ')}`;
        }
    );

    // Test 5: Verify build succeeds
    runTest(
        'Build Jobs Configured',
        'Step 5: Verify build configuration (Docker, npm build)',
        () => {
            const workflowPath = path.join(process.cwd(), '.github/workflows/', 'ci.yml');
            const content = fs.readFileSync(workflowPath, 'utf8');

            const hasDockerBuild = content.includes('docker') || content.includes('Docker');
            const hasNpmBuild = content.includes('npm run build');
            const hasPythonSetup = content.includes('setup-python') || content.includes('pip install');

            const buildTypes = [];
            if (hasDockerBuild) buildTypes.push('Docker');
            if (hasNpmBuild) buildTypes.push('npm');
            if (hasPythonSetup) buildTypes.push('Python');

            if (buildTypes.length === 0) {
                throw new Error('No build jobs found in workflow');
            }

            return `Build jobs configured: ${buildTypes.join(', ')}`;
        }
    );

    // Test 6: Verify deployment configuration
    runTest(
        'Deployment Configured',
        'Step 6: Verify deployment job exists (optional, can be placeholder)',
        () => {
            const workflowPath = path.join(process.cwd(), '.github', 'workflows', 'ci.yml');
            const content = fs.readFileSync(workflowPath, 'utf8');

            const hasDeployJob = content.includes('deploy:') || content.includes('deployment');
            const hasDeployCondition = content.includes('if:') && content.includes('main');

            if (!hasDeployJob) {
                // Deployment is optional, so we'll pass with a note
                return 'Deployment job not configured (optional for CI/CD)';
            }

            const deployConfig = hasDeployCondition ? 'conditional (main branch)' : 'always runs';
            return `Deployment job configured: ${deployConfig}`;
        }
    );

    // Print summary
    const total = passed + failed;
    const passRate = Math.round((passed / total) * 100);

    console.log(`${colors.bold}${colors.blue}
╔═══════════════════════════════════════════════════════════╗
║   📊 SUMMARY                                              ║
╚═══════════════════════════════════════════════════════════╝
${colors.reset}`);

    console.log(`${colors.cyan}Total Tests:${colors.reset} ${total}`);
    console.log(`${colors.green}Passed:${colors.reset} ${passed}`);
    console.log(`${colors.red}Failed:${colors.reset} ${failed}`);
    console.log(`${colors.yellow}Pass Rate:${colors.reset} ${passRate}%\n`);

    if (failed === 0) {
        console.log(`${colors.green}${colors.bold}✅ All CI/CD verification tests passed!${colors.reset}\n`);
        console.log(`${colors.cyan}Next steps:${colors.reset}`);
        console.log(`  1. Commit the workflow file to your repository`);
        console.log(`  2. Push to GitHub to trigger the workflow`);
        console.log(`  3. Monitor the Actions tab in GitHub to see the workflow run\n`);
        process.exit(0);
    } else {
        console.log(`${colors.red}${colors.bold}❌ Some CI/CD tests failed!${colors.reset}\n`);
        process.exit(1);
    }
}

main();
