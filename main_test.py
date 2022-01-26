# This code is without the Rekognition module
import base64
import uuid
from PIL import Image
from io import BytesIO
import csv
import boto3
from flask import Flask, flash, request, redirect, url_for, render_template, jsonify
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import urllib.request
import os

from werkzeug.utils import secure_filename
load_dotenv()
app = Flask(__name__)

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

UPLOAD_FOLDER = 'static/uploads/'
key = "/.aws/credentials"
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

####s3 part #####


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        return f"Error: {e}"
    return "complete"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    # make uuid
    uid = str(uuid.uuid4())
    image = request.json['img']
    image = Image.open(BytesIO(base64.b64decode(image)))
    image.save('tmp.png', 'PNG')
    session = boto3.Session(region_name='ap-southeast-1')
    s3 = session.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    rekognition = boto3.Session(region_name='ap-southeast-1').client('rekognition', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    try:
        s3.upload_file('tmp.png', 'combustifiertoasterclock', f'{uid}.png')


        rekognition_response = rekognition.detect_labels(Image={
            'S3Object': {
                'Bucket': 'combustifiertoasterclock',
                'Name': f'{uid}.png'
            }
        },
            MaxLabels=100,
            MinConfidence=70)
    except ClientError as e:
        print(e)
        return f"Error: {e}"
    rekognition_response = rekognition_response['Labels']
    #get avg confidence
    avg_confidence = 0
    for label in rekognition_response:
        avg_confidence += label['Confidence']
    avg_confidence = avg_confidence / len(rekognition_response)
    names = []
    for i in rekognition_response:
        names.append(i['Name'].lower())
    #return key value pairs
    print(names)
    #open combustiblelist.txt
    combustible_count = 0
    with open("combustiblelist.txt") as file:
        lines = [line.strip() for line in file]  
        print(lines)
    for i in lines:
        if i in names:
            print(i)
            combustible_count += 1
    
    if combustible_count > 0:
        combustibility = "Yes"
    else:
        combustibility = "No"

    return jsonify({'names': names, 'confidence': avg_confidence, 'combustibility': combustibility})


@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0')
