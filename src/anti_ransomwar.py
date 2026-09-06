import psutil
import time
import threading
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AntiRansomware:
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        
        # Critical folders to protect
        self.critical_folders = [
            os.path.expanduser('~\\Documents'),
            os.path.expanduser('~\\Pictures'),
            os.path.expanduser('~\\Desktop'),
            os.path.expanduser('~\\Downloads'),
        ]
        
        # File extensions commonly targeted
        self.target_extensions = [
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.txt', '.jpg', '.png', '.zip', '.rar',
            '.mp4', '.mp3', '.bak', '.sql', '.db'
        ]
        
        # Threshold for suspicious activity
        self.file_change_threshold = 50  # 50 files in 10 seconds = suspicious
        self.file_changes = []
        
    class FileChangeHandler(FileSystemEventHandler):
        def __init__(self, ransomware_detector):
            self.detector = ransomware_detector
        
        def on_modified(self, event):
            if not event.is_directory:
                ext = os.path.splitext(event.src_path)[1].lower()
                if ext in self.detector.target_extensions:
                    self.detector.file_changes.append(time.time())
        
        def on_created(self, event):
            if not event.is_directory:
                ext = os.path.splitext(event.src_path)[1].lower()
                if ext in self.detector.target_extensions:
                    self.detector.file_changes.append(time.time())
    
    def detect_mass_encryption(self):
        """Detect pola enkripsi massal"""
        current_time = time.time()
        
        # Clean old entries (older than 10 seconds)
        self.file_changes = [t for t in self.file_changes if current_time - t < 10]
        
        # Check threshold
        if len(self.file_changes) >= self.file_change_threshold:
            return {
                'type': 'RANSOMWARE_DETECTED',
                'changes': len(self.file_changes),
                'message': f" RANSOMWARE ACTIVITY DETECTED!\n\n"
                          f"Mass file encryption detected!\n"
                          f"{len(self.file_changes)} files modified in 10 seconds.\n\n"
                          f"Scanning for malicious process... "
            }
        
        return None
    
    def detect_suspicious_processes(self):
        """Detect process yang mencurigakan"""
        threats = []
        
        suspicious_keywords = [
            'ransom', 'encrypt', 'crypt', 'lock', 'cipher',
            'crypto', 'locker', 'wannacry', 'locky'
        ]
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ''
                    
                    for keyword in suspicious_keywords:
                        if keyword in proc_name or keyword in proc_exe:
                            threats.append({
                                'type': 'SUSPICIOUS_PROCESS',
                                'process': proc_name,
                                'pid': proc.info['pid'],
                                'message': f" SUSPICIOUS PROCESS!\n\n"
                                          f"Process: {proc_name}\n"
                                          f"PID: {proc.info['pid']}\n\n"
                                          f"Possible ransomware detected!\n"
                                          f"Auto-killing... "
                            })
                            
                            # Auto-kill
                            try:
                                proc.kill()
                                print(f"[ANTI-RANSOMWARE]  Killed: {proc_name}")
                            except:
                                pass
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            print(f"[ANTI-RANSOMWARE] Error: {e}")
        
        return threats
    
    def monitor_loop(self):
        self.is_running = True
        
        # Setup file system observer
        observer = Observer()
        handler = self.FileChangeHandler(self)
        
        for folder in self.critical_folders:
            if os.path.exists(folder):
                observer.schedule(handler, folder, recursive=True)
        
        observer.start()
        
        scan_interval = 2
        
        while self.is_running:
            # Check mass encryption
            threat = self.detect_mass_encryption()
            if threat and self.callback:
                self.callback(threat)
            
            # Check suspicious processes
            proc_threats = self.detect_suspicious_processes()
            if proc_threats and self.callback:
                for t in proc_threats:
                    self.callback(t)
            
            time.sleep(scan_interval)
        
        observer.stop()
    
    def start(self):
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        print("[ANTI-RANSOMWARE]  Ransomware guard activated")
    
    def stop(self):
        self.is_running = False
