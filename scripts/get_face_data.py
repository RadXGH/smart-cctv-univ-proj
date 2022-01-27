from distutils import command
import cv2
import os
import time
from os import listdir
import tkinter as tk

# go back one folder to get to root folder to get to dataset folder
os.chdir('..')
# make the dataset folder
if os.path.isdir('dataset') is not True:
    os.mkdir('dataset')

def get_face_snapshot():
    global person_name
    faceCascade = cv2.CascadeClassifier('./venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml')

    # get video capture device
    cam = cv2.VideoCapture(0)
    cam.set(3, 800)
    cam.set(4, 450)

    font = cv2.FONT_HERSHEY_COMPLEX

    # gui
    while True:
        # instruction in cli window
        # print("[INFO] Input p to start taking photos.")
        # print("[INFO] Input anything other than p to quit.")
        # print("[INFO] Stay still in front of the camera for 5 seconds after inputting p.")
        # print("\n")
        # print("[INFO] Waiting for input....")

        # input p into cli to take a photo
        # userInput = input("[INPUT] ")
        # if userInput != 'p':
        #     exit()
        

        # make new folder for new data
        directory = os.path.join('dataset', person_name)
        os.mkdir(directory)
        # change working directory into the new folder
        os.chdir(directory)


        # warm up cam (if not, color can be incorrect)
        time.sleep(3) # waits for 3 seconds
        # get video input
        ret, img = cam.read()
        # convert video input color into gray for easier face detection
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


        # show camera window
        # cv2.imshow('Camera', img)
        # press esc to quit window
        # if cv2.waitKey(1) == 27:
        #     break

        # add text on video window
        # cv2.putText(img, 'Input p to take photos', (10, 30), font, 0.5, (255, 255, 255), 1)
        # cv2.putText(img, 'Input anything other than p to quit', (10, 50), font, 0.5, (255, 255, 255), 1)


        # face detection
        box_coords = faceCascade.detectMultiScale(gray_img, 1.1, 4)
        # box on detected face
        for box in box_coords:
            x, y, width, height = box
            x2, y2 = x + width, y + height
            # draw box
            # cv2.rectangle(img, (x, y), (x2, y2), (255, 0, 0), 2)
            # get the face inside the rectangle
            box_coords = img[y:y2, x:x2]
        
        # save the current video frame into the current working directory (take a photo)
        box_coords = cv2.resize(box_coords, (224, 224))

        # takes 10 photos
        count = 0
        while count < 10:
            cv2.imwrite('image' + str(count) + '.jpg', box_coords)
            count += 1


        # go back up twice in the directory (back to the root dir)
        os.chdir('..')
        os.chdir('..')
        break;

    master.destroy()

    # encode the whole dataset of faces into a new pickle file
    os.chdir('scripts/')
    os.system('python encode_faces.py --dataset dataset --encodings model.pickle --detection-method hog')
    os.chdir('..')

    # close video and window
    cam.release()
    cv2.destroyAllWindows()

def addNewName():
    global person_name
    sameFlag = False
    # get inputted name
    person_name = entry_str.get()
    person_name = person_name.lower()
    entry_str.set('')

    # checks if name is present
    if (person_name != ''):
        # checks if name is already present in dataset
        saved_names = listdir('dataset/')
        for names in saved_names:
            if (person_name == names):
                sameFlag = True
                noteName.configure(text = 'Name has been already added.')
                break
        # open and use the camera to get a video feed for taking a photo and make a new model
        if (sameFlag == False):
            get_face_snapshot()

# variable declarations
person_name = ''
# create GUI with tkinter
master = tk.Tk()
entry_str = tk.StringVar()

master.title('New name')
tk.Label(master, text = 'Full Name: ').grid(row=0, column=0)
person_name_Panel = tk.Entry(master, textvariable=entry_str, width=30).grid(row=0, column=1, padx=5, pady=5)

noteName = tk.Label(master, text = 'Enter a name.')
noteName.grid(row=1, column=0, padx=5, columnspan=2)

noteStayStill = tk.Label(master, text = 'Look towards the camera until this window disappear after saving.').grid(row=2, column=0, columnspan=2)

tk.Button(master, text = 'Save', width=10, command=addNewName).grid(row=3, column=1, padx=5, pady=5)
tk.Button(master, text = 'Cancel', width=10, command=master.destroy).grid(row=3, column=0, padx=5, pady=5)

tk.mainloop()
