const http = require('http');
const httpProxy = require('http-proxy');
const fs = require('fs');
const path = require('path');

// Create proxy server
const proxy = httpProxy.createProxyServer({});

// MIME types
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject'
};

// Error handler for proxy
proxy.on('error', (err, req, res) => {
    console.error('Proxy error:', err);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
        error: 'Proxy error',
        message: err.message
    }));
});

// Create HTTP server
const server = http.createServer((req, res) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);

    // Handle API requests - proxy to Odoo
    if (req.url.startsWith('/api/') || req.url.startsWith('/chatbot/')) {
        // Add CORS headers
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept');

        // Handle preflight
        if (req.method === 'OPTIONS') {
            res.writeHead(200);
            res.end();
            return;
        }

        // Proxy to Odoo backend
        proxy.web(req, res, {
            target: 'http://localhost:8069',
            changeOrigin: true
        });
    } else {
        // Serve static files — strip query string
        const parsedUrl = new URL(req.url, 'http://localhost');
        let filePath = '.' + parsedUrl.pathname;
        if (filePath === './') {
            filePath = './index.html';
        }

        const extname = String(path.extname(filePath)).toLowerCase();
        const contentType = mimeTypes[extname] || 'application/octet-stream';

        fs.readFile(filePath, (error, content) => {
            if (error) {
                if (error.code === 'ENOENT') {
                    fs.readFile('./404.html', (err404, content404) => {
                        res.writeHead(404, { 'Content-Type': 'text/html' });
                        res.end(content404 || '404 Not Found', 'utf-8');
                    });
                } else {
                    res.writeHead(500);
                    res.end('Server Error: ' + error.code);
                }
            } else {
                res.writeHead(200, { 'Content-Type': contentType });
                res.end(content, 'utf-8');
            }
        });
    }
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`\n✓ Proxy server running at http://localhost:${PORT}/`);
    console.log(`✓ Static files served from: ${__dirname}`);
    console.log(`✓ API requests proxied to: http://localhost:8069`);
    console.log(`\nPress Ctrl+C to stop the server\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\nShutting down proxy server...');
    server.close(() => {
        console.log('Proxy server stopped');
        process.exit(0);
    });
});
