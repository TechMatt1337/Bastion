
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
#Get information about cv package version
import sys

# ### Training Data

# The more images used in training the better. Normally a lot of images are used for training a face recognizer so that it can learn different looks of the same person, for example with glasses, without glasses, laughing, sad, happy, crying, with beard, without beard etc. To keep our tutorial simple we are going to use only 12 images for each person. 
# 
# So our training data consists of total 2 persons with 12 images of each person. All training data is inside _`training-data`_ folder. _`training-data`_ folder contains one folder for each person and **each folder is named with format `sLabel (e.g. s1, s2)` where label is actually the integer label assigned to that person**. For example folder named s1 means that this folder contains images for person 1. The directory structure tree for training data is as follows:
# 
# ```
# training-data
# |-------------- s1
# |               |-- 1.jpg
# |               |-- ...
# |               |-- 12.jpg
# |-------------- s2
# |               |-- 1.jpg
# |               |-- ...
# |               |-- 12.jpg
# ```
# 
# The _`test-data`_ folder contains images that we will use to test our face recognizer after it has been successfully trained.

# As OpenCV face recognizer accepts labels as integers so we need to define a mapping between integer labels and persons actual names so below I am defining a mapping of persons integer labels and their respective names. 
# 
# **Note:** As we have not assigned `label 0` to any person so **the mapping for label 0 is empty**. 

# In[2]:

#there is no label 0 in our training data so subject name for index/label 0 is empty
subjects = ["", "Andrew Guinn"]


# ### Prepare training data

# You may be wondering why data preparation, right? Well, OpenCV face recognizer accepts data in a specific format. It accepts two vectors, one vector is of faces of all the persons and the second vector is of integer labels for each face so that when processing a face the face recognizer knows which person that particular face belongs too. 
# 
# For example, if we had 2 persons and 2 images for each person. 
# 
# ```
# PERSON-1    PERSON-2   
# 
# img1        img1         
# img2        img2
# ```
# 
# Then the prepare data step will produce following face and label vectors.
# 
# ```
# FACES                        LABELS
# 
# person1_img1_face              1
# person1_img2_face              1
# person2_img1_face              2
# person2_img2_face              2
# ```
# 
# 
# Preparing data step can be further divided into following sub-steps.
# 
# 1. Read all the folder names of subjects/persons provided in training data folder. So for example, in this tutorial we have folder names: `s1, s2`. 
# 2. For each subject, extract label number. **Do you remember that our folders have a special naming convention?** Folder names follow the format `sLabel` where `Label` is an integer representing the label we have assigned to that subject. So for example, folder name `s1` means that the subject has label 1, s2 means subject label is 2 and so on. The label extracted in this step is assigned to each face detected in the next step. 
# 3. Read all the images of the subject, detect face from each image.
# 4. Add each face to faces vector with corresponding subject label (extracted in above step) added to labels vector. 
# 
# **[There should be a visualization for above steps here]**

# Did you read my last article on [face detection](https://www.superdatascience.com/opencv-face-detection/)? No? Then you better do so right now because to detect faces, I am going to use the code from my previous article on [face detection](https://www.superdatascience.com/opencv-face-detection/). So if you have not read it, I encourage you to do so to understand how face detection works and its coding. Below is the same code.

# In[3]:

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

#this function will read all persons' training images, detect face from each image
#and will return two lists of exactly same size, one list 
# of faces and another list of labels for each face
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
            
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    
    return faces, labels


#let's first prepare our training data
#data will be in two lists of same size
#one list will contain all the faces
#and other list will contain respective labels for each face
print("Preparing data...")
faces, labels = prepare_training_data("training-data")
print("Data prepared")

#print total faces and labels
print("Total faces: ", len(faces))
print("Total labels: ", len(labels))


# This was probably the boring part, right? Don't worry, the fun stuff is coming up next. It's time to train our own face recognizer so that once trained it can recognize new faces of the persons it was trained on. Read? Ok then let's train our face recognizer. 

# ### Train Face Recognizer

# As we know, OpenCV comes equipped with three face recognizers.
# 
# 1. EigenFace Recognizer: This can be created with `cv2.face.createEigenFaceRecognizer()`
# 2. FisherFace Recognizer: This can be created with `cv2.face.createFisherFaceRecognizer()`
# 3. Local Binary Patterns Histogram (LBPH): This can be created with `cv2.face.LBPHFisherFaceRecognizer()`
# 
# I am going to use LBPH face recognizer but you can use any face recognizer of your choice. No matter which of the OpenCV's face recognizer you use the code will remain the same. You just have to change one line, the face recognizer initialization line given below. 

#create our LBPH face recognizer 
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
#face_recognizer = cv2.face.createLBPHFaceRecognizer()

#or use EigenFaceRecognizer by replacing above line with 
#face_recognizer = cv2.face.EigenFaceRecognizer_create()

#or use FisherFaceRecognizer by replacing above line with 
#face_recognizer = cv2.face.FisherFaceRecognizer_create()

#train our face recognizer of our training faces
face_recognizer.train(faces, np.array(labels))

#function to draw rectangle on image 
#according to given (x, y) coordinates and 
#given width and heigh
def draw_rectangle(img, rect):
    (x, y, w, h) = rect
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
#function to draw text on give image starting from
#passed (x, y) coordinates. 
def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)


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
        label_text = subjects[label];
        
        #draw a rectangle around face detected
        #draw_rectangle(img, rect)
        #draw name of predicted person
        #draw_text(img, label_text, rect[0], rect[1]-5)
        print("I found " + str(label_text) + " with " + str(confidence) + " confidence!")
        return (label_text, rect, confidence)

#Get frame from kinect and scale down resolution for speed purposes
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
    #Original image is 640x480
    dim = (320,240)
    dst = cv2.resize(array,dim)
    return dst

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

#Tracker code from: https://www.learnopencv.com/object-tracking-using-opencv-cpp-python/
print("Initializing tracker...")

def create_tracker():
    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
    #Normally use KCF, shouldn't use anything above that
    tracker_type = tracker_types[2]

    #if int(minor_ver) < 3:
    #    track = cv2.Tracker_create(tracker_type)
    #else:
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

#load test images
#test_img1 = cv2.imread("test-data/test1.jpg")
#test_img2 = cv2.imread("test-data/test2.jpg")

#perform a prediction
while 1:
    frame = get_video()

    result = predict(frame)

    #The second condition is the check for the confidence of the recognition, so that there aren't so many false positives
    if result is not None and result[2] < 115:
        #We found a face, parse it out
        identity = result[0]
        bbox = (result[1][0], result[1][1], result[1][0] + result[1][2], result[1][1] + result[1][3])
        
        #Initialize the tracker
        tracker = create_tracker()
        ok = tracker.init(frame, bbox)
        while ok:
            #Determine X and Y angles 
            mid_face = (bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2)

            print("BOUNDS: " + str(mid_face[0]) + "," + str(mid_face[1]))

            #https://stackoverflow.com/questions/37642834/opencv-how-to-calculate-the-degreesangles-of-an-object-with-its-coordinates
            #The Kinect v1 image is 640 pixels in width and 480 in height
            #The horizontal FOV is 62 degrees and the vertical FOV is 48.6
            #The pixels have been halved in each dimension
            
            x_angle = np.arctan((mid_face[0] - 160) * (np.tan(31.0/180) / 160)) * 180
            y_angle = np.arctan((mid_face[1] - 120) * (np.tan(24.3/180) / 120)) * 180
            #x_angle = (mid_face[0] - 160) * (62/320)
            #y_angle = (mid_face[1] - 120) * (48.6/240)
            print("X/Y ANGLES: " + str(x_angle) + "," + str(y_angle))

            #
            # MOVE MOTORS HERE!!!!!
            #

            #Grab frame
            frame = get_video()
            if frame is None:
                continue

            #update tracker
            ok, bbox = tracker.update(frame)

            #This code draws each frame - warning - terrible performance
            '''if ok:
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
                cv2.namedWindow('image', cv2.WINDOW_NORMAL)
                cv2.imshow('image', frame)
                cv2.resizeWindow('image', frame.shape[0], frame.shape[1])
                k = cv2.waitKey(5) & 0xFF
                if k == 27:
                    break'''

    #
    #  QUERY API ON SOME INTERVAL HERE!!!
    #

    #print("Prediction complete")
    '''k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break'''

cv2.destroyAllWindows()
#display both images
#cv2.imshow(subjects[1], cv2.resize(predicted_img1, (400, 500)))
#print("Found face at " + str(bbox[0] + bbox[2] / 2) + ", " + str(bbox[1] + bbox[3] / 2))
#cv2.imshow(subjects[2], cv2.resize(predicted_img2, (400, 500)))
#cv2.waitKey(0)
#cv2.destroyAllWindows()
#cv2.waitKey(1)
#cv2.destroyAllWindows()
