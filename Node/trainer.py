#Interface with SQL Database
import sqlite3
#Pickle objects
import pickle
#CV to train
import cv2
#Unbase 64 encode images
import base64
import sys

#function to detect face using OpenCV
def detect_face(img):
    #convert the test image to gray image as opencv face detector expects gray images
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #Workaround because all the faces are sideways
    #(h,w) = img.shape[:2]
    #M = cv2.getRotationMatrix2D((w/2, h/2), 270, 1.0)
    #gray = cv2.warpAffine(gray, M, (h,w))

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
faces = []

#Read all face/labels into lists
#LAST FIRST, I0, ..., LAST_UPDATED
for row in c.execute('SELECT * FROM images'):
    label = row[0] + " " + row[1]
    for i in range(2,9):
        face, rect = detect_face(row[i])

        if face is not None:
            labels.append(label)
            faces.append(face)

    if labels[:-1] != label:
        print("Unable to get good face of " + label)
        sys.exit()

#create our LBPH face recognizer 
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
#face_recognizer = cv2.face.createLBPHFaceRecognizer()

#or use EigenFaceRecognizer by replacing above line with 
#face_recognizer = cv2.face.EigenFaceRecognizer_create()

#or use FisherFaceRecognizer by replacing above line with 
#face_recognizer = cv2.face.FisherFaceRecognizer_create()

#train our face recognizer of our training faces
face_recognizer.train(faces, np.array(labels))

print(pickle.dumps(face_recognizer))
