import subprocess
import re
import time
import threading

class WifiRadar:
    def __init__(self, callback=None):
        self.known_bssids = {}
        self.callback = callback
        self.is_running = False
        self.threat_detected = False
        
    def scan_networks(self):
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            networks = []
            current_ssid = None
            current_bssid = None
            current_signal = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if line.startswith('SSID'):
                    match = re.search(r'SSID\s+\d+\s+:\s+(.+)', line)
                    if match:
                        current_ssid = match.group(1).strip()
                
                elif 'BSSID' in line:
                    match = re.search(r'BSSID\s+\d+\s+:\s+(.+)', line)
                    if match:
                        current_bssid = match.group(1).strip()
                
                elif 'Signal' in line:
                    match = re.search(r'Signal\s+:\s+(\d+)%', line)
                    if match:
                        current_signal = int(match.group(1))
                        
                        if current_ssid and current_bssid:
                            networks.append({
                                'ssid': current_ssid,
                                'bssid': current_bssid,
                                'signal': current_signal
                            })
                            current_ssid = None
                            current_bssid = None
                            current_signal = None
            
            return networks
            
        except Exception as e:
            print(f"[WIFI RADAR] Error scanning: {e}")
            return []
    
    def detect_evil_twin(self, networks):
        ssid_map = {}
        threats = []
        
        for net in networks:
            ssid = net['ssid']
            bssid = net['bssid']
            
            if ssid not in ssid_map:
                ssid_map[ssid] = []
            ssid_map[ssid].append(bssid)
        
        for ssid, bssids in ssid_map.items():
            if len(bssids) > 1:
                threats.append({
                    'type': 'EVIL_TWIN',
                    'ssid': ssid,
                    'bssids': bssids,
                    'message': f" EVIL TWIN DETECTED: Multiple APs with SSID '{ssid}'"
                })
        
        return threats
    
    def detect_deauth_pattern(self):
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if 'disconnected' in result.stdout.lower():
                return {
                    'type': 'DEAUTH_SUSPECT',
                    'message': " Wi-Fi disconnected unexpectedly. Possible deauth attack."
                }
            
            return None
            
        except Exception as e:
            return None
    
    def monitor_loop(self):
        self.is_running = True
        scan_interval = 5
        
        while self.is_running:
            networks = self.scan_networks()
            threats = self.detect_evil_twin(networks)
            deauth_threat = self.detect_deauth_pattern()
            if deauth_threat:
                threats.append(deauth_threat)
            
            if threats and not self.threat_detected:
                self.threat_detected = True
                if self.callback:
                    self.callback(threats)
            
            elif not threats and self.threat_detected:
                self.threat_detected = False
                if self.callback:
                    self.callback([])
            
            time.sleep(scan_interval)
    
    def start(self):
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        print("[WIFI RADAR] Started monitoring Wi-Fi threats...")
    
    def stop(self):
        self.is_running = False
        print("[WIFI RADAR] Stopped.")