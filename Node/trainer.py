#Interface with SQL Database
import sqlite3
#Pickle objects
import pickle
#CV to train
import cv2
#Base64 encode images
import base64
#For exit
import sys
#For numpy arrays
import numpy as np
#For file system interaction
import os

#If you decide to train based on the file system, this code is from the same location as the code in
#OpenCV-Face-Recognition-Python
def prepare_training_data(data_folder_path):
    #------STEP-1--------
    #get the directories (one directory for each subject) in data folder
    dirs = os.listdir(data_folder_path)
    
    #list to hold all subject faces
    faces = []
    #list to hold labels for all subjects
    labels = []
    
    #let's go through each directory and read images within it
    for dir_name in dirs:
        
        #our subject directories start with letter 's' so
        #ignore any non-relevant directories if any
        if not dir_name.startswith("s"):
            continue;
            
        #------STEP-2--------
        #extract label number of subject from dir_name
        #format of dir name = slabel
        #, so removing letter 's' from dir_name will give us label
        label = int(dir_name.replace("s", ""))
        
        #build path of directory containin images for current subject subject
        #sample subject_dir_path = "training-data/s1"
        subject_dir_path = data_folder_path + "/" + dir_name
        
        #get the images names that are inside the given subject directory
        subject_images_names = os.listdir(subject_dir_path)
        
        #------STEP-3--------
        #go through each image name, read image, 
        #detect face and add face to list of faces
        for image_name in subject_images_names:
            #ignore system files like .DS_Store
            if image_name.startswith("."):
                continue;
            
            #build image path
            #sample image path = training-data/s1/1.pgm
            image_path = subject_dir_path + "/" + image_name
            #read image
            image = cv2.imread(image_path)
           
            #display an image window to show the image 
            #cv2.imshow("Training on image...", cv2.resize(image, (400, 500)))
            #cv2.waitKey(100)
            
            #detect face
            face, rect = detect_face(image)
            
            #------STEP-4--------
            #for the purpose of this tutorial
            #we will ignore faces that are not detected
            if face is not None:
                #add face to list of faces
                faces.append(face)
                #add label for this face
                labels.append(label)
            
    #cv2.destroyAllWindows()
    #cv2.waitKey(1)
    #cv2.destroyAllWindows()
    
    return faces, labels

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

#Connect to the database
conn = sqlite3.connect('targets.db')
c = conn.cursor()

labels = []
names = []
faces = []

label = 1

#Read all face/labels into lists
#LAST FIRST, I0, ..., LAST_UPDATED
for row in c.execute('SELECT * FROM images'):
    name = row[0] + " " + row[1]

    for i in range(2,8):
        buff = base64.b64decode(row[i])
        arr = np.asarray(bytearray(buff), dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if frame is None:
                print("I can't even make an image!")
                c.close()
                conn.close()
                sys.exit()

        face, rect = detect_face(frame)

        if face is not None:
            #If a face is detected, add to the training set
            labels.append(label)
            faces.append(face)

    if labels[:-1] != label:
        print("Unable to get good face of " + name)
        c.close()
        conn.close()
        sys.exit()

    names.append(name)
    label = label + 1

#Finish the connection
c.close()
conn.close()

#create our LBPH face recognizer 
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
#face_recognizer = cv2.face.createLBPHFaceRecognizer()

#or use EigenFaceRecognizer by replacing above line with 
#face_recognizer = cv2.face.EigenFaceRecognizer_create()

#or use FisherFaceRecognizer by replacing above line with 
#face_recognizer = cv2.face.FisherFaceRecognizer_create()

#train our face recognizer of our training faces
face_recognizer.train(faces, np.array(labels))

face_recognizer.save("tmp")

#Read in result of the dump and remove the dump
buf = open("tmp").read()
os.remove("tmp")

result = {'model': buf, 'names': names}

#Give result to standard out
print(base64.b64encode(pickle.dumps(result)))
