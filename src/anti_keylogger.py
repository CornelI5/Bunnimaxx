import psutil
import ctypes
import time
import threading

class AntiKeylogger:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        
        self.keyboard_whitelist = [
            'explorer.exe', 'chrome.exe', 'firefox.exe', 'msedge.exe',
            'code.exe', 'discord.exe', 'steam.exe', 'python.exe',
            'bunnimaxx.exe', 'svchost.exe', 'csrss.exe'
        ]
        
        # Suspicious keywords
        self.suspicious_keywords = [
            'keylog', 'spy', 'sniff', 'capture', 'record', 'monitor',
            'intercept', 'hook', 'inject'
        ]
        
    def detect_keyboard_hooks(self):
        """Detect process yang hook keyboard API"""
        threats = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ''
                    
                    # Skip whitelist
                    if proc_name in self.keyboard_whitelist:
                        continue
                    
                    # Check suspicious keywords
                    is_suspicious = False
                    for keyword in self.suspicious_keywords:
                        if keyword in proc_name or keyword in proc_exe:
                            is_suspicious = True
                            break
                    
                    if is_suspicious:
                        threats.append({
                            'type': 'KEYLOGGER_DETECTED',
                            'process': proc_name,
                            'pid': proc.info['pid'],
                            'exe': proc_exe,
                            'message': f" KEYLOGGER DETECTED!\n\n"
                                      f"Process: {proc_name}\n"
                                      f"PID: {proc.info['pid']}\n\n"
                                      f"Auto-killing process... "
                        })
                        
                        # Auto-kill
                        try:
                            proc.kill()
                            print(f"[ANTI-KEYLOGGER]  Killed: {proc_name}")
                        except:
                            print(f"[ANTI-KEYLOGGER]  Failed to kill: {proc_name}")
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            print(f"[ANTI-KEYLOGGER] Error: {e}")
        
        return threats
    
    def monitor_loop(self):
        self.is_running = True
        scan_interval = 5
        
        while self.is_running:
            threats = self.detect_keyboard_hooks()
            
            if threats and self.callback:
                for threat in threats:
                    self.callback(threat)
            
            time.sleep(scan_interval)
    
    def start(self):
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        print("[ANTI-KEYLOGGER]  Keylogger shield activated")
    
    def stop(self):
        self.is_running = False
