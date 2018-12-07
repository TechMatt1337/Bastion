
# coding: utf-8

# Face Recognition with OpenCV

# To detect faces, I will use the code from my previous article on [face detection](https://www.superdatascience.com/opencv-face-detection/). So if you have not read it, I encourage you to do so to understand how face detection works and its Python coding. 

#import OpenCV module
import cv2
#import os module for reading training data directories and paths
import os
#import numpy to convert python lists to numpy arrays as 
#it is needed by OpenCV face recognizers
import numpy as np
#Kinect driver API
import freenect
#Deincode the incoming models
import base64
#Depickle the incoming model
import pickle
# importing the requests library 
import requests
#Get timestamp
import time

# api-endpoint
URL_API = "http://ec2-18-223-248-15.us-east-2.compute.amazonaws.com/api"
URL_MOD = "http://ec2-18-223-248-15.us-east-2.compute.amazonaws.com/api/model"

# target list
targets = {}
# create our LBPH face recognizer 
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
#or use EigenFaceRecognizer by replacing above line with 
#face_recognizer = cv2.face.EigenFaceRecognizer_create()
#or use FisherFaceRecognizer by replacing above line with 
#face_recognizer = cv2.face.FisherFaceRecognizer_create()
# names labels
labels = []

#Query the API to update the targeting model if required
def query_api(timestamp):
    flag = 0

    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'lastupdate':timestamp}

    # sending get request and saving the response as response object
    r = requests.get(url = URL_API, params = PARAMS)

    # extracting data in json format
    data = r.json()

    # If there are target updates, make the required changes
    if data['target_updates'] != None:
        for entry in data['target_updates']:
            name = entry['last_name'] + " " + entry['first_name']
            targets[name] = entry['is_target']
        flag = 1

    #If there is a model change, make the new model
    if data['new_model'] == True:
        #Query for new model
        r = requests.get(url = URL_MOD, params = PARAMS)
        
        #extract data
        data = r.json()
        
        #Sanity check
        if data['model'] != None:
            #Decode the data
            buff = base64.decode(data['model'])
            info = pickle.loads(buff)

            #Load the new targeting labels
            labels = info['names']

            #Load the new model
            face_recognizer.loadFromString(info['model'])
            flag = 2

    return flag

#function to detect face using OpenCV
def detect_face(img):
    #convert the test image to gray image as opencv face detector expects gray images
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #cv2.imshow("Training on image...", cv2.resize(gray, (400, 500)))
    #cv2.waitKey(100)

    #load OpenCV face detector, I am using LBP which is fast
    #there is also a more accurate but slow Haar classifier
    face_cascade = cv2.CascadeClassifier('opencv-files/lbpcascade_frontalface.xml')

    #let's detect multiscale (some images may be closer to camera than others) images
    #result is a list of faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);
    
    #if no faces are detected then return original img
    if (len(faces) == 0):
        return None, None
    
    #under the assumption that there will be only one face,
    #extract the face area
    (x, y, w, h) = faces[0]
    
    #return only the face part of the image
    return gray[y:y+w, x:x+h], faces[0]

#this function recognizes the person in image passed
#and draws a rectangle around detected face with name of the 
#subject
def predict(img):
    if img is not None:
        #make a copy of the image as we don't want to chang original image
        #img = test_img.copy()
        #detect face from the image
        face, rect = detect_face(img)
        
        if face is None:
                print("No face found!")
                return None

        #predict the image using our face recognizer 
        label, confidence = face_recognizer.predict(face)
        #get name of respective label returned by face recognizer
        label_text = labels[label];
        
        #draw a rectangle around face detected
        #draw_rectangle(img, rect)
        #draw name of predicted person
        #draw_text(img, label_text, rect[0], rect[1]-5)
        #print("I found " + str(label_text) + " with " + str(confidence) + " confidence!")
        return (label_text, rect, confidence)

#Get frame from kinect and scale down resolution for speed purposes
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
    #Original image is 640x480
    dim = (320,240)
    dst = cv2.resize(array,dim)
    return dst

#Tracker code from: https://www.learnopencv.com/object-tracking-using-opencv-cpp-python/
def create_tracker():
    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
    #Normally use KCF, shouldn't use anything above that
    tracker_type = tracker_types[2]

    if tracker_type == 'BOOSTING':
        track = cv2.TrackerBoosting_create()
    if tracker_type == 'MIL':
        track = cv2.TrackerMIL_create()
    if tracker_type == 'KCF':
        track = cv2.TrackerKCF_create()
    if tracker_type == 'TLD':
        track = cv2.TrackerTLD_create()
    if tracker_type == 'MEDIANFLOW':
        track = cv2.TrackerMedianFlow_create()
    if tracker_type == 'GOTURN':
        track = cv2.TrackerGOTURN_create()
    if tracker_type == 'MOSSE':
        track = cv2.TrackerMOSSE_create()
    if tracker_type == "CSRT":
        track = cv2.TrackerCSRT_create()
    return track

# Need to seed model
while query_api(0) != 2:
    continue

#Need to keep track of the previous timestamp in order to query every x seconds
prev_time = int(round(time.time() * 1000))

#perform a prediction
while 1:
    frame = get_video()

    result = predict(frame)

    #The second condition is the check for the confidence of the recognition, so that there aren't so many false positives
    if result is not None and result[2] < 115:
        #We found a face, parse it out
        identity = result[0]
        #Only attack a designated target
        if targets[identity] == 1:
            bbox = (result[1][0], result[1][1], result[1][0] + result[1][2], result[1][1] + result[1][3])
            
            #Initialize the tracker
            tracker = create_tracker()
            ok = tracker.init(frame, bbox)
            while ok:
                #Determine X and Y angles 
                mid_face = (bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2)

                #print("BOUNDS: " + str(mid_face[0]) + "," + str(mid_face[1]))

                #https://stackoverflow.com/questions/37642834/opencv-how-to-calculate-the-degreesangles-of-an-object-with-its-coordinates
                #The Kinect v1 image is 640 pixels in width and 480 in height
                #The horizontal FOV is 62 degrees and the vertical FOV is 48.6
                #The pixels have been halved in each dimension
                
                x_angle = np.arctan((mid_face[0] - 160) * (np.tan(31.0/180) / 160)) * 180
                y_angle = np.arctan((mid_face[1] - 120) * (np.tan(24.3/180) / 120)) * 180
                #x_angle = (mid_face[0] - 160) * (62/320)
                #y_angle = (mid_face[1] - 120) * (48.6/240)
                #print("X/Y ANGLES: " + str(x_angle) + "," + str(y_angle))

                #
                # MOVE MOTORS HERE!!!!!
                #

                #Grab frame
                frame = get_video()
                if frame is None:
                    continue

                #update tracker
                ok, bbox = tracker.update(frame)

    #
    #  QUERY API ON SOME INTERVAL HERE!!!
    #

    timestamp = int(round(time.time() * 1000))
    #Query API every 20 seconds
    if timestamp > prev_time + 20000:
        query_api(timestamp)
        prev_time = timestamp
