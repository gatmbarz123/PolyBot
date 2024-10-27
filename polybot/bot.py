import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

import json

s3_bucket   =   os.getenv("S3_BUCKET")
aws_region  =   os.getenv("AWS_REGION")
sqs_url =   os.getenv("SQS_URL")

class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class ObjectDetectionBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        chat_id = msg['chat']['id']


        if self.is_current_msg_photo(msg):
            photo_path = self.download_user_photo(msg)

    
            # TODO upload photo_path to S3\
            s3 = boto3.client('s3')
            bucket_name = s3_bucket
            image_name = os.path.basename(photo_path)
            key_name = f'{chat_id}/{image_name}'
            s3.upload_file(photo_path, bucket_name, key_name)
            logger.info(f'Image {image_name} uploaded to S3 bucket {bucket_name}.')

            self.send_text(chat_id, "Image successfully uploaded to S3.")

            # TODO send a job to the SQS queue
            sqs_client = boto3.client('sqs' ,region_name=aws_region)
            queue_url = sqs_url

            # Create message body
            message_body = {
                'image_name': key_name,
                'bucket_name': bucket_name,
                'chat_id': chat_id
            }
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message_body)
            )
            logger.info(f'Message sent to SQS queue with response: {response}')
            self.send_text(chat_id, "Your image is being processed. Please wait...")
        else:
            self.send_text(chat_id, "Hi, How can u help you?")
        
            
        
