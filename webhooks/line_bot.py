import base64
import hashlib
import hmac
import os
import requests
import json
from dotenv import load_dotenv

class AccessToken:
    def __init__(self):
        load_dotenv()
        self.base_domain = 'https://api.line.me'
        self.access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
        self.channel_secret = os.getenv('CHANNEL_SECRET')

class VerifySignature(AccessToken):
    def __init__(self, l_signature):
        super().__init__()
        self.l_signature = l_signature

    def verify_signature(self, body):
        hash = hmac.new(self.channel_secret.encode('utf-8'), body, hashlib.sha256).digest()
        signature = base64.b64encode(hash).decode('utf-8')
        return hmac.compare_digest(signature, self.l_signature)

class Message(AccessToken):
    def __init__(self):
        super().__init__()

    async def receive(self, d_json):
        events = d_json['events']
        for event in events:
            mode = event['mode']
            reply_token = event['replyToken']
            message = event['message']
            message_type = message['type']
            if message_type == 'text':
                if message['text'] == 'カメラ' and mode == 'active':
                    return reply_token
            else:
                return False
    
    async def reply(self, message, reply_token):
        content = [{'type': 'text', 'text': message}]
        url = "https://api.line.me/v2/bot/message/reply"
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.access_token}'}
        data = {'messages': content, 'replyToken': reply_token}
        r = requests.post(url=url, headers=headers, data=json.dumps(data))
        r_json = r.json()
        if 'error' not in r_json:
            return True
        else:
            status_code = r.status_code
            r_json['status_code'] = status_code
            raise HTTPException(status_code=status_code, detail=r_json)
            return False

    def send_results(self, original_image, generated_image, user_id):
        url = "https://api.line.me/v2/bot/message/push"
        text_message = "遊んでくれてありがとうございました！"
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}
        body = {
            'to': user_id,
            'messages': [
                {'type': "image", 'originalContentUrl': original_image, 'previewImageUrl': original_image},
                {'type': "image", 'originalContentUrl': generated_image, 'previewImageUrl': generated_image},
                {'type': "text", 'text': text_message}
            ]
        }
        response = requests.post(url, headers=headers, data=json.dumps(body))
        if 'error' not in response.json():
            return True
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        
    def send_error_message(self, user_id, reply_token):
        error_message = "不具合が発生しています。お近くのスタッフまでお声がけください $"
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}
        if reply_token == None:
            url = "https://api.line.me/v2/bot/message/push"
            body = {
                'to': user_id,
                'messages': [
                    {
                        'type': "text",
                        'text': error_message,
                        'emojis': [
                            {'index': 0, 'productId': "5ac1bfd5040ab15980c9b435", 'emojiId': "005"}
                        ]
                    }
                ]
            }
        else:
            url = "https://api.line.me/v2/bot/message/reply"
            body = {
                'replyToken': reply_token,
                'messages': [
                    {
                        'type': "text",
                        'text': error_message,
                        'emojis': [
                            {'index': 0, 'productId': "5ac1bfd5040ab15980c9b435", 'emojiId': "005"}
                        ]
                    }
                ]
            }
        response = requests.post(url, headers=headers, data=json.dumps(body))
        if 'error' not in response.json():
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
