import psutil
import os
import time
import threading

class AntiDataExfiltration:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        
        # Sensitive folders
        self.sensitive_folders = [
            os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data'),
            os.path.expanduser('~\\AppData\\Local\\Mozilla\\Firefox'),
            os.path.expanduser('~\\AppData\\Roaming\\Electrum'),
            os.path.expanduser('~\\AppData\\Roaming\\Bitcoin'),
        ]
        
        # Sus process keywords
        self.exfil_keywords = [
            'stealer', 'exfil', 'grab', 'collect', 'harvest',
            'credential', 'password', 'wallet'
        ]
        
    def detect_sensitive_access(self):
        """Detect akses ke folder sensitif"""
        threats = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    for keyword in self.exfil_keywords:
                        if keyword in proc_name:
                            threats.append({
                                'type': 'DATA_EXFILTRATION',
                                'process': proc_name,
                                'pid': proc.info['pid'],
                                'message': f" DATA EXFILTRATION DETECTED!\n\n"
                                          f"Process: {proc_name}\n"
                                          f"PID: {proc.info['pid']}\n\n"
                                          f"Stealer trying to access sensitive data!\n"
                                          f"Auto-killing... "
                            })
                            
                            # Auto-kill
                            try:
                                proc.kill()
                            except:
                                pass
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            print(f"[ANTI-EXFILTRATION] Error: {e}")
        
        return threats
    
    def monitor_loop(self):
        self.is_running = True
        scan_interval = 5
        
        while self.is_running:
            threats = self.detect_sensitive_access()
            
            if threats and self.callback:
                for threat in threats:
                    self.callback(threat)
            
            time.sleep(scan_interval)
    
    def start(self):
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        print("[ANTI-EXFILTRATION]  Data exfiltration shield activated")
    
    def stop(self):
        self.is_running = False
