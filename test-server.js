// test-server.js
const http = require('http');

const options = {
  host: 'localhost',
  port: 8080,
  path: '/',
  method: 'GET'
};

const req = http.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);
  res.setEncoding('utf8');
  res.on('data', (chunk) => {
    console.log('Received data (first 100 chars):', chunk.substring(0, 100));
    if (chunk.includes('Glitcher')) {
      console.log('SUCCESS: Server responded with Glitcher content');
    } else {
      console.log('WARNING: Response does not contain expected content');
    }
  });
  res.on('end', () => {
    console.log('Response ended');
  });
});

req.on('error', (e) => {
  console.error('Request error:', e.message);
});

req.end();