import os
import uuid
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from decouple import config

logger = logging.getLogger(__name__)

def upload_file_to_s3(file_obj, folder="heritage/audio"):
    """
    Uploads a file to AWS S3 using boto3.
    If AWS credentials are missing or default placeholders, falls back to Django local storage.
    Returns the absolute public URL of the uploaded file.
    """
    aws_access_key = config('AWS_ACCESS_KEY_ID', default='').strip()
    aws_secret_key = config('AWS_SECRET_ACCESS_KEY', default='').strip()
    bucket_name = config('AWS_STORAGE_BUCKET_NAME', default='').strip()
    region_name = config('AWS_S3_REGION_NAME', default='ap-south-1').strip()
    custom_domain = config('AWS_S3_CUSTOM_DOMAIN', default='').strip()

    # Generate a unique clean filename
    ext = os.path.splitext(file_obj.name)[1].lower()
    if not ext:
        ext = '.mp3' if 'audio' in folder else '.jpg'
    filename = f"{folder}/{uuid.uuid4().hex}{ext}"

    # Check if AWS credentials are valid and not placeholders
    has_valid_aws = (
        aws_access_key and 
        aws_secret_key and 
        bucket_name and 
        not aws_access_key.startswith('AKIAXXXXX') and 
        not aws_access_key.startswith('your_aws')
    )

    if has_valid_aws:
        try:
            import boto3
            from botocore.exceptions import BotoCoreError, ClientError

            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region_name
            )

            # Determine content type
            content_type = file_obj.content_type if hasattr(file_obj, 'content_type') else 'application/octet-stream'

            # Upload to S3
            s3_client.upload_fileobj(
                file_obj,
                bucket_name,
                filename,
                ExtraArgs={'ContentType': content_type}
            )

            if custom_domain:
                url = f"https://{custom_domain}/{filename}"
            else:
                url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{filename}"
            
            logger.info(f"Successfully uploaded file to AWS S3: {url}")
            return url

        except Exception as e:
            logger.warning(f"AWS S3 upload failed ({str(e)}). Falling back to Django local storage.")

    # Fallback to local storage
    saved_path = default_storage.save(filename, ContentFile(file_obj.read()))
    media_url = settings.MEDIA_URL.rstrip('/')
    full_path = f"/{media_url}/{saved_path}".replace('//', '/')
    logger.info(f"Saved file to local media storage: {full_path}")
    return full_path
