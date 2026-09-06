import psutil
import time
import threading

class AntiCryptojacking:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        
        # Known mining processes
        self.mining_keywords = [
            'xmrig', 'minergate', 'coinhive', 'cryptonight',
            'ethminer', 'cgminer', 'bfgminer', 'cpuminer',
            'mining', 'miner', 'hash', 'crypto'
        ]
        
        # CPU threshold
        self.cpu_threshold = 90  # 90% CPU usage for 30 seconds = suspicious
        self.high_cpu_start = None
        
    def detect_mining_processes(self):
        """Detect process mining"""
        threats = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ''
                    
                    # Check mining keywords
                    for keyword in self.mining_keywords:
                        if keyword in proc_name or keyword in proc_exe:
                            threats.append({
                                'type': 'MINING_PROCESS',
                                'process': proc_name,
                                'pid': proc.info['pid'],
                                'message': f" CRYPTOJACKING DETECTED!\n\n"
                                          f"Process: {proc_name}\n"
                                          f"PID: {proc.info['pid']}\n\n"
                                          f"Laptop lo dipake buat mining!\n"
                                          f"Auto-killing miner... "
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
            print(f"[ANTI-CRYPTOJACKING] Error: {e}")
        
        return threats
    
    def detect_cpu_anomaly(self):
        """Detect CPU usage anomaly"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent >= self.cpu_threshold:
                if self.high_cpu_start is None:
                    self.high_cpu_start = time.time()
                elif time.time() - self.high_cpu_start >= 30:
                    return {
                        'type': 'CPU_ANOMALY',
                        'usage': cpu_percent,
                        'message': f" HIGH CPU USAGE!\n\n"
                                  f"CPU: {cpu_percent}%\n"
                                  f"Duration: 30+ seconds\n\n"
                                  f"Possible cryptojacking detected!\n"
                                  f"Check running processes. "
                    }
            else:
                self.high_cpu_start = None
                
        except Exception as e:
            print(f"[ANTI-CRYPTOJACKING] Error: {e}")
        
        return None
    
    def monitor_loop(self):
        self.is_running = True
        scan_interval = 5
        
        while self.is_running:
            # Check mining processes
            threats = self.detect_mining_processes()
            if threats and self.callback:
                for threat in threats:
                    self.callback(threat)
            
            # Check CPU anomaly
            cpu_threat = self.detect_cpu_anomaly()
            if cpu_threat and self.callback:
                self.callback(cpu_threat)
            
            time.sleep(scan_interval)
    
    def start(self):
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        print("[ANTI-CRYPTOJACKING]  Cryptojacking shield activated")
    
    def stop(self):
        self.is_running = False
