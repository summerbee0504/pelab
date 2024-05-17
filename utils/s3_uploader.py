import os
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

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
            #upload files to s3
            self.s3_client.upload_file(
                file_path, self.bucket_name, file_name,
                ExtraArgs={'ACL': 'public-read'}
            )
            #create public url
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
            print(f"Deleted {file_name} from S3")
        except Exception as e:
            raise Exception(f"Error: Failed to delete file from S3; {e}")
        
        file_path = "/pienv/project/assets/" + file_name
        try:
            os.remove(file_path)
            print(f"Local file {file_path} deleted successfully")
        except Exception as e:
            print(f"Error deleting local file {file_path}: {e}")

if __name__ == "__main__":
    uploader = S3Uploader()
    file_name = "example_user_generated.png"
    try:
        # delete file
        response = uploader.delete(file_name)
        print("File deleted successfully")
    except Exception as e:
        print(f"Error: {e}")
