from django.shortcuts import render
from django.template import RequestContext
import pymysql
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import datetime
import os
import cv2
import numpy as np
from keras.utils.np_utils import to_categorical
from keras.layers import  MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D
from keras.models import Sequential
from keras.models import model_from_json

global index
index = 0
global missing_child_classifier
global cascPath
global faceCascade

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def Upload(request):
    if request.method == 'GET':
       return render(request, 'Upload.html', {})

def OfficialLogin(request):
    if request.method == 'POST':
      username = request.POST.get('t1', False)
      password = request.POST.get('t2', False)
      if username == 'admin' and password == 'admin':
       context= {'data':'welcome '+username}
       return render(request, 'OfficialScreen.html', context)
      else:
       context= {'data':'login failed'}
       return render(request, 'Login.html', context)

def ViewUpload(request):
    if request.method == 'GET':
       strdata = '<table border=1 align=center width=100%><tr><th>Upload Person Name</th><th>Child Name</th><th>Contact No</th><th>Found Location</th><th>Child Image <th>Uploaded Date</th><th>Status</th></tr><tr>'
       con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'MissingChildDB',charset='utf8')
       with con:
          cur = con.cursor()
          cur.execute("select * FROM missing")
          rows = cur.fetchall()
          for row in rows: 
             strdata+='<td>'+row[0]+'</td><td>'+str(row[1])+'</td><td>'+row[2]+'</td><td>'+row[3]+'</td><td><img src=/static/photo/'+row[4]+' width=200 height=200></img></td><td>'
             strdata+=str(row[5])+'</td><td>'+str(row[6])+'</td></tr>'
    context= {'data':strdata}
    return render(request, 'ViewUpload.html', context)
    


def UploadAction(request):
     global index
     global missing_child_classifier
     global cascPath
     global faceCascade
     if request.method == 'POST' and request.FILES['t5']:
        output = ''
        person_name = request.POST.get('t1', False)
        child_name = request.POST.get('t2', False)
        contact_no = request.POST.get('t3', False)
        location = request.POST.get('t4', False)
        myfile = request.FILES['t5']
        fs = FileSystemStorage()
        filename = fs.save('C:/Python/MissingChilds/MissingChildApp/static/photo/'+child_name+'.png', myfile)
        #if index == 0:
        cascPath = "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(cascPath)
        #index = 1
        option = 0;
        frame = cv2.imread(filename)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray,1.3,5)
        print("Found {0} faces!".format(len(faces)))
        img = ''
        status = 'Child not found in missing database'
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                img = frame[y:y + h, x:x + w]
                option = 1
        if option == 1:
            with open('model/model.json', "r") as json_file:
                loaded_model_json = json_file.read()
                missing_child_classifier = model_from_json(loaded_model_json)
            missing_child_classifier.load_weights("model/model_weights.h5")
            missing_child_classifier._make_predict_function()   
            img = cv2.resize(img, (64,64))
            im2arr = np.array(img)
            im2arr = im2arr.reshape(1,64,64,3)
            img = np.asarray(im2arr)
            img = img.astype('float32')
            img = img/255
            preds = missing_child_classifier.predict(img)
            if(np.amax(preds) > 0.60):
                status = 'Child found in missing database'
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(filename)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'MissingChildDB',charset='utf8')
        db_cursor = db_connection.cursor()
        query = "INSERT INTO missing(person_name,child_name,contact_no,location,image,upload_date,status) VALUES('"+person_name+"','"+child_name+"','"+contact_no+"','"+location+"','"+filename+"','"+str(current_time)+"','"+status+"')"
        db_cursor.execute(query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        context= {'data':'Thank you for uploading. '+status}
        return render(request, 'Upload.html', context)
        
