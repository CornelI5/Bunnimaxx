import subprocess
import re
import time
import threading

class WifiDefense:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        self.trusted_bssid = None
        self.trusted_ssid = None
        self.is_connected = False
        self.defense_active = False
        
    def get_current_connection(self):
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            info = {
                'ssid': None,
                'bssid': None,
                'status': 'disconnected'
            }
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if 'SSID' in line and ':' in line:
                    match = re.search(r'SSID\s+:\s+(.+)', line)
                    if match:
                        info['ssid'] = match.group(1).strip()
                
                elif 'BSSID' in line and ':' in line:
                    match = re.search(r'BSSID\s+:\s+(.+)', line)
                    if match:
                        info['bssid'] = match.group(1).strip()
                
                elif 'State' in line and ':' in line:
                    match = re.search(r'State\s+:\s+(.+)', line)
                    if match:
                        info['status'] = match.group(1).strip().lower()
            
            return info
            
        except Exception as e:
            print(f"[WIFI DEFENSE] Error getting connection info: {e}")
            return {'ssid': None, 'bssid': None, 'status': 'disconnected'}
    
    def set_trusted_network(self, ssid=None, bssid=None):
        if ssid:
            self.trusted_ssid = ssid
        if bssid:
            self.trusted_bssid = bssid
        
        if not self.trusted_ssid or not self.trusted_bssid:
            current = self.get_current_connection()
            if current['ssid'] and current['bssid']:
                self.trusted_ssid = current['ssid']
                self.trusted_bssid = current['bssid']
                print(f"[WIFI DEFENSE] Trusted network set: {self.trusted_ssid} ({self.trusted_bssid})")
    
    def connect_to_network(self, ssid):
        try:
            print(f"[WIFI DEFENSE] Connecting to {ssid}...")
            result = subprocess.run(
                ['netsh', 'wlan', 'connect', f'name={ssid}'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                print(f"[WIFI DEFENSE]  Connected to {ssid}")
                return True
            else:
                print(f"[WIFI DEFENSE]  Failed to connect: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[WIFI DEFENSE] Error connecting: {e}")
            return False
    
    def disconnect_from_network(self):
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'disconnect'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                print(f"[WIFI DEFENSE] Disconnected from current network")
                return True
            else:
                print(f"[WIFI DEFENSE]  Failed to disconnect")
                return False
                
        except Exception as e:
            print(f"[WIFI DEFENSE] Error disconnecting: {e}")
            return False
    
    def detect_deauth_attack(self, current_info):
        if current_info['status'] == 'disconnected' and self.is_connected:
            return True
        return False
    
    def detect_evil_twin(self, current_info):
        if current_info['ssid'] == self.trusted_ssid and current_info['bssid'] != self.trusted_bssid:
            return True
        return False
    
    def defend_and_reconnect(self):
        print("[WIFI DEFENSE]  DEFENSE ACTIVATED!")
        
        self.disconnect_from_network()
        time.sleep(2)
        
        if self.trusted_ssid:
            success = self.connect_to_network(self.trusted_ssid)
            
            if success:
                print("[WIFI DEFENSE]  Reconnected to trusted network")
                if self.callback:
                    self.callback({
                        'type': 'EVIL_TWIN_BLOCKED',
                        'message': f" EVIL TWIN BLOCKED!\n\n"
                                  f"Attempted SSID: {self.trusted_ssid}\n"
                                  f"Fake BSSID was blocked.\n"
                                  f"Reconnected to trusted router.\n\n"
                                  f"Nice try. Your Evil Twin was intercepted. 🐰"
                    })
            else:
                print("[WIFI DEFENSE]  Failed to reconnect")
                if self.callback:
                    self.callback({
                        'type': 'DEAUTH_DETECTED',
                        'message': f" DEAUTH ATTACK DETECTED!\n\n"
                                  f"Connection was interrupted.\n"
                                  f"Attempting to reconnect...\n\n"
                                  f"Stay safe. "
                    })
    
    def monitor_loop(self):
        self.is_running = True
        check_interval = 2
        
        self.set_trusted_network()
        
        while self.is_running:
            current_info = self.get_current_connection()
            
            if current_info['status'] == 'connected':
                self.is_connected = True
            else:
                self.is_connected = False
            
            deauth_detected = self.detect_deauth_attack(current_info)
            evil_twin_detected = self.detect_evil_twin(current_info)
            
            if deauth_detected or evil_twin_detected:
                if not self.defense_active:
                    self.defense_active = True
                    self.defend_and_reconnect()
                    time.sleep(5)
                    self.defense_active = False
            
            time.sleep(check_interval)
    
    def start(self):
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        print("[WIFI DEFENSE] Started monitoring Wi-Fi connection...")
    
    def stop(self):
        self.is_running = False
        print("[WIFI DEFENSE] Stopped.")
