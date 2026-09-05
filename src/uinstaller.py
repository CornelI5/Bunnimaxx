import ctypes
import os
import sys
import subprocess
import winreg
import time

class WindowsNativeUninstaller:
    def __init__(self):
        self.app_name = "Bunnimaxx"
        self.service_name = "BunnimaxxService"
        self.exe_path = self._get_bunnimaxx_path()
        
        self.user32 = ctypes.windll.user32
        self.credui = ctypes.windll.credui
        self.shell32 = ctypes.windll.shell32
        
    def _get_bunnimaxx_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "Bunnimaxx.exe")
    
    def check_admin_privilege(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def trigger_uac_prompt(self):
        if not self.check_admin_privilege():
            print("[UNINSTALLER]   Administrator privilege required")
            print("[UNINSTALLER] Requesting UAC elevation...")
            
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    sys.executable,
                    " ".join(sys.argv),
                    None,
                    1
                )
                sys.exit(0)
            except Exception as e:
                print(f"[UNINSTALLER]  UAC elevation failed: {e}")
                return False
        
        print("[UNINSTALLER]  Running with administrator privilege")
        return True
    
    def show_credential_dialog(self):
        print("[UNINSTALLER]  Requesting Windows authentication...")
        
        class CREDUI_INFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_ulong),
                ("hwndParent", ctypes.c_void_p),
                ("pszMessageText", ctypes.c_wchar_p),
                ("pszCaptionText", ctypes.c_wchar_p),
                ("hbmBanner", ctypes.c_void_p)
            ]
        
        cred_info = CREDUI_INFO()
        cred_info.cbSize = ctypes.sizeof(CREDUI_INFO)
        cred_info.hwndParent = 0
        cred_info.pszMessageText = "Enter your Windows PIN or password to uninstall Bunnimaxx"
        cred_info.pszCaptionText = "Bunnimaxx Uninstaller - Authentication Required"
        cred_info.hbmBanner = 0
        
        max_username = 256
        max_password = 256
        username = ctypes.create_unicode_buffer(max_username)
        password = ctypes.create_unicode_buffer(max_password)
        save = ctypes.c_bool(False)
        
        flags = 0x0001 | 0x0004
        
        result = self.credui.CredUIPromptForWindowsCredentialsW(
            ctypes.byref(cred_info),
            0,
            ctypes.byref(username),
            max_username,
            ctypes.byref(password),
            max_password,
            ctypes.byref(save),
            "Bunnimaxx Uninstaller",
            "",
            0,
            flags
        )
        
        if result == 0:
            print("[UNINSTALLER]  Authentication successful")
            return True
        else:
            print("[UNINSTALLER]  Authentication failed or cancelled")
            return False
    
    def show_smartscreen_warning(self):
        print("[UNINSTALLER]   Showing security warning...")
        
        MB_YESNO = 0x04
        MB_ICONWARNING = 0x30
        MB_DEFBUTTON2 = 0x100
        
        message = (
            "Windows protected your PC\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Bunnimaxx is a security protection software.\n"
            "Uninstalling it will remove all protection layers.\n\n"
            "Are you sure you want to continue?\n\n"
            "Click 'Yes' to uninstall or 'No' to cancel."
        )
        
        result = self.user32.MessageBoxW(
            0,
            message,
            "Bunnimaxx Uninstaller - Security Warning",
            MB_YESNO | MB_ICONWARNING | MB_DEFBUTTON2
        )
        
        if result == 6:
            print("[UNINSTALLER]  User confirmed uninstallation")
            return True
        else:
            print("[UNINSTALLER]  User cancelled uninstallation")
            return False
    
    def remove_windows_service(self):
        print("[UNINSTALLER] Removing Windows Service...")
        
        try:
            subprocess.run(['sc', 'stop', self.service_name], capture_output=True)
            time.sleep(2)
            
            result = subprocess.run(['sc', 'delete', self.service_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[UNINSTALLER]  Service '{self.service_name}' removed")
            else:
                print(f"[UNINSTALLER]   Service not found or already removed")
                
        except Exception as e:
            print(f"[UNINSTALLER]   Service removal error: {e}")
    
    def remove_registry_entries(self):
        print("[UNINSTALLER] Removing Registry entries...")
        
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
                try:
                    winreg.DeleteValue(key, self.app_name)
                    print(f"[UNINSTALLER]  Registry entry '{self.app_name}' removed")
                except FileNotFoundError:
                    print(f"[UNINSTALLER]   Registry entry not found")
                    
        except Exception as e:
            print(f"[UNINSTALLER]   Registry cleanup error: {e}")
    
    def remove_file_protection(self):
        print("[UNINSTALLER] Removing file protection...")
        
        try:
            if os.path.exists(self.exe_path):
                result = subprocess.run(
                    ['icacls', self.exe_path, '/reset'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"[UNINSTALLER]  File protection removed")
                else:
                    print(f"[UNINSTALLER]   File protection reset failed")
            else:
                print(f"[UNINSTALLER]   Bunnimaxx.exe not found")
                
        except Exception as e:
            print(f"[UNINSTALLER]   File protection error: {e}")
    
    def run_uninstallation(self):
        print("=" * 60)
        print("BUNNIMAXX UNINSTALLER")
        print("Windows-Native Authentication Mode")
        print("=" * 60)
        print()
        
        if not self.trigger_uac_prompt():
            print("\n Uninstallation aborted: UAC elevation failed")
            input("\nPress Enter to exit...")
            return
        
        print()
        
        if not self.show_credential_dialog():
            print("\n Uninstallation aborted: Authentication failed")
            input("\nPress Enter to exit...")
            return
        
        print()
        
        if not self.show_smartscreen_warning():
            print("\n Uninstallation aborted: User cancelled")
            input("\nPress Enter to exit...")
            return
        
        print()
        print("=" * 60)
        print("STARTING UNINSTALLATION...")
        print("=" * 60)
        print()
        
        self.remove_windows_service()
        self.remove_registry_entries()
        self.remove_file_protection()
        
        print()
        print("=" * 60)
        print(" UNINSTALLATION COMPLETE")
        print("=" * 60)
        print()
        print("Bunnimaxx has been completely removed from your system.")
        print("You can now manually delete this uninstaller file.")
        print()
        input("Press Enter to exit...")

if __name__ == "__main__":
    uninstaller = WindowsNativeUninstaller()
    uninstaller.run_uninstallation()
