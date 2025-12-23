#!/usr/bin/env node

/**
 * Metrics Endpoint Test - Session 82
 * Tests all 5 steps for the /metrics endpoint
 */

const http = require('http');

const API_BASE = 'localhost';
const API_PORT = 8001;

let testsPassed = 0;
let testsFailed = 0;
let metricsData = null;

function makeRequest(path) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: API_BASE,
            port: API_PORT,
            path: path,
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        };

        const req = http.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                try {
                    const parsed = JSON.parse(data);
                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        data: parsed
                    });
                } catch (e) {
                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        data: data
                    });
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.setTimeout(5000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        req.end();
    });
}

async function testStep1() {
    console.log('\n📊 Step 1: Call GET /metrics');
    console.log('================================');

    try {
        const response = await makeRequest('/metrics');

        console.log(`✓ Status Code: ${response.statusCode}`);

        if (response.statusCode !== 200) {
            console.log('✗ FAIL: Expected status 200');
            testsFailed++;
            return false;
        }

        const data = response.data;

        if (!data.success || !data.data) {
            console.log('✗ FAIL: Invalid response structure');
            testsFailed++;
            return false;
        }

        metricsData = data.data;
        console.log(`✓ Response structure valid`);
        console.log(`✓ Has success field: ${data.success}`);
        console.log(`✓ Has data field: Yes`);
        console.log(`✓ Has message field: ${data.message}`);

        console.log('\n✅ Step 1 PASSED');
        testsPassed++;
        return true;

    } catch (error) {
        console.log(`✗ FAIL: ${error.message}`);
        console.log('\n❌ Step 1 FAILED');
        testsFailed++;
        return false;
    }
}

async function testStep2() {
    console.log('\n📊 Step 2: Verify response includes request count');
    console.log('==================================================');

    if (!metricsData) {
        console.log('✗ FAIL: Must run Step 1 first');
        testsFailed++;
        return false;
    }

    const hasRequestCount = metricsData.request_count !== undefined;
    const requestCount = metricsData.request_count;
    const isNumber = typeof requestCount === 'number';
    const isValid = isNumber && requestCount >= 0;

    console.log(`✓ Has request_count field: ${hasRequestCount}`);
    console.log(`✓ Type: ${typeof requestCount}`);
    console.log(`✓ Value: ${requestCount}`);
    console.log(`✓ Valid (number >= 0): ${isValid}`);

    if (hasRequestCount && isValid) {
        console.log('\n✅ Step 2 PASSED');
        testsPassed++;
        return true;
    } else {
        console.log('\n❌ Step 2 FAILED');
        testsFailed++;
        return false;
    }
}

async function testStep3() {
    console.log('\n📊 Step 3: Verify response includes active sessions');
    console.log('====================================================');

    if (!metricsData) {
        console.log('✗ FAIL: Must run Step 1 first');
        testsFailed++;
        return false;
    }

    const hasActiveSessions = metricsData.active_sessions !== undefined;
    const activeSessions = metricsData.active_sessions;
    const isNumber = typeof activeSessions === 'number';
    const isValid = isNumber && activeSessions >= 0;

    console.log(`✓ Has active_sessions field: ${hasActiveSessions}`);
    console.log(`✓ Type: ${typeof activeSessions}`);
    console.log(`✓ Value: ${activeSessions}`);
    console.log(`✓ Valid (number >= 0): ${isValid}`);

    if (hasActiveSessions && isValid) {
        console.log('\n✅ Step 3 PASSED');
        testsPassed++;
        return true;
    } else {
        console.log('\n❌ Step 3 FAILED');
        testsFailed++;
        return false;
    }
}

async function testStep4() {
    console.log('\n📊 Step 4: Verify response includes error rate');
    console.log('===============================================');

    if (!metricsData) {
        console.log('✗ FAIL: Must run Step 1 first');
        testsFailed++;
        return false;
    }

    const hasErrorRate = metricsData.error_rate !== undefined;
    const hasErrorCount = metricsData.error_count !== undefined;
    const errorRate = metricsData.error_rate;
    const errorCount = metricsData.error_count;
    const rateIsNumber = typeof errorRate === 'number';
    const countIsNumber = typeof errorCount === 'number';
    const isValid = rateIsNumber && countIsNumber && errorRate >= 0 && errorCount >= 0;

    console.log(`✓ Has error_rate field: ${hasErrorRate}`);
    console.log(`✓ Has error_count field: ${hasErrorCount}`);
    console.log(`✓ Error rate type: ${typeof errorRate}`);
    console.log(`✓ Error count type: ${typeof errorCount}`);
    console.log(`✓ Error rate value: ${errorRate}%`);
    console.log(`✓ Error count value: ${errorCount}`);
    console.log(`✓ Valid: ${isValid}`);

    if (hasErrorRate && hasErrorCount && isValid) {
        console.log('\n✅ Step 4 PASSED');
        testsPassed++;
        return true;
    } else {
        console.log('\n❌ Step 4 FAILED');
        testsFailed++;
        return false;
    }
}

async function testStep5() {
    console.log('\n📊 Step 5: Verify Prometheus format');
    console.log('====================================');

    if (!metricsData) {
        console.log('✗ FAIL: Must run Step 1 first');
        testsFailed++;
        return false;
    }

    const hasPrometheusFormat = metricsData.prometheus_format !== undefined;
    const prometheusFormat = metricsData.prometheus_format;
    const isString = typeof prometheusFormat === 'string';
    const hasContent = isString && prometheusFormat.length > 0;

    console.log(`✓ Has prometheus_format field: ${hasPrometheusFormat}`);
    console.log(`✓ Type: ${typeof prometheusFormat}`);
    console.log(`✓ Length: ${prometheusFormat?.length || 0} characters`);

    if (!hasContent) {
        console.log('\n❌ Step 5 FAILED - Prometheus format missing or empty');
        testsFailed++;
        return false;
    }

    // Verify Prometheus format structure
    const hasHelpLines = prometheusFormat.includes('# HELP');
    const hasTypeLines = prometheusFormat.includes('# TYPE');
    const hasMetricLines = prometheusFormat.includes('sherpa_');
    const hasRequestsTotal = prometheusFormat.includes('sherpa_requests_total');
    const hasActiveSessions = prometheusFormat.includes('sherpa_active_sessions');
    const hasErrorRate = prometheusFormat.includes('sherpa_error_rate');
    const hasUptimeSeconds = prometheusFormat.includes('sherpa_uptime_seconds');

    console.log(`✓ Contains # HELP lines: ${hasHelpLines}`);
    console.log(`✓ Contains # TYPE lines: ${hasTypeLines}`);
    console.log(`✓ Contains sherpa_ metrics: ${hasMetricLines}`);
    console.log(`✓ Contains sherpa_requests_total: ${hasRequestsTotal}`);
    console.log(`✓ Contains sherpa_active_sessions: ${hasActiveSessions}`);
    console.log(`✓ Contains sherpa_error_rate: ${hasErrorRate}`);
    console.log(`✓ Contains sherpa_uptime_seconds: ${hasUptimeSeconds}`);

    // Show sample of Prometheus format
    const lines = prometheusFormat.split('\n');
    console.log('\nPrometheus Format Sample (first 15 lines):');
    console.log('==========================================');
    lines.slice(0, 15).forEach(line => {
        console.log(line);
    });

    const allChecks = hasHelpLines && hasTypeLines && hasMetricLines &&
                     hasRequestsTotal && hasActiveSessions && hasErrorRate &&
                     hasUptimeSeconds;

    if (allChecks) {
        console.log('\n✅ Step 5 PASSED - Prometheus format valid');
        testsPassed++;
        return true;
    } else {
        console.log('\n❌ Step 5 FAILED - Prometheus format incomplete');
        testsFailed++;
        return false;
    }
}

async function runAllTests() {
    console.log('🏔️  SHERPA V1 - Metrics Endpoint Test (Session 82)');
    console.log('==================================================');
    console.log('Testing /metrics endpoint with all 5 steps...\n');

    await testStep1();
    await testStep2();
    await testStep3();
    await testStep4();
    await testStep5();

    console.log('\n\n📊 TEST SUMMARY');
    console.log('================');
    console.log(`Tests Passed: ${testsPassed}`);
    console.log(`Tests Failed: ${testsFailed}`);
    console.log(`Total Tests: ${testsPassed + testsFailed}`);

    if (testsFailed === 0) {
        console.log('\n🎉 ALL TESTS PASSED!');
        console.log('Metrics endpoint is fully functional and ready for production.');
        console.log('\nFeature can be marked as "passes": true in feature_list.json\n');
        process.exit(0);
    } else {
        console.log('\n⚠️  SOME TESTS FAILED!');
        console.log('Review failed tests above and fix issues.\n');
        process.exit(1);
    }
}

// Run tests
runAllTests().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
