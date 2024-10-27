import flask
from flask import request
import os
from bot import ObjectDetectionBot
import boto3
from botocore.exceptions import ClientError
import json

aws_region  =   os.getenv("AWS_REGION")
dynamodb_table=os.getenv("DYNAMODB_TABLE")
alb_url =   os.getenv("ALB_URL")

def get_secret():

    secret_name = "telegram_token"
    region_name = aws_region

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    secret = json.loads(secret)
    return secret["telegram_token"]


app = flask.Flask(__name__)

dynamodb = boto3.resource('dynamodb', region_name=aws_region)
# TODO load TELEGRAM_TOKEN value from Secret Manager
TELEGRAM_TOKEN = get_secret()

TELEGRAM_APP_URL = f'https://{alb_url}:8443'


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


@app.route(f'/results', methods=['POST'])
def results():
    prediction_id = request.args.get('prediction_id')
    table = dynamodb.Table(dynamodb_table)

    response= table.get_item(Key={'prediction_id':prediction_id})
    class_counts={}

    chat_id = int(response['Item']['chat_id'])
    labels=response['Item']['labels']
    for x in labels:
        name = x['class']
        if name in class_counts:
            class_counts[name] += 1
        else:
            class_counts[name] = 1 
    print(class_counts)
    text_results=[]
    for name,count in class_counts.items():
        text_results.append(f"There are {count} {name}(s).")
    result_message = "\n".join(text_results)
    #text_results =response['Item']['labels'][0]['class']

    bot.send_text(chat_id, result_message)
    return 'Ok'


@app.route(f'/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)
