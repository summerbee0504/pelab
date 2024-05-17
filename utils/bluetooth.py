import evdev
import os

class BluetoothListener:
    def __init__(self, callback):
        self.callback = callback
        self.device_name = "BT Shutter"

    def find_device(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if self.device_name in device.name:
                return device
        raise FileNotFoundError(f"Device with name '{self.device_name}' not found.")

    def listen_for_button_presses(self):
        key_press_times = {}
        try:
            device = self.find_device()
            print(f"Listening on device: {device}")
        except FileNotFoundError as e:
            print(e)
            return

        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                key_event = evdev.ecodes.KEY[event.code]
                
                if event.value == 1:  # Key down
                    key_press_times[event.code] = event.timestamp()
                
                elif event.value == 0:  # Key up
                    press_time = key_press_times.pop(event.code, None)
                    if press_time is not None:
                        duration = event.timestamp() - press_time
                        if duration > 1:  # Long press (greater than 1 second)
                            print(f"Long press detected. Duration: {duration:.2f}s. Shutting down...")
                            os.system("sudo shutdown now")
                        else:  # Short press (1 second or less)
                            print(f"Short press detected. Duration: {duration:.2f}s.")
                            self.callback()

def button_press_callback():
    print("Button pressed callback executed.")

if __name__ == "__main__":
    listener = BluetoothListener(button_press_callback)
    listener.listen_for_button_presses()
