#!/usr/bin/env node
/**
 * Test Rate Limiting Feature
 * Tests all 6 steps from feature_list.json
 */

const API_URL = "http://localhost:8001";

function printSection(title) {
    console.log("\n" + "=".repeat(60));
    console.log(`  ${title}`);
    console.log("=".repeat(60));
}

async function testStep1() {
    printSection("Step 1: Make Rapid API Calls");

    try {
        const promises = [];
        for (let i = 0; i < 10; i++) {
            promises.push(fetch(`${API_URL}/health`));
        }

        const responses = await Promise.all(promises);
        const statuses = responses.map(r => r.status);
        const allSuccess = statuses.every(s => s === 200);

        if (allSuccess) {
            console.log("✅ PASS - Step 1");
            console.log("Made 10 rapid API calls");
            console.log("All responses: 200 OK");
            return true;
        } else {
            console.log("❌ FAIL - Step 1");
            console.log(`Unexpected status codes: ${statuses}`);
            return false;
        }
    } catch (error) {
        console.log(`❌ FAIL - Step 1: ${error.message}`);
        return false;
    }
}

async function testStep2() {
    printSection("Step 2: Verify Rate Limit Applied");

    try {
        const response = await fetch(`${API_URL}/health`);

        const limit = response.headers.get('X-RateLimit-Limit');
        const remaining = response.headers.get('X-RateLimit-Remaining');
        const reset = response.headers.get('X-RateLimit-Reset');

        if (limit && remaining !== null && reset) {
            console.log("✅ PASS - Step 2");
            console.log("Rate limit is being tracked\n");
            console.log("Rate Limit Headers:");
            console.log(`  X-RateLimit-Limit: ${limit}`);
            console.log(`  X-RateLimit-Remaining: ${remaining}`);
            console.log(`  X-RateLimit-Reset: ${reset}`);
            return true;
        } else {
            console.log("❌ FAIL - Step 2");
            console.log("Missing rate limit headers");
            console.log(`Limit: ${limit}, Remaining: ${remaining}, Reset: ${reset}`);
            return false;
        }
    } catch (error) {
        console.log(`❌ FAIL - Step 2: ${error.message}`);
        return false;
    }
}

async function testStep3() {
    printSection("Step 3: Verify 429 Status Returned");

    try {
        console.log("Making 101 requests to exceed the limit...");
        const responses = [];

        for (let i = 0; i < 101; i++) {
            const response = await fetch(`${API_URL}/health`);
            responses.push(response);

            if ((i + 1) % 20 === 0) {
                console.log(`  Progress: ${i + 1}/101 requests`);
            }
        }

        const has429 = responses.some(r => r.status === 429);
        const response429 = responses.reverse().find(r => r.status === 429);

        if (has429 && response429) {
            const errorData = await response429.json();
            console.log("✅ PASS - Step 3");
            console.log("Made 101 requests");
            console.log("Rate limit exceeded - received 429 status\n");
            console.log("429 Response:");
            console.log(JSON.stringify(errorData, null, 2));
            return true;
        } else {
            console.log("❌ FAIL - Step 3");
            console.log("Expected 429 status but didn't receive it");
            const statuses = responses.map(r => r.status);
            console.log(`Response statuses: ${statuses}`);
            return false;
        }
    } catch (error) {
        console.log(`❌ FAIL - Step 3: ${error.message}`);
        return false;
    }
}

async function testStep4() {
    printSection("Step 4: Verify Rate Limit Headers Present");

    try {
        // Make enough requests to trigger rate limit
        for (let i = 0; i < 100; i++) {
            await fetch(`${API_URL}/health`);
        }

        // Make one more to get 429
        const response = await fetch(`${API_URL}/health`);

        if (response.status === 429) {
            const limit = response.headers.get('X-RateLimit-Limit');
            const remaining = response.headers.get('X-RateLimit-Remaining');
            const reset = response.headers.get('X-RateLimit-Reset');
            const retryAfter = response.headers.get('Retry-After');

            const hasAllHeaders = limit && remaining !== null && reset && retryAfter;

            if (hasAllHeaders) {
                console.log("✅ PASS - Step 4");
                console.log("All rate limit headers present in 429 response:\n");
                console.log(`  X-RateLimit-Limit: ${limit}`);
                console.log(`  X-RateLimit-Remaining: ${remaining}`);
                console.log(`  X-RateLimit-Reset: ${reset}`);
                console.log(`  Retry-After: ${retryAfter} seconds`);
                return true;
            } else {
                console.log("❌ FAIL - Step 4");
                console.log("Missing headers in 429 response");
                console.log(`Limit: ${limit}, Remaining: ${remaining}, Reset: ${reset}, Retry-After: ${retryAfter}`);
                return false;
            }
        } else {
            console.log("❌ FAIL - Step 4");
            console.log(`Expected 429 status but got ${response.status}`);
            return false;
        }
    } catch (error) {
        console.log(`❌ FAIL - Step 4: ${error.message}`);
        return false;
    }
}

async function testStep5() {
    printSection("Step 5: Wait and Retry");

    try {
        // First, trigger rate limit
        for (let i = 0; i < 100; i++) {
            await fetch(`${API_URL}/health`);
        }

        const response429 = await fetch(`${API_URL}/health`);

        if (response429.status === 429) {
            const retryAfter = parseInt(response429.headers.get('Retry-After') || '60');
            console.log("Rate limit hit!");
            console.log(`Waiting ${retryAfter} seconds for window to reset...`);

            // Wait with countdown
            for (let i = retryAfter; i > 0; i -= 10) {
                console.log(`  Time remaining: ${i} seconds`);
                await new Promise(resolve => setTimeout(resolve, Math.min(10, i) * 1000));
            }

            // Try again after waiting
            const retryResponse = await fetch(`${API_URL}/health`);

            if (retryResponse.status === 200) {
                console.log("✅ PASS - Step 5");
                console.log(`Waited ${retryAfter} seconds`);
                console.log(`Retry successful - status: ${retryResponse.status}`);
                return true;
            } else {
                console.log("❌ FAIL - Step 5");
                console.log(`After waiting, still got status ${retryResponse.status}`);
                return false;
            }
        } else {
            console.log("❌ FAIL - Step 5");
            console.log("Could not trigger rate limit initially");
            return false;
        }
    } catch (error) {
        console.log(`❌ FAIL - Step 5: ${error.message}`);
        return false;
    }
}

async function testStep6() {
    printSection("Step 6: Verify Access Restored");

    try {
        const promises = [];
        for (let i = 0; i < 5; i++) {
            promises.push(fetch(`${API_URL}/health`));
        }

        const responses = await Promise.all(promises);
        const allSuccess = responses.every(r => r.status === 200);
        const firstResponse = responses[0];
        const remaining = firstResponse.headers.get('X-RateLimit-Remaining');

        if (allSuccess && remaining) {
            console.log("✅ PASS - Step 6");
            console.log("Access fully restored!");
            console.log("Made 5 successful requests");
            console.log("All responses: 200 OK");
            console.log(`Remaining requests: ${remaining}`);
            return true;
        } else {
            console.log("❌ FAIL - Step 6");
            console.log("Access not fully restored");
            return false;
        }
    } catch (error) {
        console.log(`❌ FAIL - Step 6: ${error.message}`);
        return false;
    }
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
    console.log("\n" + "🛡️ ".repeat(20));
    console.log("     RATE LIMITING TEST SUITE - Session 78");
    console.log("🛡️ ".repeat(20));

    const results = {};

    // Run all tests
    results.step1 = await testStep1();
    await sleep(1000);

    results.step2 = await testStep2();
    await sleep(1000);

    results.step3 = await testStep3();
    await sleep(2000);

    results.step4 = await testStep4();
    await sleep(2000);

    results.step5 = await testStep5();
    await sleep(2000);

    results.step6 = await testStep6();

    // Summary
    printSection("TEST SUMMARY");
    const totalTests = Object.keys(results).length;
    const passedTests = Object.values(results).filter(v => v === true).length;

    console.log(`Total Tests: ${totalTests}`);
    console.log(`Passed: ${passedTests}`);
    console.log(`Failed: ${totalTests - passedTests}`);
    console.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);

    if (passedTests === totalTests) {
        console.log("\n🎉 All tests passed! Rate limiting feature is working correctly!");
        process.exit(0);
    } else {
        console.log("\n⚠️  Some tests failed. Please review the results above.");
        process.exit(1);
    }
}

main().catch(error => {
    console.error("Fatal error:", error);
    process.exit(1);
});
