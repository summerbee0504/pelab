import base64
import os
import requests
from dotenv import load_dotenv
load_dotenv()

class Stability:
    def __init__(self):
        self.api_host = 'https://api.stability.ai'
        self.api_key = os.getenv('STABILITY_KEY')
        self.engine_id = 'stable-diffusion-v1-6'
        self.save_directory = '/pienv/project/assets'

    def request_stability(self, user_id):
        original_image_path = os.path.join(self.save_directory, f"{user_id}.jpg")
        response = requests.post(
            f"{self.api_host}/v1/generation/{self.engine_id}/image-to-image",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            files={
                "init_image": open(original_image_path, "rb")
            },
            data={
                "init_image_mode": "IMAGE_STRENGTH",
                "image_strength": 0.35,
                "steps": 50,
                "seed": 0,
                "cfg_scale": 11,
                "samples": 1,
                "style_preset": "cinematic",
                "text_prompts[0][text]": 'Transform the selfie into a highly detailed 3D-rendered anime style. The faces should be smooth and three-dimensional, with large expressive eyes and youthful features. Maintain the original hairstyle, hair color, and clothing, but enhance the hair with detailed visual strands and a stylized look. Keep the background from the original selfie, with realistic lighting and environmental details. Preserve the original composition, ensuring the subjects remain in the same positions and proportions as in the original photo. The overall style should blend lifelike 3D rendering with the stylized charm of anime, resulting in a vibrant, whimsical, and visually appealing image.',
                "text_prompts[0][weight]": 1,
                "text_prompts[1][text]": 'Blurry details, low resolution, flat colors, unrealistic proportions, overly exaggerated features, dark or moody atmosphere, cluttered background, unnatural lighting, deviation from original hair and clothing styles, unnatural facial expressions, flat or lifeless hair.',
                "text_prompts[1][weight]": -1,
            }
        )

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()

        generated_image_path = os.path.join(self.save_directory, f"{user_id}_generated.png")
        
        for i, image in enumerate(data["artifacts"]):
            with open(generated_image_path, "wb") as f:
                f.write(base64.b64decode(image["base64"]))

        return True



if __name__ == "__main__":
    stability = Stability()
    user_id = 'example_user'
    try:
        stability.request_stability(user_id)
        print(f"Image generated successfully: {os.path.join(stability.save_directory, f'{user_id}_generated.png')}")
    except Exception as e:
        print(f"Error: {e}")