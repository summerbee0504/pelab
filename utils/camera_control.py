from picamera2 import Picamera2
import os

class Camera:
    def __init__(self):
        self.camera = Picamera2()
        self.save_directory = "/pienv/project/assets"

    def start_camera(self):
        try:
            self.camera.start()
            return True
        except Exception as e:
            print(f"Failed to start camera: {e}")
            return False

    def capture_camera(self, user_id):
        try:
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)
            image_path = os.path.join(self.save_directory, f"{user_id}.jpg")
            self.camera.capture_file(image_path)
            return True
        except Exception as e:
            raise Exception(f"Error: Capture image failed; {e}")
