import wmi
import time
import threading

class HardwareGuard:
    def __init__(self, callback=None):
        self.c = wmi.WMI()
        self.callback = callback
        self.is_running = False
        self.threat_detected = False
        
        self.blacklist_keywords = [
            'acr122', 'pn532', 'proxmark', 'rcs', 'contactless', 'nfc reader',
            'rfid reader', 'smart card reader', 'iso14443', 'mifare',
            'yubikey', 'fido', 'u2f', 'security key', 'solokey', 'nitrokey',
            'infrared', 'ir receiver', 'ir transmitter', 'ir blaster',
            'flipper', 'microlord',
            'badusb', 'rubber ducky', 'teensy', 'digispark',
        ]
        
        self.whitelist_keywords = [
            'asus', 'ps/2', 'synaptics', 'elantech', 'touchpad',
        ]
    
    def scan_usb_devices(self):
        devices = []
        try:
            for device in self.c.Win32_PnPEntity():
                if device.DeviceID and 'USB' in device.DeviceID:
                    device_info = {
                        'name': device.Name or 'Unknown',
                        'device_id': device.DeviceID,
                        'status': device.Status,
                        'class': device.PNPClass,
                        'manufacturer': device.Manufacturer or 'Unknown',
                    }
                    devices.append(device_info)
        except Exception as e:
            print(f"[HARDWARE GUARD] Error scanning USB: {e}")
        
        return devices
    
    def is_device_suspicious(self, device_info):
        device_name = device_info['name'].lower()
        device_id = device_info['device_id'].lower()
        manufacturer = device_info['manufacturer'].lower()
        
        for whitelist in self.whitelist_keywords:
            if whitelist in device_name or whitelist in manufacturer:
                return False
        
        for blacklist in self.blacklist_keywords:
            if blacklist in device_name or blacklist in device_id or blacklist in manufacturer:
                return True
        
        if device_info['class'] in ['SmartCardReader', 'Media', 'HIDClass']:
            if 'keyboard' not in device_name.lower() and 'mouse' not in device_name.lower():
                return True
        
        return False
    
    def disable_device(self, device_info):
        try:
            device_id = device_info['device_id']
            
            for device in self.c.Win32_PnPEntity(DeviceID=device_id):
                result = device.Disable()
                if result[0] == 0:
                    print(f"[HARDWARE GUARD]  Device DISABLED: {device_info['name']}")
                    return True
                else:
                    print(f"[HARDWARE GUARD]  Failed to disable: {device_info['name']} (Code: {result[0]})")
                    return False
            
        except Exception as e:
            print(f"[HARDWARE GUARD] Error disabling device: {e}")
        
        return False
    
    def detect_threats(self):
        devices = self.scan_usb_devices()
        threats = []
        
        for device in devices:
            if self.is_device_suspicious(device):
                threats.append({
                    'type': 'SUSPICIOUS_HARDWARE',
                    'device': device,
                    'message': f" SUSPICIOUS DEVICE: {device['name']}\n"
                              f"Manufacturer: {device['manufacturer']}\n"
                              f"Class: {device['class']}\n"
                              f"Status: {device['status']}"
                })
        
        return threats
    
    def neutralize_threats(self, threats):
        neutralized = []
        for threat in threats:
            device = threat['device']
            if self.disable_device(device):
                neutralized.append(device['name'])
        
        return neutralized
    
    def monitor_loop(self):
        self.is_running = True
        scan_interval = 3
        
        while self.is_running:
            threats = self.detect_threats()
            
            if threats and not self.threat_detected:
                self.threat_detected = True
                neutralized = self.neutralize_threats(threats)
                
                if self.callback:
                    self.callback(threats, neutralized)
            
            elif not threats and self.threat_detected:
                self.threat_detected = False
                if self.callback:
                    self.callback([], [])
            
            time.sleep(scan_interval)
    
    def start(self):
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        print("[HARDWARE GUARD] Started monitoring USB devices (NFC/RFID/U2F/IR)...")
    
    def stop(self):
        self.is_running = False
        print("[HARDWARE GUARD] Stopped.")
