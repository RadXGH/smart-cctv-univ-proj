from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os

### CONTOH RUN SCRIPT:
### python .\encode_faces.py --dataset dataset --encodings model.pickle --detection-method cnn

# go back one folder to root folder to get to dataset folder and make pickle file
os.chdir('..')


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()

# determine where folder the dataset is located
ap.add_argument("-i", "--dataset", required=True, help="path to input directory of faces + images")

# input the name of the pickle encodings file
ap.add_argument("-e", "--encodings", required=True, help="path to serialized db of facial encodings")

# use hog or cnn detection method, cnn is more accurate but uses more memory and resources
# cnn isn't recommended for pi usage
# use hog for pi usage
# OPTIONAL, defaults to use cnn
ap.add_argument("-d", "--detection-method", type=str, default="cnn", help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())



# grab the paths to the input images in our dataset
print("[INFO] Quantifying faces...")
imagePaths = list(paths.list_images(args["dataset"]))

# initialize the list of known encodings and known names
knownEncodings = []
knownNames = []

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
	# extract the person name from the image path
	print("[INFO] Processing image {}/{}".format(i + 1, len(imagePaths)))
	name = imagePath.split(os.path.sep)[-2]

	# load the input image and convert it from BGR (OpenCV ordering) to dlib ordering (RGB)
	image = cv2.imread(imagePath)
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	# detect the (x, y)coordinates of the bounding boxes corresponding to each face in the input image
	boxes = face_recognition.face_locations(rgb, model=args["detection_method"])

	# compute the facial embedding for the face
	encodings = face_recognition.face_encodings(rgb, boxes)
	# loop over the encodings
	for encoding in encodings:
		# add each encoding + name to our set of known names and
		# encodings
		knownEncodings.append(encoding)
		knownNames.append(name)



# dump the facial encodings + names to disk
print("[INFO] Finishing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
f = open(args["encodings"], "wb")
f.write(pickle.dumps(data))
f.close()