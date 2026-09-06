import subprocess
import time
import threading

class AntiBitlocker:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        
    def check_bitlocker_status(self):
        """Check status BitLocker"""
        try:
            result = subprocess.run(
                ['manage-bde', '-status'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None
                
        except Exception as e:
            print(f"[ANTI-BITLOCKER] Error: {e}")
            return None
    
    def detect_bitlocker_bypass(self):
        """Detect bypass BitLocker"""
        threats = []
        
        # Check for suspicious processes that might try to bypass BitLocker
        try:
            result = subprocess.run(
                ['tasklist'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            suspicious_tools = [
                'mimikatz', 'procdump', 'ntdsutil', 'vssadmin',
                'diskpart', 'format', 'cipher'
            ]
            
            for tool in suspicious_tools:
                if tool in result.stdout.lower():
                    threats.append({
                        'type': 'BITLOCKER_BYPASS_ATTEMPT',
                        'tool': tool,
                        'message': f" BITLOCKER BYPASS ATTEMPT!\n\n"
                                  f"Tool detected: {tool}\n\n"
                                  f"Someone trying to bypass encryption!\n"
                                  f"Blocking... "
                    })
                    
        except Exception as e:
            print(f"[ANTI-BITLOCKER] Error: {e}")
        
        return threats
    
    def monitor_loop(self):
        self.is_running = True
        scan_interval = 30  # Check every 30 seconds
        
        while self.is_running:
            # Check BitLocker bypass attempts
            threats = self.detect_bitlocker_bypass()
            
            if threats and self.callback:
                for threat in threats:
                    self.callback(threat)
            
            time.sleep(scan_interval)
    
    def start(self):
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        print("[ANTI-BITLOCKER]  BitLocker protection v3 activated")
    
    def stop(self):
        self.is_running = False
