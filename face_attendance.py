import numpy as np
import cv2, math
from PIL import Image
import os
import time
from imutils import face_utils
import datetime
import imutils
import dlib
from imutils import face_utils, rotate_bound


# Path for face image database
path = 'dataset'

model = "Data/filters/shape_predictor_68_face_landmarks.dat"

# detector = cv2.CascadeClassifier('Data/haarcascade_frontalface_default.xml')
# font = cv2.FONT_HERSHEY_SIMPLEX

class RecognitionUser():
    def __init__(self):
        pass

    # points are tuples in the form (x,y)
    # returns angle between points in degrees
    def calculate_inclination(self, point1, point2):
        x1,x2,y1,y2 = point1[0], point2[0], point1[1], point2[1]
        incl = -180/math.pi*math.atan((float(y2-y1))/(x2-x1))
        return incl

    def calculate_boundbox(self, list_coordinates):
        x = min(list_coordinates[:,0])
        y = min(list_coordinates[:,1])
        w = max(list_coordinates[:,0]) - x
        h = max(list_coordinates[:,1]) - y
        return (x,y,w,h)

    # 68-point landmark detectors: identifies 68 points ((x, y) coordinates) in a human face. 
    # these points localize the region around the eyes, eyebrows, nose, mouth, chin and jaw.
    def get_face_boundbox(self, points, face_part):
        if face_part == 1:
            (x,y,w,h) = self.calculate_boundbox(points[17:22]) #left eyebrow
        elif face_part == 2:
            (x,y,w,h) = self.calculate_boundbox(points[22:27]) #right eyebrow
        elif face_part == 3:
            (x,y,w,h) = self.calculate_boundbox(points[36:42]) #left eye
        elif face_part == 4:
            (x,y,w,h) = self.calculate_boundbox(points[42:48]) #right eye
        elif face_part == 5:
            (x,y,w,h) = self.calculate_boundbox(points[29:36]) #nose
        elif face_part == 6:
            (x,y,w,h) = self.calculate_boundbox(points[48:68]) #mouth
        return (x,y,w,h)

    def facial_landmarks(self):
        # initialize dlib's face detector (HOG-based + Linear SVM face) and then create
        # the facial landmark predictor
        print("[INFO] loading facial landmark predictor...")
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(model)
        fa = FaceAligner(predictor, desiredFaceWidth=256)

        video_capture = cv2.VideoCapture(0)
        cv2.imshow('Video', np.empty((5,5),dtype=float))


        # loop over the frames from the video stream
        while cv2.getWindowProperty('Video', 0) >= 0:
            # grab the frame from the threaded video stream, resize it to
            # have a maximum width of 400 pixels, and convert it to
            # grayscale
            
            # Capture frame-by-frame
            ret, frame = video_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # detect faces in the grayscale frame
            rects = detector(gray, 0)

            # check to see if a face was detected, and if so, draw the total
            if len(rects) > 0:
                print('{} face(s) found'.format(len(rects)))


            # loop over the face detections
            for rect in rects:
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a NumPy array
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)

                # for i in range(1,7):
                #     (x,y,w,h) = self.get_face_boundbox(shape, i)
                #     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)

                incl = self.calculate_inclination(shape[17], shape[26])
                print("Pixels distance points in mouth: ", shape[66][1] - shape[62][1])

                # x, y, w, h = rect.left(), rect.top(), rect.width(), rect.height()
                (x, y, w, h) = face_utils.rect_to_bb(rect)

                faceOrig = imutils.resize(frame[y:y + h, x:x + w], width=256)
                faceAligned = fa.align(frame, gray, rect)

                # # display the output images
                cv2.imshow("Original", frame[y:y + h, x:x + w])
                cv2.imshow("Aligned", faceAligned)

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)


                # loop over the (x, y)-coordinates for the facial landmarks
                # and draw them on the image
                for (x, y) in shape:
                    cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
                    

            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
    	        break
        video_capture.release()
        cv2.destroyAllWindows()

class FaceAligner():
    def __init__(self, predictor, desiredLeftEye=(0.35, 0.35), desiredFaceWidth=256, desiredFaceHeight=None):
        # Store the facial landmark predictor, desired output left
        # eye position, and desired output face width + height
        # The facial predictor model
        self.predictor = predictor 
        self.desiredLeftEye = desiredLeftEye
        # face with in pixels
        self.desiredFaceWidth = desiredFaceWidth
        # face height value in pixels.
        self.desiredFaceHeight = desiredFaceHeight

        # if the desired face height is None, set it to be the
        # desired face width (normal behavior)
        if self.desiredFaceHeight is None:
            self.desiredFaceHeight = self.desiredFaceWidth
    
    def align(self, image, gray, rect):
        # convert the landmark (x, y)-coordinates to a NumPy array
        shape = self.predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # extract the left and right eye (x, y)-coordinates
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        leftEyePts = shape[lStart:lEnd]
        rightEyePts = shape[rStart:rEnd]

        # compute the center of mass for each eye
        leftEyeCenter = leftEyePts.mean(axis=0).astype("int")
        rightEyeCenter = rightEyePts.mean(axis=0).astype("int")

        # compute the angle between the eye centroids
        dY = rightEyeCenter[1] - leftEyeCenter[1]
        dX = rightEyeCenter[0] - leftEyeCenter[0]
        angle = np.degrees(np.arctan2(dY, dX)) - 180
        
        # compute the desired right eye x-coordinate based on the
        # desired x-coordinate of the left eye
        desiredRightEyeX = 1.0 - self.desiredLeftEye[0]

        # determine the scale of the new resulting image by taking
        # the ratio of the distance between eyes in the *current*
        # image to the ratio of distance between eyes in the
        # *desired* image
        dist = np.sqrt((dX ** 2) + (dY ** 2))
        desiredDist = (desiredRightEyeX - self.desiredLeftEye[0])
        desiredDist *= self.desiredFaceWidth
        scale = desiredDist / dist

        # compute center (x, y)-coordinates (i.e., the median point)
        # between the two eyes in the input image
        eyesCenter = ((leftEyeCenter[0] + rightEyeCenter[0]) // 2,
            (leftEyeCenter[1] + rightEyeCenter[1]) // 2)
        
        # grab the rotation matrix for rotating and scaling the face
        M = cv2.getRotationMatrix2D(eyesCenter, angle, scale)

        # update the translation component of the matrix
        tX = self.desiredFaceWidth * 0.5
        tY = self.desiredFaceHeight * self.desiredLeftEye[1]
        M[0, 2] += (tX - eyesCenter[0])
        M[1, 2] += (tY - eyesCenter[1])

        # apply the affine transformation
        (w, h) = (self.desiredFaceWidth, self.desiredFaceHeight)
        output = cv2.warpAffine(image, M, (w, h),
            flags=cv2.INTER_CUBIC)

        # return the aligned face
        return output