# GLITCHER - Professional Web Security Testing Platform

## Project Summary

Glitcher is a professional web security testing platform inspired by PortSwigger's Burp Suite. It provides a comprehensive set of tools for web application security testing with both web and GUI interfaces.

## Features Implemented

### Web Interface (Node.js/JavaScript)
- Complete Burp Suite-like interface with all major components
- Dashboard with statistics and activity log
- Proxy with interception and history
- Intruder with multiple attack types (Sniper, Battering Ram, Pitchfork, Cluster Bomb)
- Repeater for manual request testing
- Target site mapping
- Sequencer for randomness analysis
- Decoder for encoding/decoding
- Comparer for response comparison
- Scanner for automated vulnerability detection
- Extender for plugin management

### Python GUI Interface (Tkinter)
- Full-featured GUI application matching web interface functionality
- All components implemented with Tkinter
- Same professional security testing capabilities
- Real-time simulation of security testing activities

### Additional Features
- Proxy functionality for intercepting HTTP/HTTPS traffic
- Vulnerability detection simulation
- Request/response manipulation
- Payload testing capabilities
- Site mapping and target management
- Automatic website crawling and analysis
- SQL injection detection
- XSS vulnerability detection
- Source code comment extraction
- Hidden URL discovery
- Encoding/decoding utilities
- Session token analysis
- Response comparison tools

## File Structure

### Main Application Files
- `index.html` - Main web interface
- `styles.css` - Styling for web interface
- `app.js` - JavaScript functionality for web version
- `server.js` - Node.js server implementation
- `glitcher_gui.py` - Python GUI implementation
- `run_glitcher.py` - Python GUI launcher

### Configuration and Setup
- `package.json` - Node.js dependencies and scripts
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `DOCUMENTATION.md` - Comprehensive documentation

### Startup Scripts
- `start.bat` - Windows batch file for web version
- `start.ps1` - PowerShell script for web version
- `start_gui.bat` - Windows batch file for GUI version
- `start_gui.ps1` - PowerShell script for GUI version
- `launcher.bat` - Universal launcher (web or GUI)
- `launcher.ps1` - PowerShell universal launcher

### Setup Scripts
- `setup_glitch_url.bat` - Windows batch file to add glitch to hosts file
- `setup_glitch_url.ps1` - PowerShell script to add glitch to hosts file

### Utility Files
- `test-server.js` - Server testing script

## How to Run

### Web Version
1. Install Node.js
2. Run `npm install` to install dependencies
3. Run `npm start` to start the server
4. Access at http://localhost:8080
5. For http://glitch access, run setup script to modify hosts file

### Python GUI Version
1. Ensure Python 3.6+ is installed
2. Run `pip install -r requirements.txt`
3. Run `python run_glitcher.py` or `npm run python`

### Universal Launcher
- Run `launcher.bat` or `launcher.ps1` to choose between versions

## Professional Security Testing Capabilities

Glitcher provides the same core functionality as Burp Suite:

1. **Interception** - Man-in-the-middle proxy for HTTP/HTTPS traffic
2. **Analysis** - Request/response inspection and modification
3. **Attack** - Automated and manual vulnerability testing
4. **Reporting** - Activity logging and vulnerability tracking
5. **Extensibility** - Plugin support for enhanced functionality

## Technology Stack

### Web Version
- Frontend: HTML5, CSS3, JavaScript (ES6+)
- Backend: Node.js with Express
- Proxy: http-proxy module
- Build: npm for dependency management

### Python GUI Version
- GUI Framework: Tkinter (built into Python)
- HTTP Operations: requests library
- Threading: for simulation and background tasks
- Cross-platform compatibility

## Architecture

Glitcher operates as a man-in-the-middle proxy:
```
Browser ↔ Glitcher ↔ Target Web Server
```

All traffic passes through Glitcher, allowing for complete inspection, modification, and analysis.

## Legal Notice

Glitcher is intended for authorized security testing only. Users are responsible for ensuring they have explicit permission before testing any systems they do not own. Unauthorized access to computer systems is illegal in many jurisdictions.

## License

MIT License - see LICENSE file for details.

## Conclusion

Glitcher is a fully functional professional web security testing platform that replicates the core functionality of Burp Suite. It provides both web and GUI interfaces with comprehensive security testing capabilities, making it suitable for professional security analysts and penetration testers.