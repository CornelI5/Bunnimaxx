import psutil
import socket
import re
import time
import threading
import os
import json
from datetime import datetime

class AntiDoxxingShield:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        
        # Blacklist IP ranges (known logging services, trackers)
        self.ip_blacklist = [
            'grabify.link',
            'iplogger.org',
            '2no.co',
            'blasze.com',
            'ipgrabber.ru',
        ]
        
        # Sensitive data patterns
        self.sensitive_patterns = {
            'phone': r'\b(\+?62|0)[\s-]?8[\d\s-]{8,12}\b',  # Indonesian phone
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'address': r'\b(Jl\.|Jalan|Dusun|RT|RW|Kel|Kec|Kab|Kota)\b.*\d+',
            'nip': r'\b\d{18}\b',  # NIK Indonesia
        }
        
        # Whitelist apps for webcam/mic
        self.camera_whitelist = ['zoom.exe', 'teams.exe', 'chrome.exe', 'firefox.exe']
        
        # Clipboard history
        self.last_clipboard = ""
        self.clipboard_timer = None
        
    def get_public_ip(self):
        """Get current public IP (for monitoring)"""
        try:
            result = subprocess.run(
                ['powershell', '-Command', '(Invoke-WebRequest -Uri "https://api.ipify.org").Content'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except:
            return None
    
    def scan_active_connections(self):
        """Layer 1: Monitor outbound connections"""
        threats = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED':
                    try:
                        # Get process name
                        process = psutil.Process(conn.pid)
                        process_name = process.name().lower()
                        
                        # Check if connecting to blacklisted domain
                        remote_ip = conn.raddr.ip
                        
                        # Reverse DNS lookup
                        try:
                            hostname = socket.gethostbyaddr(remote_ip)[0]
                            
                            for blacklisted in self.ip_blacklist:
                                if blacklisted in hostname:
                                    threats.append({
                                        'type': 'IP_LEAK_ATTEMPT',
                                        'process': process_name,
                                        'ip': remote_ip,
                                        'hostname': hostname,
                                        'message': f" IP LEAK DETECTED!\n\n"
                                                  f"Process: {process_name}\n"
                                                  f"Connecting to: {hostname}\n"
                                                  f"IP: {remote_ip}\n\n"
                                                  f"Possible IP logger/tracker.\n"
                                                  f"Blocked by Inversert. "
                                    })
                        except:
                            pass
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
        except Exception as e:
            print(f"[ANTI-DOXXING] Error scanning connections: {e}")
        
        return threats
    
    def scan_file_metadata(self, file_path):
        """Layer 2: Scan file for sensitive metadata"""
        threats = []
        
        try:
            # Check file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.tiff']:
                # Image file - check EXIF
                try:
                    from PIL import Image
                    from PIL.ExifTags import TAGS
                    
                    img = Image.open(file_path)
                    exif_data = img._getexif()
                    
                    if exif_data:
                        sensitive_tags = ['GPSInfo', 'DateTime', 'Make', 'Model']
                        found_tags = []
                        
                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if tag in sensitive_tags:
                                found_tags.append(f"{tag}: {value}")
                        
                        if found_tags:
                            threats.append({
                                'type': 'METADATA_LEAK',
                                'file': file_path,
                                'tags': found_tags,
                                'message': f" METADATA LEAK IN IMAGE!\n\n"
                                          f"File: {os.path.basename(file_path)}\n"
                                          f"Sensitive data found:\n" + 
                                          "\n".join(found_tags[:3]) +
                                          f"\n\nGPS location or device info exposed!\n"
                                          f"Use Inversert Scrubber to clean. "
                            })
                except ImportError:
                    pass  # PIL not installed
                    
            elif ext in ['.docx', '.xlsx', '.pptx', '.pdf']:
                # Office/PDF file - check author info
                try:
                    stat = os.stat(file_path)
                    # Check file properties
                    threats.append({
                        'type': 'DOCUMENT_METADATA',
                        'file': file_path,
                        'message': f" DOCUMENT METADATA WARNING!\n\n"
                                  f"File: {os.path.basename(file_path)}\n"
                                  f"Office documents may contain:\n"
                                  f"- Author name\n"
                                  f"- Company info\n"
                                  f"- Edit history\n\n"
                                  f"Use 'Inspect Document' before sharing. "
                    })
                except:
                    pass
                    
        except Exception as e:
            print(f"[ANTI-DOXXING] Error scanning metadata: {e}")
        
        return threats
    
    def scrub_file_metadata(self, file_path):
        """Layer 2: Remove sensitive metadata from file"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png']:
                from PIL import Image
                
                img = Image.open(file_path)
                # Create new image without EXIF
                data = list(img.getdata())
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(data)
                
                # Save to new file
                base, ext = os.path.splitext(file_path)
                clean_path = f"{base}_clean{ext}"
                clean_img.save(clean_path)
                
                print(f"[ANTI-DOXXING]  Metadata scrubbed: {clean_path}")
                return clean_path
                
        except Exception as e:
            print(f"[ANTI-DOXXING] Error scrubbing metadata: {e}")
        
        return None
    
    def monitor_clipboard(self):
        """Layer 3: Monitor clipboard for sensitive data"""
        try:
            import pyperclip
            
            current_clipboard = pyperclip.paste()
            
            if current_clipboard != self.last_clipboard:
                self.last_clipboard = current_clipboard
                
                # Check for sensitive patterns
                for data_type, pattern in self.sensitive_patterns.items():
                    if re.search(pattern, current_clipboard):
                        if self.callback:
                            self.callback({
                                'type': 'CLIPBOARD_SENSITIVE',
                                'data_type': data_type,
                                'message': f" SENSITIVE DATA IN CLIPBOARD!\n\n"
                                          f"Type: {data_type.upper()}\n"
                                          f"Detected: {current_clipboard[:20]}...\n\n"
                                          f"Be careful copying sensitive info!\n"
                                          f"Clipboard will auto-clear in 30s. "
                            })
                        
                        # Auto-clear after 30 seconds
                        if self.clipboard_timer:
                            self.clipboard_timer.cancel()
                        
                        self.clipboard_timer = threading.Timer(30, self.clear_clipboard)
                        self.clipboard_timer.start()
                        
        except Exception as e:
            print(f"[ANTI-DOXXING] Error monitoring clipboard: {e}")
    
    def clear_clipboard(self):
        """Clear clipboard automatically"""
        try:
            import pyperclip
            pyperclip.copy('')
            print("[ANTI-DOXXING]  Clipboard auto-cleared")
        except:
            pass
    
    def check_camera_access(self):
        """Layer 4: Monitor webcam/mic access"""
        threats = []
        
        try:
            # Check if any process is using camera
            # Windows doesn't have direct API for this, so we check known apps
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # Check if camera app is running but not in whitelist
                    if 'camera' in proc_name or 'webcam' in proc_name:
                        if proc_name not in self.camera_whitelist:
                            threats.append({
                                'type': 'CAMERA_ACCESS',
                                'process': proc_name,
                                'message': f" CAMERA ACCESS DETECTED!\n\n"
                                          f"Process: {proc_name}\n"
                                          f"Status: Running\n\n"
                                          f"Unknown app accessing camera!\n"
                                          f"Check Windows Privacy Settings. "
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            print(f"[ANTI-DOXXING] Error checking camera: {e}")
        
        return threats
    
    def analyze_network_traffic(self):
        """Layer 5: Analyze network traffic patterns"""
        threats = []
        
        try:
            # Get network IO stats
            net_io = psutil.net_io_counters()
            
            # Check for unusual outbound traffic
            # (This is simplified - real implementation would need baseline)
            bytes_sent = net_io.bytes_sent
            
            # Store baseline (first run)
            if not hasattr(self, 'baseline_sent'):
                self.baseline_sent = bytes_sent
                self.baseline_time = time.time()
            else:
                elapsed = time.time() - self.baseline_time
                if elapsed > 0:
                    rate = (bytes_sent - self.baseline_sent) / elapsed
                    
                    # Alert if sending too much data (possible exfiltration)
                    if rate > 1_000_000:  # 1 MB/s threshold
                        threats.append({
                            'type': 'DATA_EXFILTRATION',
                            'rate': rate,
                            'message': f" HIGH OUTBOUND TRAFFIC!\n\n"
                                      f"Rate: {rate/1000:.2f} KB/s\n\n"
                                      f"Possible data exfiltration detected!\n"
                                      f"Check running applications. "
                        })
                        
        except Exception as e:
            print(f"[ANTI-DOXXING] Error analyzing traffic: {e}")
        
        return threats
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.is_running = True
        scan_interval = 10  # Scan every 10 seconds
        
        while self.is_running:
            # Layer 1: IP Leak Detection
            ip_threats = self.scan_active_connections()
            if ip_threats and self.callback:
                for threat in ip_threats:
                    self.callback(threat)
            
            # Layer 3: Clipboard Monitoring
            self.monitor_clipboard()
            
            # Layer 4: Camera Access
            camera_threats = self.check_camera_access()
            if camera_threats and self.callback:
                for threat in camera_threats:
                    self.callback(threat)
            
            # Layer 5: Network Traffic
            traffic_threats = self.analyze_network_traffic()
            if traffic_threats and self.callback:
                for threat in traffic_threats:
                    self.callback(threat)
            
            time.sleep(scan_interval)
    
    def start(self):
        """Start anti-doxxing shield"""
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        self.is_running = True
        print("[ANTI-DOXXING]  Anti-OSINT Shield activated")
        print("[ANTI-DOXXING] Monitoring: IP leaks, clipboard, camera, network")
    
    def stop(self):
        """Stop anti-doxxing shield"""
        self.is_running = False
        if self.clipboard_timer:
            self.clipboard_timer.cancel()
        print("[ANTI-DOXXING] Shield deactivated")
