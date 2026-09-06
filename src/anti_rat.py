import psutil
import socket
import time
import threading

class AntiRAT:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        
        # Suspicious ports (commonly used by RATs)
        self.suspicious_ports = [
            4444, 5555, 6666, 7777, 8080, 8888, 9999,
            1337, 31337, 12345, 54321
        ]
        
        # Known RAT process names
        self.rat_keywords = [
            'rat', 'trojan', 'backdoor', 'remote', 'access',
            'teamviewer', 'anydesk', 'vnc', 'rdesktop'
        ]
        
    def detect_suspicious_connections(self):
        """Detect koneksi outbound mencurigakan"""
        threats = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    try:
                        process = psutil.Process(conn.pid)
                        proc_name = process.name().lower()
                        
                        # Check suspicious port
                        if conn.raddr.port in self.suspicious_ports:
                            threats.append({
                                'type': 'SUSPICIOUS_PORT',
                                'process': proc_name,
                                'port': conn.raddr.port,
                                'ip': conn.raddr.ip,
                                'message': f" SUSPICIOUS CONNECTION!\n\n"
                                          f"Process: {proc_name}\n"
                                          f"Port: {conn.raddr.port}\n"
                                          f"IP: {conn.raddr.ip}\n\n"
                                          f"Possible RAT communication detected!\n"
                                          f"Blocking connection... "
                            })
                        
                        # Check suspicious process name
                        for keyword in self.rat_keywords:
                            if keyword in proc_name:
                                threats.append({
                                    'type': 'RAT_PROCESS',
                                    'process': proc_name,
                                    'pid': conn.pid,
                                    'message': f" RAT PROCESS DETECTED!\n\n"
                                              f"Process: {proc_name}\n"
                                              f"PID: {conn.pid}\n\n"
                                              f"Remote access tool detected!\n"
                                              f"Auto-killing... "
                                })
                                
                                # Auto-kill
                                try:
                                    process.kill()
                                except:
                                    pass
                                break
                                
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
        except Exception as e:
            print(f"[ANTI-RAT] Error: {e}")
        
        return threats
    
    def monitor_loop(self):
        self.is_running = True
        scan_interval = 5
        
        while self.is_running:
            threats = self.detect_suspicious_connections()
            
            if threats and self.callback:
                for threat in threats:
                    self.callback(threat)
            
            time.sleep(scan_interval)
    
    def start(self):
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        print("[ANTI-RAT]  RAT firewall activated")
    
    def stop(self):
        self.is_running = False
