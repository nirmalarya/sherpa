#!/usr/bin/env node

const http = require('http');

function httpRequest(url) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const reqOptions = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port,
      path: parsedUrl.pathname,
      method: 'GET'
    };

    const req = http.request(reqOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          body: data
        });
      });
    });

    req.on('error', reject);
    req.end();
  });
}

async function debugMetrics() {
  const response = await httpRequest('http://localhost:8001/metrics');
  console.log('Status:', response.statusCode);
  console.log('Body:', response.body);

  const data = JSON.parse(response.body);
  console.log('\nParsed data keys:', Object.keys(data));
  console.log('data.data keys:', Object.keys(data.data || {}));
  console.log('data.data.total_sessions:', data.data?.total_sessions);
  console.log('data.data.active_sessions:', data.data?.active_sessions);
}

debugMetrics().catch(console.error);
