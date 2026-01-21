// Glitcher - Professional Web Security Testing Platform
class GlitcherApp {
    constructor() {
        this.currentPanel = 'dashboard-panel';
        this.requests = [];
        this.vulnerabilities = [];
        this.targets = [];
        this.isIntercepting = false;
        this.requestCounter = 0;
        this.vulnCounter = 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startSimulation();
    }
    
    setupEventListeners() {
        // Navigation buttons
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const panelId = e.target.id.replace('-btn', '-panel');
                this.switchPanel(panelId);
            });
        });
        
        // Proxy controls
        document.getElementById('toggle-proxy').addEventListener('click', () => {
            this.toggleProxy();
        });
        
        document.getElementById('clear-history').addEventListener('click', () => {
            this.clearHistory();
        });
        
        // Intruder controls
        document.getElementById('start-attack').addEventListener('click', () => {
            this.startIntruderAttack();
        });
        
        document.getElementById('clear-attack').addEventListener('click', () => {
            this.clearAttack();
        });
        
        // Repeater controls
        document.getElementById('send-request').addEventListener('click', () => {
            this.sendRepeaterRequest();
        });
        
        document.getElementById('reset-request').addEventListener('click', () => {
            this.resetRepeaterRequest();
        });
        
        // Target controls
        document.getElementById('add-target').addEventListener('click', () => {
            this.addTarget();
        });
        
        // Listen for Enter key in target URL field
        document.getElementById('target-url').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addTarget();
            }
        });
    }
    
    switchPanel(panelId) {
        // Hide current panel
        document.getElementById(this.currentPanel).classList.remove('active');
        
        // Remove active class from all nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show new panel
        document.getElementById(panelId).classList.add('active');
        
        // Update current panel
        this.currentPanel = panelId;
        
        // Add active class to corresponding nav button
        const navBtnId = panelId.replace('-panel', '-btn');
        document.getElementById(navBtnId).classList.add('active');
    }
    
    toggleProxy() {
        this.isIntercepting = !this.isIntercepting;
        const proxyBtn = document.getElementById('toggle-proxy');
        
        if (this.isIntercepting) {
            proxyBtn.textContent = 'Intercept: ON';
            proxyBtn.classList.add('intercept-on');
            this.logActivity('Proxy interception enabled');
        } else {
            proxyBtn.textContent = 'Intercept: OFF';
            proxyBtn.classList.remove('intercept-on');
            this.logActivity('Proxy interception disabled');
        }
    }
    
    clearHistory() {
        this.requests = [];
        document.getElementById('history-body').innerHTML = '';
        this.updateDashboardStats();
        this.logActivity('HTTP history cleared');
    }
    
    simulateRequest() {
        const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];
        const domains = ['example.com', 'test.com', 'demo.org', 'sample.net', 'site.edu'];
        const paths = ['/login', '/api/users', '/admin', '/dashboard', '/profile', '/api/data', '/auth', '/upload'];
        const statuses = [200, 201, 400, 401, 403, 404, 500];
        
        const method = methods[Math.floor(Math.random() * methods.length)];
        const domain = domains[Math.floor(Math.random() * domains.length)];
        const path = paths[Math.floor(Math.random() * paths.length)];
        const status = statuses[Math.floor(Math.random() * statuses.length)];
        const length = Math.floor(Math.random() * 5000) + 100;
        const time = (Math.random() * 1000).toFixed(2);
        
        const request = {
            id: ++this.requestCounter,
            method: method,
            url: `https://${domain}${path}`,
            status: status,
            length: length,
            time: time,
            timestamp: new Date().toISOString()
        };
        
        this.requests.push(request);
        this.addRequestToHistory(request);
        this.updateDashboardStats();
        
        // Simulate potential vulnerabilities
        if (method === 'POST' && path.includes('login')) {
            this.detectVulnerability(request);
        }
        
        return request;
    }
    
    addRequestToHistory(request) {
        const historyBody = document.getElementById('history-body');
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${request.id}</td>
            <td>${request.method}</td>
            <td>${request.url}</td>
            <td>${request.status}</td>
            <td>${request.length}</td>
            <td>${request.time}ms</td>
            <td>
                <button onclick="glitcher.sendToRepeater(${request.id})" class="control-btn" style="padding: 0.2rem 0.5rem; font-size: 0.8rem;">Repeater</button>
                <button onclick="glitcher.sendToIntruder(${request.id})" class="control-btn" style="padding: 0.2rem 0.5rem; font-size: 0.8rem;">Intruder</button>
            </td>
        `;
        
        historyBody.prepend(row);
    }
    
    detectVulnerability(request) {
        // Simple simulation of vulnerability detection
        const vulnTypes = ['SQL Injection', 'XSS', 'CSRF', 'IDOR', 'SSRF'];
        const vulnType = vulnTypes[Math.floor(Math.random() * vulnTypes.length)];
        
        const vulnerability = {
            id: ++this.vulnCounter,
            type: vulnType,
            severity: Math.random() > 0.5 ? 'High' : 'Medium',
            request: request,
            timestamp: new Date().toISOString()
        };
        
        this.vulnerabilities.push(vulnerability);
        this.updateDashboardStats();
        this.logActivity(`Potential ${vulnType} vulnerability detected on ${request.url}`);
    }
    
    sendToRepeater(requestId) {
        const request = this.requests.find(r => r.id === requestId);
        if (request) {
            document.getElementById('repeater-request').value = this.formatRequest(request);
            this.switchPanel('repeater-panel');
        }
    }
    
    sendToIntruder(requestId) {
        const request = this.requests.find(r => r.id === requestId);
        if (request) {
            document.getElementById('intruder-request').value = this.formatRequest(request);
            this.switchPanel('intruder-panel');
        }
    }
    
    formatRequest(request) {
        // Simple request formatting for demonstration
        return `${request.method} ${request.url} HTTP/1.1
Host: ${new URL(request.url).host}
User-Agent: Glitcher/1.0
Content-Type: application/json

{}`;
    }
    
    startIntruderAttack() {
        const attackType = document.getElementById('attack-type').value;
        const request = document.getElementById('intruder-request').value;
        const payloads = document.getElementById('payloads').value;
        
        if (!request.trim()) {
            alert('Please enter a request to attack');
            return;
        }
        
        if (!payloads.trim()) {
            alert('Please enter payloads to test');
            return;
        }
        
        this.logActivity(`Starting ${attackType} attack...`);
        
        // Simulate attack results
        const resultsDiv = document.getElementById('attack-results');
        resultsDiv.innerHTML = '<p>Attack in progress...</p>';
        
        // Simulate attack completion after delay
        setTimeout(() => {
            const payloadList = payloads.split('\n').filter(p => p.trim());
            let resultsHTML = '<h4>Attack Results:</h4><ul>';
            
            for (let i = 0; i < Math.min(5, payloadList.length); i++) {
                const payload = payloadList[i].trim();
                const status = Math.random() > 0.7 ? 'SUCCESS' : 'FAILED';
                const responseTime = (Math.random() * 1000).toFixed(2);
                
                resultsHTML += `<li><strong>${payload}</strong> - Status: ${status}, Time: ${responseTime}ms</li>`;
            }
            
            resultsHTML += '</ul>';
            resultsDiv.innerHTML = resultsHTML;
            
            this.logActivity(`${attackType} attack completed with ${payloadList.length} payloads`);
        }, 2000);
    }
    
    clearAttack() {
        document.getElementById('intruder-request').value = '';
        document.getElementById('payloads').value = '';
        document.getElementById('attack-results').innerHTML = '';
        this.logActivity('Intruder attack cleared');
    }
    
    sendRepeaterRequest() {
        const request = document.getElementById('repeater-request').value;
        
        if (!request.trim()) {
            alert('Please enter a request to send');
            return;
        }
        
        this.logActivity('Sending request via Repeater...');
        
        // Simulate response
        const response = this.simulateResponse();
        document.getElementById('repeater-response').textContent = response;
        
        this.logActivity('Response received via Repeater');
    }
    
    simulateResponse() {
        const responses = [
            'HTTP/1.1 200 OK\nContent-Type: application/json\nContent-Length: 123\n\n{"status": "success", "data": "response data"}',
            'HTTP/1.1 404 Not Found\nContent-Type: text/html\nContent-Length: 45\n\n<html><body><h1>404 Not Found</h1></body></html>',
            'HTTP/1.1 500 Internal Server Error\nContent-Type: application/json\nContent-Length: 67\n\n{"error": "Internal Server Error", "message": "Something went wrong"}',
            'HTTP/1.1 302 Found\nLocation: /login\nContent-Type: text/html\nContent-Length: 89\n\n<html><body><p>Redirecting to login page</p></body></html>'
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }
    
    resetRepeaterRequest() {
        document.getElementById('repeater-request').value = '';
        document.getElementById('repeater-response').textContent = '';
        this.logActivity('Repeater request reset');
    }
    
    addTarget() {
        const targetUrl = document.getElementById('target-url').value.trim();
        
        if (!targetUrl) {
            alert('Please enter a target URL');
            return;
        }
        
        try {
            new URL(targetUrl); // Validate URL
            
            const target = {
                id: this.targets.length + 1,
                url: targetUrl,
                added: new Date().toISOString()
            };
            
            this.targets.push(target);
            this.updateSiteMap();
            document.getElementById('target-url').value = '';
            this.updateDashboardStats();
            this.logActivity(`Target added: ${targetUrl}`);
        } catch (e) {
            alert('Please enter a valid URL (include http:// or https://)');
        }
    }
    
    updateSiteMap() {
        const siteMapDiv = document.getElementById('site-map');
        siteMapDiv.innerHTML = '<h3>Target Site Map</h3>';
        
        if (this.targets.length === 0) {
            siteMapDiv.innerHTML += '<p>No targets added yet.</p>';
            return;
        }
        
        const ul = document.createElement('ul');
        this.targets.forEach(target => {
            const li = document.createElement('li');
            li.textContent = target.url;
            ul.appendChild(li);
        });
        
        siteMapDiv.appendChild(ul);
    }
    
    updateDashboardStats() {
        document.getElementById('request-count').textContent = this.requests.length;
        document.getElementById('vuln-count').textContent = this.vulnerabilities.length;
        document.getElementById('target-count').textContent = this.targets.length;
        
        // Simulate scan progress
        const progress = Math.min(100, Math.floor(this.requests.length / 10));
        document.getElementById('scan-progress').textContent = `${progress}%`;
    }
    
    logActivity(message) {
        const activityLog = document.getElementById('activity-log');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.textContent = `[${timestamp}] ${message}`;
        activityLog.prepend(logEntry);
        
        // Limit log entries to prevent performance issues
        if (activityLog.children.length > 50) {
            activityLog.removeChild(activityLog.lastChild);
        }
    }
    
    loadInitialData() {
        // Add some initial stats for demo purposes
        this.updateDashboardStats();
        
        // Add a sample target
        this.targets.push({
            id: 1,
            url: 'http://glitch',
            added: new Date().toISOString()
        });
        this.updateSiteMap();
        
        // Add a sample request
        const sampleRequest = {
            id: 1,
            method: 'GET',
            url: 'http://glitch/login',
            status: 200,
            length: 1234,
            time: 125.34,
            timestamp: new Date().toISOString()
        };
        this.requests.push(sampleRequest);
        this.addRequestToHistory(sampleRequest);
        this.updateDashboardStats();
    }
    
    startSimulation() {
        // Simulate ongoing traffic
        setInterval(() => {
            if (this.isIntercepting) {
                this.simulateRequest();
            }
        }, 5000); // Simulate a request every 5 seconds when intercepting is on
    }
}

// Initialize the application
const glitcher = new GlitcherApp();

// Set up the proxy URL mapping
window.addEventListener('load', () => {
    // When user goes to http://glitch, redirect to this application
    if (window.location.hostname === 'glitch') {
        // This would be handled by DNS or proxy configuration in a real implementation
        console.log('Glitcher is running at http://glitch');
    }
});