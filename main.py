# This code is without the Rekognition module

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
        return False
    return "complete"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        with open(UPLOAD_FOLDER + filename, 'rb') as source_image:
            global source_bytes
            source_bytes = source_image.read()

        #print('upload_image filename: ' + filename)
        #flash('Image successfully uploaded and displayed below')
        # return render_template('index.html', filename=filename)

        session = boto3.Session(region_name='us-east-1')

        s3 = session.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        
        rekognition = boto3.Session(region_name='us-east-1').client('rekognition'
                            , aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        # Upload the file
        try:
            response = s3.upload_file(
                UPLOAD_FOLDER + filename, 'combustifierbucket', filename)
            rekognition_response = rekognition.detect_labels(Image={
                'S3Object': {
                    'Bucket': 'combustifierbucket',
                    'Name': filename
                }
            },
            MaxLabels=100,
            MinConfidence=70)
            print(rekognition_response)
        except ClientError as e:
            print(e)
            return False
        #return response and rekognition_response in a json
        return jsonify(
            {
                'rekognition_response': rekognition_response,
                's3_response': response
            }
        )

        #print('upload_image filename: ' + filename)
        #flash('Image successfully uploaded and displayed below')
        # return render_template('index.html', filename=filename)



@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0')
