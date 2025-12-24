#!/usr/bin/env node

/**
 * SHERPA V1 - Core Features Verification Script
 *
 * This script verifies that core features still work before implementing new ones.
 * Tests backend health, CORS, frontend accessibility, and API endpoints.
 */

const BACKEND_URL = 'http://localhost:8001';
const FRONTEND_URL = 'http://localhost:3003';

// ANSI color codes for pretty output
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

async function fetchWithTimeout(url, options = {}, timeout = 5000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        throw error;
    }
}

async function runTest(name, description, testFn) {
    process.stdout.write(`${colors.cyan}⏳ Test: ${name}${colors.reset}\n`);
    process.stdout.write(`   ${description}\n`);

    try {
        const result = await testFn();
        passed++;
        console.log(`${colors.green}✅ PASS${colors.reset}: ${result}\n`);
        return true;
    } catch (error) {
        failed++;
        console.log(`${colors.red}❌ FAIL${colors.reset}: ${error.message}\n`);
        return false;
    }
}

async function main() {
    console.log(`${colors.bold}${colors.blue}
╔═══════════════════════════════════════════════════════════╗
║   🏔️  SHERPA V1 - Core Features Verification            ║
║   Verifying critical features before implementing new     ║
╚═══════════════════════════════════════════════════════════╝
${colors.reset}\n`);

    // Test 1: Backend Health Check
    await runTest(
        'Backend Health Check',
        'Verify backend server responds to /health endpoint',
        async () => {
            const response = await fetchWithTimeout(`${BACKEND_URL}/health`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            return `Backend healthy: ${JSON.stringify(data)}`;
        }
    );

    // Test 2: Backend CORS Configuration
    // Note: Node.js fetch doesn't trigger CORS preflight, so we test with OPTIONS request
    await runTest(
        'Backend CORS Configuration',
        'Verify CORS headers are configured (OPTIONS preflight)',
        async () => {
            const response = await fetchWithTimeout(`${BACKEND_URL}/health`, {
                method: 'OPTIONS',
                headers: {
                    'Origin': 'http://localhost:3003',
                    'Access-Control-Request-Method': 'GET'
                }
            });
            const corsHeader = response.headers.get('access-control-allow-origin');
            if (!corsHeader) {
                // If OPTIONS doesn't work, check if server has wildcard CORS
                const getResponse = await fetchWithTimeout(`${BACKEND_URL}/health`);
                const getCors = getResponse.headers.get('access-control-allow-origin');
                if (getCors) {
                    return `CORS configured (from GET): ${getCors}`;
                }
                throw new Error('No CORS header found in OPTIONS or GET');
            }
            return `CORS configured (from OPTIONS): ${corsHeader}`;
        }
    );

    // Test 3: Frontend Accessibility
    await runTest(
        'Frontend Accessibility',
        'Verify frontend is accessible and has root element',
        async () => {
            const response = await fetchWithTimeout(FRONTEND_URL);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const text = await response.text();
            if (!text.includes('<div id="root"') && !text.includes('<div id=root')) {
                throw new Error('Frontend HTML does not contain root element');
            }
            return 'Frontend accessible with React root element';
        }
    );

    // Test 4: API Sessions Endpoint
    await runTest(
        'API Sessions Endpoint',
        'Verify /api/sessions endpoint exists and returns data',
        async () => {
            const response = await fetchWithTimeout(`${BACKEND_URL}/api/sessions`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            const count = Array.isArray(data) ? data.length : 'unknown';
            return `Sessions endpoint working, returned ${count} sessions`;
        }
    );

    // Test 5: API Snippets Endpoint
    await runTest(
        'API Snippets Endpoint',
        'Verify /api/snippets endpoint exists and returns data',
        async () => {
            const response = await fetchWithTimeout(`${BACKEND_URL}/api/snippets`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            const count = Array.isArray(data) ? data.length : 'unknown';
            return `Snippets endpoint working, returned ${count} snippets`;
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
        console.log(`${colors.green}${colors.bold}✅ All core features verified! Safe to proceed with new implementation.${colors.reset}\n`);
        process.exit(0);
    } else {
        console.log(`${colors.red}${colors.bold}❌ Some core features failed! Fix issues before proceeding.${colors.reset}\n`);
        process.exit(1);
    }
}

main().catch(error => {
    console.error(`${colors.red}Fatal error:${colors.reset}`, error);
    process.exit(1);
});
