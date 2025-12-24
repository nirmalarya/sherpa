#!/usr/bin/env node

/**
 * Session 82 Verification Script
 * Tests core features to ensure no regressions from previous session
 */

const http = require('http');

const API_BASE = 'localhost';
const API_PORT = 8001;

let testsPassed = 0;
let testsFailed = 0;

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

async function testHealthEndpoint() {
    console.log('\n🔍 Test 1: Health Endpoint (Session 81 Feature)');
    console.log('================================================');

    try {
        const response = await makeRequest('/health');

        console.log(`✓ Status Code: ${response.statusCode}`);

        if (response.statusCode !== 200) {
            console.log('✗ FAIL: Expected status 200');
            testsFailed++;
            return false;
        }

        const data = response.data;

        // Verify structure
        const checks = [
            ['Has success field', data.success !== undefined],
            ['Has data field', data.data !== undefined],
            ['Has status field', data.data?.status !== undefined],
            ['Status is ok', data.data?.status === 'ok'],
            ['Has version field', data.data?.version !== undefined],
            ['Has dependencies', data.data?.dependencies !== undefined],
            ['Has database dependency', data.data?.dependencies?.database !== undefined],
            ['Database status is ok', data.data?.dependencies?.database?.status === 'ok']
        ];

        let allPass = true;
        checks.forEach(([name, passed]) => {
            if (passed) {
                console.log(`✓ ${name}`);
            } else {
                console.log(`✗ ${name}`);
                allPass = false;
            }
        });

        if (allPass) {
            console.log('\n✅ Health endpoint test PASSED');
            testsPassed++;
            return true;
        } else {
            console.log('\n❌ Health endpoint test FAILED');
            testsFailed++;
            return false;
        }

    } catch (error) {
        console.log(`✗ FAIL: ${error.message}`);
        console.log('\n❌ Health endpoint test FAILED');
        testsFailed++;
        return false;
    }
}

async function testHomepageAPI() {
    console.log('\n🔍 Test 2: Homepage API (/api/sessions)');
    console.log('========================================');

    try {
        const response = await makeRequest('/api/sessions');

        console.log(`✓ Status Code: ${response.statusCode}`);

        if (response.statusCode !== 200) {
            console.log('✗ FAIL: Expected status 200');
            testsFailed++;
            return false;
        }

        const data = response.data;

        // Verify structure (with pagination support)
        const checks = [
            ['Has success field', data.success !== undefined],
            ['Has data field', data.data !== undefined],
            ['Data has sessions field', data.data?.sessions !== undefined],
            ['Sessions is array', Array.isArray(data.data?.sessions)],
            ['Data has total field', data.data?.total !== undefined],
            ['Has message field', data.message !== undefined],
            ['Has timestamp field', data.timestamp !== undefined]
        ];

        let allPass = true;
        checks.forEach(([name, passed]) => {
            if (passed) {
                console.log(`✓ ${name}`);
            } else {
                console.log(`✗ ${name}`);
                allPass = false;
            }
        });

        console.log(`✓ Sessions count: ${data.data?.sessions?.length || 0}`);

        if (allPass) {
            console.log('\n✅ Homepage API test PASSED');
            testsPassed++;
            return true;
        } else {
            console.log('\n❌ Homepage API test FAILED');
            testsFailed++;
            return false;
        }

    } catch (error) {
        console.log(`✗ FAIL: ${error.message}`);
        console.log('\n❌ Homepage API test FAILED');
        testsFailed++;
        return false;
    }
}

async function runAllTests() {
    console.log('🏔️  SHERPA V1 - Session 82 Verification');
    console.log('========================================');
    console.log('Testing core features for regressions...\n');

    await testHealthEndpoint();
    await testHomepageAPI();

    console.log('\n📊 VERIFICATION SUMMARY');
    console.log('=======================');
    console.log(`Tests Passed: ${testsPassed}`);
    console.log(`Tests Failed: ${testsFailed}`);
    console.log(`Total Tests: ${testsPassed + testsFailed}`);

    if (testsFailed === 0) {
        console.log('\n🎉 ALL VERIFICATION TESTS PASSED!');
        console.log('No regressions detected. Safe to implement new features.\n');
        process.exit(0);
    } else {
        console.log('\n⚠️  REGRESSIONS DETECTED!');
        console.log('Fix failing tests before implementing new features.\n');
        process.exit(1);
    }
}

// Run tests
runAllTests().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
