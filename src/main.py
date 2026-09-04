import tkinter as tk
import ctypes
import time
import threading
import wmi
from pynput import keyboard
from wifi_radar import WifiRadar
from hardware_guard import HardwareGuard

class BunnimaxxDeskUSB:
    def __init__(self):
        self.keystroke_times = []
        self.threshold = 30
        self.is_locked = False
        self.user32 = ctypes.windll.user32
        self.c = wmi.WMI()
        
        self.root = tk.Tk()
        self.root.title("BUNNIMAXX :: FULL SHIELD")
        self.root.geometry("600x400")
        self.root.configure(bg="#1a1a1a")
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.label = tk.Label(
            self.root,
            text="BUNNIMAXX SHIELD ACTIVE\n\n"
                 "[USB] Monitoring HID Input...\n"
                 "[WIFI] Scanning for threats...\n"
                 "[HARDWARE] Scanning NFC/RFID/U2F/IR...\n\n"
                 "Waiting for anomalies.",
            fg="#FF8C00",
            bg="#1a1a1a",
            font=("Courier", 11, "bold"),
            justify="center"
        )
        self.label.pack(expand=True)
        
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
        self.wifi_radar = WifiRadar(callback=self.on_wifi_threat)
        self.wifi_radar.start()
        
        self.hardware_guard = HardwareGuard(callback=self.on_hardware_threat)
        self.hardware_guard.start()
        
        self.root.mainloop()

    def on_press(self, key):
        if self.is_locked:
            return
            
        current_time = time.time()
        self.keystroke_times.append(current_time)
        self.keystroke_times = [t for t in self.keystroke_times if current_time - t < 1.0]
        
        speed = len(self.keystroke_times)
        
        if speed >= self.threshold:
            self.root.after(0, self.trigger_psychological_warfare)

    def on_wifi_threat(self, threats):
        if threats:
            self.root.after(0, lambda: self.show_wifi_alert(threats))
        else:
            self.root.after(0, self.reset_ui)

    def on_hardware_threat(self, threats, neutralized):
        """
        Callback dari HardwareGuard kalau ada device mencurigakan
        """
        if threats:
            self.root.after(0, lambda: self.show_hardware_alert(threats, neutralized))
        else:
            self.root.after(0, self.reset_ui)

    def show_hardware_alert(self, threats, neutralized):
        """
        Tampilkan alert hardware threat di UI
        """
        self.is_locked = True
        
        threat_messages = []
        for threat in threats:
            threat_messages.append(threat['message'])
        
        alert_text = "\n".join(threat_messages[:2]) 
        
        if neutralized:
            neutralized_text = "\n DISABLED: " + ", ".join(neutralized)
        else:
            neutralized_text = ""
        
        self.root.configure(bg="#FF4500")
        self.label.config(
            text=f" HARDWARE THREAT DETECTED \n\n{alert_text}\n{neutralized_text}\n\n"
                 "NFC/RFID/U2F/IR device blocked.\n"
                 "System protected. 🐰",
            fg="white",
            bg="#FF4500"
        )
        print(f"[BUNNIMAXX] Hardware Threat: {threats}")
        print(f"[BUNNIMAXX] Neutralized: {neutralized}")

    def show_wifi_alert(self, threats):
        self.is_locked = True
        
        threat_messages = []
        for threat in threats:
            threat_messages.append(threat['message'])
        
        alert_text = "\n".join(threat_messages[:3])
        
        self.root.configure(bg="#FF4500")
        self.label.config(
            text=f" WI-FI THREAT DETECTED \n\n{alert_text}\n\n"
                 "ESP32/Flipper Zero nearby?\n"
                 "Check your Wi-Fi connections.\n\n"
                 "Stay safe. ",
            fg="white",
            bg="#FF4500"
        )
        print(f"[BUNNIMAXX] Wi-Fi Threat: {threats}")

    def eject_suspicious_usb(self):
        try:
            for device in self.c.Win32_PnPEntity():
                if device.Name and "HID" in str(device.Name) and "Keyboard" in str(device.Name):
                    print(f"[BUNNIMAXX] Found HID Device: {device.Name} | ID: {device.DeviceID}")
                    result = device.Disable()
                    if result[0] == 0:
                        print(f"[BUNNIMAXX] Device DISABLED: {device.Name}")
                    else:
                        print(f"[BUNNIMAXX] Failed to disable: {device.Name} (Code: {result[0]})")
        except Exception as e:
            print(f"[BUNNIMAXX] Error during USB eject: {e}")

    def trigger_psychological_warfare(self):
        if self.is_locked:
            return
            
        self.is_locked = True
        print("[BUNNIMAXX] BADUSB DETECTED! INITIATING PSYCHOLOGICAL WARFARE...")
        
        self.eject_suspicious_usb()
        
        self.root.withdraw()
        
        self.psych_window = tk.Toplevel(self.root)
        self.psych_window.attributes('-fullscreen', True)
        self.psych_window.attributes('-topmost', True)
        self.psych_window.configure(bg="#FF8C00")
        
        psych_label = tk.Label(
            self.psych_window,
            text=" BUNNIMAXX SHIELD \n\n"
                 "This window will disappear in 20 seconds...",
            fg="black",
            bg="#FF8C00",
            font=("Courier", 24, "bold"),
            justify="center"
        )
        psych_label.pack(expand=True)
        
        print("[BUNNIMAXX]  Window proggress activated. 20 seconds countdown...")
        
        threading.Thread(target=self.auto_close_psych_window, daemon=True).start()

    def auto_close_psych_window(self):
        time.sleep(20)
        print("[BUNNIMAXX] Psychological Warfare Window closed. System safe.")
        self.root.after(0, self.close_psych_window)

    def close_psych_window(self):
        if hasattr(self, 'psych_window') and self.psych_window:
            self.psych_window.destroy()
            self.psych_window = None
        self.root.deiconify()
        self.reset_ui()

    def reset_ui(self):
        self.is_locked = False
        self.keystroke_times = []
        self.root.configure(bg="#1a1a1a")
        self.label.config(
            text="BUNNIMAXX SHIELD ACTIVE\n\n"
                 "[USB] Monitoring HID Input...\n"
                 "[WIFI] Scanning for threats...\n"
                 "[HARDWARE] Scanning NFC/RFID/U2F/IR...\n\n"
                 "Waiting for anomalies.",
            fg="#FF8C00",
            bg="#1a1a1a"
        )

    def on_closing(self):
        self.wifi_radar.stop()
        self.hardware_guard.stop()
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    print("========================================")
    print(" BUNNIMAXX :: FULL SHIELD")
    print("========================================")
    print("Modules:")
    print("  - USB Defense (BadUSB Detection)")
    print("  - Wi-Fi Radar (ESP32/Deauth)")
    print("  - Hardware Guard (NFC/RFID/U2F/IR)")
    print("========================================")
    print("NOTE: Run as Administrator for USB eject.")
    print("========================================")
    app = BunnimaxxDeskUSB()
