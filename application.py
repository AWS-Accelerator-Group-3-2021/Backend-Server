import csv
import boto3

from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
 
app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


        with open(UPLOAD_FOLDER + filename,'rb') as source_image:
            global source_bytes
            source_bytes = source_image.read()


      
        #print('upload_image filename: ' + filename)
        #flash('Image successfully uploaded and displayed below')
        #return render_template('index.html', filename=filename)
    
        session = boto3.Session(profile_name='default', region_name='us-east-1')

        #client stuff
        client = session.client('rekognition')

        #with open('./cat.png','rb') as source_image:
        #    base64string = source_image.read()





        response = client.detect_labels(Image ={'Bytes':source_bytes},
                                        MaxLabels =100,   #size of out dict
                                        MinConfidence = 90) # min %level give
        print(response)
        print()
        print()



        labels = response["Labels"]


        allitems = []
        for i in range(len(labels)):
            for x, y in labels[i].items():
                if x == 'Name':
                    allitems.append(y.lower())



        #list of combustible item
        file = open("combustiblelist.csv", "r")
        csv_reader = csv.reader(file)
        combustible_list = []
        for row in csv_reader:
            combustible_list.append(row)


        #find combustible items
        combustible_list_found = []
        non_combustible_list_found = []
        for i in range(len(allitems)):
            if allitems[i] in combustible_list[0]:
                combustible_list_found.append(allitems[i])
            else:
                non_combustible_list_found.append(allitems[i])
        #print("combustible_list_found:",combustible_list_found)
        #print("non_combustible_list_found:",non_combustible_list_found)
        list_items = [combustible_list_found,non_combustible_list_found]


        return render_template('index.html', list_items=list_items)

    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


    
app.run()
