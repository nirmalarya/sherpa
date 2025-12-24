#!/usr/bin/env node

const http = require('http');

function httpRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const reqOptions = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port,
      path: parsedUrl.pathname + parsedUrl.search,
      method: options.method || 'GET',
      headers: options.headers || {}
    };

    const req = http.request(reqOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data
        });
      });
    });

    req.on('error', reject);
    if (options.body) {
      req.write(options.body);
    }
    req.end();
  });
}

async function debugIssues() {
  console.log('=== Debugging CORS Headers ===');
  const healthResp = await httpRequest('http://localhost:8001/health');
  console.log('All headers:', JSON.stringify(healthResp.headers, null, 2));

  console.log('\n=== Debugging Metrics Endpoint ===');
  const metricsResp = await httpRequest('http://localhost:8001/metrics');
  console.log('Status:', metricsResp.statusCode);
  console.log('Body:', metricsResp.body);

  console.log('\n=== Debugging Sessions Endpoint ===');
  const sessionsResp = await httpRequest('http://localhost:8001/api/sessions');
  console.log('Status:', sessionsResp.statusCode);
  console.log('Body snippet:', sessionsResp.body.substring(0, 500));
}

debugIssues().catch(console.error);
