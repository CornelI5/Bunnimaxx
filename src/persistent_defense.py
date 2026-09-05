import ctypes
import os
import sys
import subprocess
import winreg
import time
import threading

class PersistentDefense:
    def __init__(self, app_name="Bunnimaxx"):
        self.app_name = app_name
        self.exe_path = os.path.abspath(sys.argv[0])
        self.service_name = f"{app_name}Service"
        
        self.advapi32 = ctypes.windll.advapi32
        self.kernel32 = ctypes.windll.kernel32
        
    def create_windows_service(self):
        try:
            result = subprocess.run(
                ['sc', 'query', self.service_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"[PERSISTENT DEFENSE] Creating Windows Service: {self.service_name}")
                
                create_cmd = [
                    'sc', 'create', self.service_name,
                    f'binPath= "{self.exe_path}"',
                    'start= auto',
                    f'displayname= "{self.app_name} Protection Service"',
                    'obj= LocalSystem'
                ]
                
                result = subprocess.run(create_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"[PERSISTENT DEFENSE]  Service created successfully")
                    subprocess.run(['sc', 'start', self.service_name], capture_output=True)
                    print(f"[PERSISTENT DEFENSE]  Service started")
                    return True
                else:
                    print(f"[PERSISTENT DEFENSE]  Failed to create service: {result.stderr}")
                    return False
            else:
                print(f"[PERSISTENT DEFENSE] Service already exists")
                return True
                
        except Exception as e:
            print(f"[PERSISTENT DEFENSE] Error creating service: {e}")
            return False
    
    def add_registry_protection(self):
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, self.exe_path)
            
            print(f"[PERSISTENT DEFENSE]  Registry protection added")
            return True
            
        except Exception as e:
            print(f"[PERSISTENT DEFENSE]  Registry protection failed: {e}")
            return False
    
    def protect_file_with_acl(self):
        try:
            cmd = [
                'icacls', self.exe_path,
                '/deny', 'Everyone:(DE,DC)',
                '/grant', 'Administrator:(F)'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[PERSISTENT DEFENSE]  File ACL protection activated")
                return True
            else:
                print(f"[PERSISTENT DEFENSE]  ACL protection failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[PERSISTENT DEFENSE] Error setting ACL: {e}")
            return False
    
    def create_uninstaller(self):
        uninstaller_code = '''
import ctypes
import os
import sys
import subprocess
import winreg

def require_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def uninstall():
    if not require_admin():
        print("ERROR: Administrator privilege required!")
        print("Right-click and select 'Run as administrator'")
        input("Press Enter to exit...")
        return
    
    print("=" * 50)
    print("BUNNIMAXX UNINSTALLER")
    print("=" * 50)
    print()
    
    pin = input("Enter uninstallation PIN (default: 1234): ")
    
    if pin != "1234":
        print(" Incorrect PIN. Uninstallation aborted.")
        input("Press Enter to exit...")
        return
    
    print()
    print("  WARNING: This will completely remove Bunnimaxx")
    confirm = input("Are you sure? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Uninstallation cancelled.")
        input("Press Enter to exit...")
        return
    
    print()
    print("Removing Windows Service...")
    subprocess.run(['sc', 'stop', 'BunnimaxxService'], capture_output=True)
    subprocess.run(['sc', 'delete', 'BunnimaxxService'], capture_output=True)
    
    print("Removing Registry entries...")
    try:
        key_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
            try:
                winreg.DeleteValue(key, "Bunnimaxx")
                print(" Registry entry removed")
            except:
                print("  Registry entry not found")
    except Exception as e:
        print(f"  Registry cleanup failed: {e}")
    
    print("Removing file protection...")
    exe_path = os.path.abspath(__file__).replace('uninstaller.py', 'Bunnimaxx.exe')
    subprocess.run(['icacls', exe_path, '/reset'], capture_output=True)
    
    print()
    print(" Uninstallation complete!")
    print("You can now manually delete Bunnimaxx.exe")
    input("Press Enter to exit...")

if __name__ == "__main__":
    uninstall()
'''
        
        uninstaller_path = os.path.join(os.path.dirname(self.exe_path), 'uninstall_bunnimaxx.py')
        
        try:
            with open(uninstaller_path, 'w') as f:
                f.write(uninstaller_code)
            
            print(f"[PERSISTENT DEFENSE]  Uninstaller created: {uninstaller_path}")
            return True
            
        except Exception as e:
            print(f"[PERSISTENT DEFENSE]  Failed to create uninstaller: {e}")
            return False
    
    def activate_all_layers(self):
        print("=" * 50)
        print("ACTIVATING PERSISTENT DEFENSE")
        print("=" * 50)
        
        self.create_windows_service()
        self.add_registry_protection()
        self.protect_file_with_acl()
        self.create_uninstaller()
        
        print()
        print("=" * 50)
        print(" ALL PROTECTION LAYERS ACTIVATED")
        print("=" * 50)
        print()
        print("   Bunnimaxx is now PROTECTED:")
        print("   Auto-starts on boot")
        print("   Protected from deletion")
        print("   Requires special uninstaller")
        print("   Uninstaller needs PIN: 1234")
        print()
        print("To uninstall, run: uninstall_bunnimaxx.py")
        print("=" * 50)
