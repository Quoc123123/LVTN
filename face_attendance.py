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


SAMPLE_NUMBER = 30
BLUE = (255,0,0)
GREEN = (0,255,0)
RED = (0,0,255)
YELL = (0,255,255)



# Path for face image database
path = 'dataset'

# Filters path
haar_faces = cv2.CascadeClassifier('Data/haarcascade_frontalface_default.xml')
haar_eyes = cv2.CascadeClassifier('Data/haarcascade_eye.xml')
haar_mouth = cv2.CascadeClassifier('Data/Mouth.xml')
haar_nose = cv2.CascadeClassifier('Data/Nose.xml')


model = "Data/filters/shape_predictor_68_face_landmarks.dat"

# detector = cv2.CascadeClassifier('Data/haarcascade_frontalface_default.xml')
# font = cv2.FONT_HERSHEY_SIMPLEX

class RecognitionUser():
    def __init__(self):
        pass

    def apply_haar_filter(self, img, haar_cascade, scaleFact = 1.1, minNeigh = 5, minSizeW = 30):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        features = haar_cascade.detectMultiScale(
            gray,
            scaleFactor=scaleFact,
            minNeighbors=minNeigh,
            minSize=(minSizeW, minSizeW),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return features

    def getDataSet(self, face_id):
        imagepath = ''

        # For each person, enter one numeric face id
        print('Initializing face captures. Look the camera and wait ...')
        
        # Initialize individual sampling face count
        count = 0
        
        # Config webcam
        cap = cv2.VideoCapture(0)
        cv2.imshow('Video', np.empty((5,5),dtype=float))

        while(True):
            # Capture frame-by-frame
            ret, img = cap.read()
            img = cv2.flip(img, 1) # Flip camera vertically
            
            # Take a image for display purpose
            if(count == SAMPLE_NUMBER / 2):
                imagepath = 'picture/image_user/User.' + face_id  + '.jpg'
                print('[INFO] The image user register', imagepath)
                cv2.imwrite(imagepath, img)

            # draw a frame in the middle of the screen so that the user 
            # can bring his face into this area
            # centerH = img.shape[0] // 2 
            # centerW = img.shape[1] // 2
            # sizeboxW = 300
            # sizeboxH = 400
            # cv2.rectangle(img, (centerW - sizeboxW // 2, centerH - sizeboxH // 2),
            #             (centerW + sizeboxW // 2, centerH + sizeboxH // 2), (255, 255, 255), 5)

            # classifier function
            faces = self.apply_haar_filter(img, haar_faces, 1.3, 5, 30)

            for(x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, w+h), BLUE, 2)

                sub_img = img[y:y+h,x:x+w,:]
                eyes = self.apply_haar_filter(sub_img, haar_eyes, 1.3 , 10, 10)
                for (x2, y2, w2, h2) in eyes:
                    cv2.rectangle(img, (x+x2, y+y2), (x + x2+w2, y + y2+h2), YELL, 2)

                nose = self.apply_haar_filter(sub_img, haar_nose, 1.3 , 8, 10)
                for (x2, y2, w2, h2) in nose:
                    cv2.rectangle(img, (x+x2, y+y2), (x + x2+w2, y + y2+h2), RED, 2) #red
                
                # only analize half of face for mouth
                sub_img2 = img[y + h//2:y+h,x:x+w,:] 
                mouth = self.apply_haar_filter(sub_img2, haar_mouth, 1.3 , 10, 10)
                for (x2, y2, w2, h2) in mouth:
                    cv2.rectangle(img, (x+x2, y+h//2+y2), (x + x2+w2, y+h//2+y2+h2), GREEN, 2) #green


                count += 1
                cv2.imwrite('dataset/User.' + face_id + '.' + str(count) + '.jpg', cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[y:y+h, x:x+w])

            cv2.imshow('Video', img)
            
            k = cv2.waitKey(100) & 0xff
            if k == 27: # press 'ESC' to quit
                break
            elif count >= SAMPLE_NUMBER: # take 30 face sample and stop video
                break
        # Do a bit cleanup
        print('[INFO] Exiting Program and cleanup stuff')

        cap.release()
        cv2.destroyAllWindows()
        return imagepath


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

    # def trainingUser(self):
    #     print('[INFO] Traning faces. It will take a few seconds. Wait ...')
    #     # 
    #     recognizer = cv2.face.LBPHFaceRecognizer_create()
    #     faces, ids = self.getImagesAndLabels(path)
    #     recognizer.train(faces, np.array(ids))

    #     # Save the model into trainer/trainer.yml
    #     recognizer.write('trainer/trainer.yml') 

    #     # print the number of faces trained and end program
    #     print('[INFO] {0} faces trained. Exiting Program'.format(len(np.unique(ids))))


    # def getImagesAndLabels(self, path):
    #     imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    #     faceSamples = []
    #     ids = []
    #     for imagePath in imagePaths:
    #         PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
    #         img_numpy = np.array(PIL_img, 'uint8')
    #         id = int(os.path.split(imagePath)[-1].split('.')[1])
    #         print('ID: ', id)
    #         faces = detector.detectMultiScale(img_numpy)
    #         for(x, y, w, h) in faces:
    #             faceSamples.append(img_numpy[y:y+h, x:x+w])
    #             ids.append(id)
    #     return faceSamples, ids 

    # def recognitionUser(self, timeout):
    #     recognizer = cv2.face.LBPHFaceRecognizer_create()
    #     recognizer.read('trainer/trainer.yml')

    #     # initiate id counter
    #     id = 0
    #     confidence = 0


    #     # Initialize and start realine video capture
    #     cam = cv2.VideoCapture(0)
    #     cam.set(3, 640) # set video widht
    #     cam.set(4, 480) # set video height

    #     # Define min window size to be recognized as a face
    #     minW = 0.1*cam.get(3)
    #     minH = 0.1*cam.get(4)

    #     start_time = time.time()

    #     while True:
    #         # read image from camera
    #         ret, img = cam.read()
    #         img =  cv2.flip(img, 1)

    #         centerH = img.shape[0] // 2
    #         centerW = img.shape[1] // 2
    #         sizeboxW = 300
    #         sizeboxH = 400
    #         cv2.rectangle(img, (centerW - sizeboxW // 2, centerH - sizeboxH // 2),
    #                     (centerW + sizeboxW // 2, centerH + sizeboxH // 2), (255, 255, 255), 5)

    #         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #         faceCascade = cv2.CascadeClassifier(cascadePath)
    #         faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 5,  minSize = (int(minW), int(minH)))

    #         for(x, y, w, h) in faces:
    #             cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    #             id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
    #             print('Face recognition id: {} - Confidence: {}'.format(id, confidence))

    #             # Check if confidence is less them 100 ==> '0' is perfect match
    #             if(confidence < 100):
    #                 # confidence = '{0}%'.format(round(100 - confidence))
    #                 confidence = round(100 - confidence)
    #                 cv2.putText(img, str(id), (x, y+h+30), font, 1, (0, 255, 0), 2)
    #             else:
    #                 # confidence = '{0}%'.format(round(100 - confidence))
    #                 confidence = round(100 - confidence)
    #                 cv2.putText(img, 'Name: Unknown', (x, y+h+30), font, 1, (255, 0, 0), 2)
    #                 print('Name: Unknown')

    #         # Check the timeout
    #         if time.time() - start_time > timeout:
    #             print("[INFO] Exiting Program and cleanup stuff")
                
    #             # Do a bit of cleanup
    #             cam.release()
    #             cv2.destroyAllWindows()
    #             return str(id), str(confidence)
    #             break
            

    #         cv2.imshow('camera', img)
    #         cv2.waitKey(10)
            # print("[INFO] Exiting Program and cleanup stuff")
            # # Do a bit of cleanup
            # cam.release()
            # cv2.destroyAllWindows()
          
            # k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
            # if k == 27:
            #     break

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