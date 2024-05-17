import os
import boto3
import time
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import threading
import uvicorn
from fastapi import FastAPI, Request, Header, HTTPException
from webhooks import line_bot
from utils import s3_uploader, stability_request as stability, camera_control as camera_module, bluetooth

load_dotenv()

class S3Uploader:
    def __init__(self):
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

    def upload(self, file_name):
        file_path = "/pienv/project/assets/" + file_name
        try:
            self.s3_client.upload_file(
                file_path, self.bucket_name, file_name,
                ExtraArgs={'ACL': 'public-read'}
            )
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_name}"
            return url
        except NoCredentialsError:
            raise Exception("S3Credentials not available")
        except Exception as e:
            raise Exception(f"Error: Image upload failed; {e}")

    def delete(self, file_name):
        try:
            response = self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
            return response
        except Exception as e:
            raise Exception(f"Error: Failed to delete file; {e}")

class Application:
    def __init__(self):
        self.msg = line_bot.Message()
        self.camera = camera_module.Camera()  
        self.s3 = s3_uploader.S3Uploader()
        self.user_id = ""
        self.stability = stability.Stability()
        self.camera_running = False
        self.lock = threading.Lock()

    def capture_image_and_process(self):
        with self.lock:
            if self.camera_running:
                result = self.camera.capture_camera(self.user_id)
                if not result:
                    print("Error: Capturing image failed")
                    return False

                #Stability API request
                result = self.stability.request_stability(self.user_id)
                if not result:
                    error_message = f"Error: Stability API request failed; {result}"
                    self.msg.send_error_message(self.user_id)
                    return False

                #Upload to Amazon S3 and get URLs
                original_file = self.user_id + ".jpg"
                generated_file = self.user_id + "_generated.png"
                try:
                    original_image = self.s3.upload(original_file)  
                    generated_image = self.s3.upload(generated_file)
                except FileNotFoundError as e:
                    print(f"Error: File not found; {e}")
                    return False
                
                if original_image and generated_image:
                    if self.msg.send_results(original_image, generated_image, self.user_id):
                        time.sleep(5)
                        self.s3.delete(original_file)
                        self.s3.delete(generated_file)
                        return True
                else:
                    self.msg.send_error_message(self.user_id)
                    return False
            else:
                print("カメラが起動していません。")
                return False

    async def handle_line_request(self, request: Request, x_line_signature: str = Header(None)):
        body = await request.body()
        verify_signature = line_bot.VerifySignature(x_line_signature)
        if not verify_signature.verify_signature(body):
            raise HTTPException(status_code=400, detail="Invalid signature")

        d_json = await request.json()
        reply_token = await self.msg.receive(d_json)
        if reply_token:
            self.user_id = d_json['events'][0]['source']['userId']
            e = self.camera.start_camera()
            if not e:
                error_message = "Error: Starting camera failed"
                self.msg.send_error_message("起動に失敗しました。リトライしてください", reply_token)
                print("カメラの起動に失敗しました")
                return
            
            self.camera_running = True
            await self.msg.reply("起動に成功しました", reply_token)
            print("カメラが正常に起動しました")

app = FastAPI()
app_instance = Application()

@app.post("/")
async def handle_line_request(request: Request, x_line_signature: str = Header(None)):
    return await app_instance.handle_line_request(request, x_line_signature)

def run_uvicorn():
    while True:
        try:
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except Exception as e:
            print(f"Uvicorn server crashed: {e}")
            print("Restarting Uvicorn server...")
            
def listen_for_bluetooth():
    while True:
        try:
            listener = bluetooth.BluetoothListener(app_instance.capture_image_and_process)
            listener.listen_for_button_presses()
        except Exception as e:
            print(f"Bluetooth listener crashed: {e}")
            print("Restarting Bluetooth listener...")

if __name__ == "__main__":
    uvicorn_thread = threading.Thread(target=run_uvicorn)
    bluetooth_thread = threading.Thread(target=listen_for_bluetooth)

    uvicorn_thread.start()
    bluetooth_thread.start()

    uvicorn_thread.join()
    bluetooth_thread.join()
