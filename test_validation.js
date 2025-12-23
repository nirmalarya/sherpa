// Node.js script to test request validation
const http = require('http');

const API_BASE = 'localhost';
const API_PORT = 8001;

async function makeRequest(method, path, body) {
    return new Promise((resolve, reject) => {
        const data = body ? JSON.stringify(body) : null;

        const options = {
            hostname: API_BASE,
            port: API_PORT,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data ? Buffer.byteLength(data) : 0
            }
        };

        const req = http.request(options, (res) => {
            let responseData = '';

            res.on('data', (chunk) => {
                responseData += chunk;
            });

            res.on('end', () => {
                try {
                    const parsed = JSON.parse(responseData);
                    resolve({ status: res.statusCode, data: parsed, headers: res.headers });
                } catch (e) {
                    resolve({ status: res.statusCode, data: responseData, headers: res.headers });
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        if (data) {
            req.write(data);
        }

        req.end();
    });
}

async function runTests() {
    console.log('🧪 Starting Request Validation Tests\n');
    console.log('=' .repeat(80));

    let passed = 0;
    let failed = 0;

    // Step 1: Send malformed request
    console.log('\n📤 Step 1: Send Malformed Request');
    console.log('Request: POST /api/sessions with { "total_features": "not_a_number" }');
    try {
        const result = await makeRequest('POST', '/api/sessions', {
            total_features: "not_a_number"
        });
        console.log(`Status: ${result.status}`);
        console.log(`Response: ${JSON.stringify(result.data, null, 2)}`);

        if (result.status === 400) {
            console.log('✅ PASS: Returned 400 status');
            passed++;
        } else {
            console.log(`❌ FAIL: Expected 400, got ${result.status}`);
            failed++;
        }
    } catch (error) {
        console.log(`❌ FAIL: ${error.message}`);
        failed++;
    }

    // Step 2: Verify 400 status with negative number
    console.log('\n📤 Step 2: Verify 400 Status Returned');
    console.log('Request: POST /api/sessions with { "total_features": -1 }');
    try {
        const result = await makeRequest('POST', '/api/sessions', {
            total_features: -1
        });
        console.log(`Status: ${result.status}`);

        if (result.status === 400) {
            console.log('✅ PASS: Returned 400 status for negative number');
            passed++;
        } else {
            console.log(`❌ FAIL: Expected 400, got ${result.status}`);
            failed++;
        }
    } catch (error) {
        console.log(`❌ FAIL: ${error.message}`);
        failed++;
    }

    // Step 3: Verify validation errors listed
    console.log('\n📤 Step 3: Verify Validation Errors Listed');
    console.log('Request: POST /api/sessions with invalid data');
    try {
        const result = await makeRequest('POST', '/api/sessions', {
            total_features: "invalid",
            spec_file: ""
        });
        console.log(`Status: ${result.status}`);
        console.log(`Response: ${JSON.stringify(result.data, null, 2)}`);

        const hasError = result.data.error !== undefined;
        const hasMessage = result.data.message !== undefined;
        const hasDetails = Array.isArray(result.data.details) && result.data.details.length > 0;
        const detailsValid = hasDetails && result.data.details.every(d =>
            d.field !== undefined && d.message !== undefined && d.type !== undefined
        );

        console.log(`Has "error": ${hasError}`);
        console.log(`Has "message": ${hasMessage}`);
        console.log(`Has "details" array: ${hasDetails}`);
        console.log(`Details have field/message/type: ${detailsValid}`);

        if (hasError && hasMessage && hasDetails && detailsValid) {
            console.log('✅ PASS: Validation errors properly listed');
            passed++;
        } else {
            console.log('❌ FAIL: Validation error format incorrect');
            failed++;
        }
    } catch (error) {
        console.log(`❌ FAIL: ${error.message}`);
        failed++;
    }

    // Step 4: Send request with extra fields
    console.log('\n📤 Step 4: Send Request with Extra Fields');
    console.log('Request: POST /api/sessions with extra_field');
    try {
        const result = await makeRequest('POST', '/api/sessions', {
            total_features: 5,
            extra_field: "should_reject",
            another_extra: true
        });
        console.log(`Status: ${result.status}`);
        console.log(`Response: ${JSON.stringify(result.data, null, 2)}`);

        if (result.status === 400) {
            console.log('✅ PASS: Extra fields rejected with 400 status');
            passed++;
        } else {
            console.log(`❌ FAIL: Expected 400, got ${result.status}`);
            failed++;
        }
    } catch (error) {
        console.log(`❌ FAIL: ${error.message}`);
        failed++;
    }

    // Step 5: Verify extra fields error message
    console.log('\n📤 Step 5: Verify Extra Fields Rejected');
    console.log('Request: POST /api/sessions with forbidden_field');
    try {
        const result = await makeRequest('POST', '/api/sessions', {
            total_features: 10,
            forbidden_field: "test"
        });
        console.log(`Status: ${result.status}`);
        console.log(`Response: ${JSON.stringify(result.data, null, 2)}`);

        const errorText = JSON.stringify(result.data).toLowerCase();
        const mentionsExtra = errorText.includes('extra') ||
                             errorText.includes('forbidden') ||
                             errorText.includes('not permitted') ||
                             errorText.includes('additional');

        console.log(`Error mentions extra/forbidden fields: ${mentionsExtra}`);

        if (result.status === 400 && mentionsExtra) {
            console.log('✅ PASS: Extra fields error clearly indicated');
            passed++;
        } else {
            console.log('❌ FAIL: Extra fields error not clear');
            failed++;
        }
    } catch (error) {
        console.log(`❌ FAIL: ${error.message}`);
        failed++;
    }

    // Step 6: Send valid request
    console.log('\n📤 Step 6: Send Valid Request');
    console.log('Request: POST /api/sessions with valid data');
    try {
        const result = await makeRequest('POST', '/api/sessions', {
            spec_file: "validation_test.txt",
            total_features: 10,
            work_item_id: "WI-123",
            git_branch: "feature/validation-test"
        });
        console.log(`Status: ${result.status}`);
        console.log(`Response: ${JSON.stringify(result.data, null, 2)}`);

        if (result.status === 201) {
            console.log('✅ PASS: Valid request accepted with 201 status');
            passed++;
        } else {
            console.log(`❌ FAIL: Expected 201, got ${result.status}`);
            failed++;
        }
    } catch (error) {
        console.log(`❌ FAIL: ${error.message}`);
        failed++;
    }

    // Step 7: Verify valid request accepted
    console.log('\n📤 Step 7: Verify Valid Request Accepted');
    console.log('Request: POST /api/sessions with valid data');
    try {
        const result = await makeRequest('POST', '/api/sessions', {
            spec_file: "final_validation_test.txt",
            total_features: 25
        });
        console.log(`Status: ${result.status}`);
        console.log(`Response: ${JSON.stringify(result.data, null, 2)}`);

        const hasId = result.data.id !== undefined;
        const hasStatus = result.data.status === "created";
        const hasTimestamp = result.data.timestamp !== undefined;
        const noErrors = result.data.error === undefined;

        console.log(`Has "id": ${hasId}`);
        console.log(`Has "status" = "created": ${hasStatus}`);
        console.log(`Has "timestamp": ${hasTimestamp}`);
        console.log(`No errors: ${noErrors}`);

        if (result.status === 201 && hasId && hasStatus && hasTimestamp && noErrors) {
            console.log('✅ PASS: Valid request properly processed');
            passed++;
        } else {
            console.log('❌ FAIL: Valid request not properly processed');
            failed++;
        }
    } catch (error) {
        console.log(`❌ FAIL: ${error.message}`);
        failed++;
    }

    // Final summary
    console.log('\n' + '='.repeat(80));
    console.log('🎯 FINAL RESULTS');
    console.log('='.repeat(80));
    console.log(`✅ Passed: ${passed}/7`);
    console.log(`❌ Failed: ${failed}/7`);
    console.log(`📊 Success Rate: ${Math.round(passed/7 * 100)}%`);

    if (passed === 7) {
        console.log('\n🎉 ALL TESTS PASSED! Request validation is working correctly!');
        process.exit(0);
    } else {
        console.log('\n⚠️  Some tests failed. Please review the output above.');
        process.exit(1);
    }
}

runTests().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
