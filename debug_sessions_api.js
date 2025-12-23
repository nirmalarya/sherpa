#!/usr/bin/env node

const http = require('http');

function makeRequest(path) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: 8001,
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

        req.on('error', reject);
        req.setTimeout(5000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        req.end();
    });
}

async function debug() {
    console.log('Debugging /api/sessions endpoint...\n');

    try {
        const response = await makeRequest('/api/sessions');
        console.log('Status Code:', response.statusCode);
        console.log('\nFull Response:');
        console.log(JSON.stringify(response.data, null, 2));
        console.log('\nData Type:', typeof response.data);
        console.log('Data.data Type:', typeof response.data?.data);
        console.log('Is Data.data an Array?:', Array.isArray(response.data?.data));
        console.log('Data.data value:', response.data?.data);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

debug();
