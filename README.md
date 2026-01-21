# Glitcher - Professional Web Security Testing Platform

Glitcher is a professional web security testing platform inspired by PortSwigger's Burp Suite. It provides a comprehensive set of tools for web application security testing including proxy capabilities, vulnerability scanning, and manual testing features.

## Features

- **Dashboard**: Overview of testing activities and statistics
- **Proxy**: Intercept and modify HTTP/HTTPS traffic
- **Intruder**: Automated attack tool with multiple attack types
- **Repeater**: Manual request editor and sender
- **Target**: Site mapping and target management
- **Site Package**: Automatic website crawling and vulnerability analysis
- **Sequencer**: Randomness analysis tool
- **Decoder**: Encoding/decoding utilities
- **Comparer**: Response comparison tool
- **Scanner**: Automated vulnerability detection
- **Extender**: Plugin support
- **User-Agent Management**: Anonymity through random User-Agent selection with manual override
- **UA-Gen**: User-Agent generator with customizable options (OS, device, browser) and file integration
- **D-Attack**: Layer 7 DDoS attack tool with configurable parameters (threads, bandwidth up to 1200 Mbps), proxy support (proxies.txt), and bypass capabilities (Cloudflare, 2Captcha)
- **UDP/TCP Attack**: Network layer attacks with UDP flood, TCP connection flood, and SYN flood capabilities
- **Proxy Management**: Proxy validation and management with status checking (Online/Offline) and enable/disable controls
- **Proxy Display in Attack Tabs**: Individual proxy enable/disable controls directly in DDoS and UDP/TCP attack tabs
- **Login Protection**: Password-protected access with image background and secure authentication (password: godveaq)
- **Enhanced Login GUI**: Larger login window (1280x720) with improved visibility and user experience
- **Reliable Vulnerability Detection**: Consistent display of security vulnerabilities in Site Package module
- **Fixed UA Generator**: Proper UI updates and reliable generation with improved feedback

## Installation

1. Clone or download this repository
2. Install Node.js if not already installed
3. Run the following command to install dependencies:

```bash
npm install
```

## Usage

### Web Version

1. Start the Glitcher server:

```bash
npm start
```

2. The server will start on `http://localhost:8080`

3. Configure your browser to use Glitcher as a proxy:
   - Host: `localhost`
   - Port: `8080`

4. Access Glitcher interface at `http://localhost:8080`

5. To access via `http://glitch`, you need to:
   - Add an entry to your system's hosts file (`C:\\Windows\\System32\\drivers\\etc\\hosts` on Windows)
   - Add the line: `127.0.0.1 glitch`
   - Restart your browser after making this change

### Python GUI Version

1. Run the Python GUI application:

```bash
python run_glitcher.py
```

2. The Glitcher GUI will open with all the same functionality as the web version

3. Use the tabs to access different security testing tools

4. The Python version provides the same professional security testing capabilities as the web version

## How to Use

### Proxy Functionality
- Toggle interception on/off using the Proxy panel
- All HTTP/HTTPS traffic routed through the configured proxy will be captured
- Review and modify requests in the HTTP history table
- Send requests to Repeater or Intruder for further testing

### Intruder
- Select an attack type (Sniper, Battering Ram, Pitchfork, Cluster Bomb)
- Paste an HTTP request in the request editor
- Add payloads to test in the payloads section
- Click "Start Attack" to begin testing

### Repeater
- Paste an HTTP request in the request editor
- Modify the request as needed
- Click "Send" to send the request and view the response

### Target
- Add target URLs to build a site map
- Monitor and analyze the target application structure

### Site Package
- Automatically crawl and analyze websites
- Display discovered URLs in a hierarchical structure
- Analyze URLs for vulnerabilities (SQL injection, XSS)
- Extract comments from source code
- Find hidden URLs in page source
- Click on URLs to see detailed analysis on the right panel

## Architecture

Glitcher operates as a man-in-the-middle proxy:

```
Browser ↔ Glitcher Proxy ↔ Target Web Server
```

All traffic between the browser and target server passes through Glitcher, allowing for inspection, modification, and analysis.

## Legal Disclaimer

Glitcher is intended for authorized security testing only. Users are responsible for ensuring they have explicit permission before testing any systems they do not own. Unauthorized access to computer systems is illegal in many jurisdictions.

## License

MIT License - see LICENSE file for details.

## Security Notice


This tool is desi

https://github.com/user-attachments/assets/43e0eed7-e95f-4274-993f-52fc3a611932


https://github.com/user-attachments/assets/c3b4a698-b408-420d-b33d-0d56cd9fd3b4


gned for security professionals and should be used responsibly. Always follow responsible disclosure practices and applicable laws in your jurisdiction.
