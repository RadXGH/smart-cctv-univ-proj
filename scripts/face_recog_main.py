import email
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import os
from datetime import datetime
import string
import tkinter as tk

# import from email_notify.py
from email_notify import send_email

### CONTOH RUN SCRIPT:
### python face_recog_main.py --cascade haarcascade_frontalface_default.xml --encodings model.pickle

# go back one folder to get to root folder
os.chdir('..')


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
# determine where is the haar cascade file located
ap.add_argument("-c", "--cascade", required=True, help = "path to where the face cascade resides")

# determine which encodings file to use (the created pickle file from encode_faces.py)
ap.add_argument("-e", "--encodings", required=True, help="path to serialized db of facial encodings")
args = vars(ap.parse_args())



# load the known faces and embeddings along with OpenCV's Haar cascade for face detection (usually uses haarcascade_frontalface_default.xml)
print("[INFO] Loading encodings + face detector...")

# checks if model.pickle exist
if os.path.isfile('model.pickle') is not True:
    master = tk.Tk()
    note = tk.Label(master, text="Please run 'Add Face' first.")
    note.grid(row=0, column=0)
    tk.mainloop()
    exit()
else:
    data = pickle.loads(open(args["encodings"], "rb").read())
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + args["cascade"])

# initialize video stream
print("[INFO] Starting video stream...")
cam = VideoStream(src=0).start()

## FOR RASPBERRY PI CAMERA
# cam = VideoStream(usePiCamera=True).start()

# wait for camera turns on or warms up
time.sleep(3)

###### FPS INFO DEBUGGING ######
# start the FPS counter
fps = FPS().start()

temp = '' # used for storing detected names (line 134)
# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream and resize it to 500px (to speedup processing)
    frame = cam.read()
    frame = imutils.resize(frame, width=500)
	
	# convert the input frame from (1) BGR to grayscale (for face detection) and (2) from BGR to RGB (for face recognition)
    # gray is used for face detection from the realtime video stream
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # rgb is used for face recognition from the realtime video stream with the encoded model (pickle file)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	# detect faces from the grayscale frame
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
    
	# OpenCV returns -> (x, y, w, h) order, change into (top, right, bottom, left) order
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(rgb, boxes)
    # name that will be displayed as the result
    names = []

    # loop over the detected face encodings (realtime video stream)
    for encoding in encodings:
		# attempt to match each face in the input image to our known encodings (created pickle file)
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

		# check to see if we have found a match
        if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
            name = max(counts, key=counts.get)
		
		# update the list of names
        names.append(name)

    time_required = 0

    # loop over the detected faces (from realtime video stream)
    for ((top, right, bottom, left), name) in zip(boxes, names):
        timeNow = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # if the detected face is recognized
        if name != 'Unknown':
            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

            time.sleep(5)
            if name != temp:
                temp = name
                name = string.capwords(name, sep = None)
                name = name + ' at ' + timeNow + '\n'
                with open('scripts/files/detected_names.txt', 'a') as nameFile:
                    nameFile.write(name)

            print('[INFO] found')

        # if the detected face isn't recognized
        else:
            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

            time.sleep(5)
            if name != temp:
                temp = name
                name = name + ' at ' + timeNow + '\n'
                with open('scripts/files/detected_names.txt', 'a') as nameFile:
                    nameFile.write(name)

            print('[INFO] unknown face')


    cv2.putText(frame, 'Press Esc to quit', (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
	# display the box which holds the result of face recognition
    cv2.imshow("Camera", frame)

    # press Esc to exit program
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

    ##### FPS INFO DEBUGGING ######
    # update the FPS counter
    fps.update()



###### FPS INFO DEBUGGING ######
fps.stop()
print("[INFO] Elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] Approx. FPS: {:.2f}".format(fps.fps()))


# close all program windows (from opencv gui) and stop camera video stream (from opencv video stream)
cv2.destroyAllWindows()



# NOTES:
# fps sangat rendah: 1-3 fps ketika terdetect ada muka di depan kamera, fps kembali normal ketika tidak terdetect ada muka di depan kamera.
# hal ini dikarenakan program memiliki proses lebih berat ketika harus membandingkan muka yang terdetect dengan model pickle yang disimpan sebelumnya.