// server.js - Glitcher Proxy Server
const express = require('express');
const http = require('http');
const httpProxy = require('http-proxy');
const path = require('path');
const fs = require('fs');

const app = express();
const proxy = httpProxy.createProxyServer({});

// Serve static files from the current directory
app.use(express.static(path.join(__dirname)));

// Create HTTP server
const server = http.createServer(app);

// Handle proxy requests
app.all('/proxy/*', (req, res) => {
    // Extract the target URL from the request path
    const targetUrl = req.url.replace('/proxy/', '');
    
    // Parse the target URL to get protocol, host, and path
    try {
        const parsedUrl = new URL(targetUrl);
        const target = `${parsedUrl.protocol}//${parsedUrl.host}`;
        
        // Proxy the request to the target
        proxy.web(req, res, { target: target, changeOrigin: true }, (err) => {
            console.error('Proxy error:', err);
            res.status(500).send('Proxy error');
        });
    } catch (error) {
        console.error('Invalid URL:', error);
        res.status(400).send('Invalid URL format');
    }
});

// Handle requests to /glitch or the root path by serving the main application
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Handle requests to /glitch specifically
app.get('/glitch', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Handle all other routes by serving the main application
app.get('*', (req, res) => {
    // If the route is for the Glitcher tool, serve the main app
    if (req.url.startsWith('/glitch') || req.url === '/') {
        res.sendFile(path.join(__dirname, 'index.html'));
    } else {
        // For other routes, we'll proxy them if they're meant to be proxied
        res.redirect('/');
    }
});

// Handle WebSocket upgrades for real-time communication
server.on('upgrade', (req, socket, head) => {
    // This would handle WebSocket connections in a real implementation
    console.log('WebSocket upgrade request:', req.url);
});

const PORT = process.env.PORT || 8080;

server.listen(PORT, () => {
    console.log(`Glitcher server running on http://localhost:${PORT}`);
    console.log(`Access Glitcher at http://localhost:${PORT} or configure your browser to use this as a proxy`);
    console.log(`To access via http://glitch, add '127.0.0.1 glitch' to your hosts file`);
    console.log(`Hosts file location: C:\\Windows\\System32\\drivers\\etc\\hosts (on Windows)`);
    console.log(`To proxy requests, use the format: http://localhost:${PORT}/proxy/https://example.com`);
});

// Handle proxy errors
proxy.on('error', (err, req, res) => {
    console.error('Proxy error:', err);
    if (!res.headersSent) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Proxy error');
    }
});