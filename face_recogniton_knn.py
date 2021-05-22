import numpy as np
import cv2, math
from sklearn import neighbors
import pickle
from PIL import Image, ImageDraw
import os
import time
from imutils import face_utils,  rotate_bound
import datetime
import imutils
import dlib
import face_recognition_models 
import recognition.face_recognition as face_recognition
from recognition.face_recognition.face_recognition_cli import image_files_in_folder
from user_infor import *

# Using algorithm

# Path for face image database
INPUT_TRAINING_DIR      = 'recognition/dataset/train'
INPUT_TEST_DIR          = 'recognition/dataset/test'
OUTPUT_TRAINING_DIR     = 'recognition/output/trained_knn_model.clf'
# OUTPUT_TRAINING_DIR     = 'recognition/output/trainer.yml'


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class RecognitionUser():
    def __init__(self):
        self.userInfor = UserInfor()

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

    def facial_landmarks(self, ID):
        # initialize dlib's face detector (HOG-based + Linear SVM face) and then create
        # the facial landmark predictor
        print("[INFO] loading facial landmark predictor...")
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
        fa = FaceAligner(predictor)

        video_capture = cv2.VideoCapture(0)
        cv2.imshow('Video', np.empty((5,5),dtype=float))
        
        # total number of faces written to disk
        total = 0

        # loop over the frames from the video stream
        while cv2.getWindowProperty('Video', 0) >= 0:
            # grab the frame from the threaded video stream, resize it to
            # have a maximum width of 400 pixels, and convert it to
            # grayscale
            
            # Capture frame-by-frame
            ret, frame = video_capture.read()
            orig = frame.copy()
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

                # incl = self.calculate_inclination(shape[17], shape[26])
                # print("Pixels distance points in mouth: ", shape[66][1] - shape[62][1])

                # x, y, w, h = rect.left(), rect.top(), rect.width(), rect.height()
                (x, y, w, h) = face_utils.rect_to_bb(rect)
                
                # get image to write and align it
                # output_img = frame[y:y + h, x:x + w].copy()
                faceAligned = fa.align(frame, gray, rect)
                # cv2.imshow("Aligned", faceAligned)

	            
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

                # loop over the (x, y)-coordinates for the facial landmarks
                # and draw them on the image
                for (x, y) in shape:
                    cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
                cv2.imshow("Frame", frame)

            time.sleep(0.1)
            p = os.path.join(f'{INPUT_TRAINING_DIR}', ID)
            if not os.path.exists(p):
                os.makedirs(p)
            p = os.path.join(p, "{}.png".format(str(total).zfill(5)))
            
            if len(rects) > 0:
                total += 1
                cv2.imwrite(p, faceAligned)

            if total >= 10:
                break
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
    	        break
        print("[INFO] {} face images stored".format(total))
        print("[INFO] cleaning up...")
        video_capture.release()
        cv2.destroyAllWindows()

    #========================================================================================
    # Uisng KNN algorithm
    #========================================================================================

    def train(self, train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
        """
        Trains a k-nearest neighbors classifier for face recognition.

        :param train_dir: directory that contains a sub-directory for each known person, with its name.

        (View in source code to see train_dir example tree structure)

        Structure:
            <train_dir>/
            ├── <person1>/
            │   ├── <somename1>.jpeg
            │   ├── <somename2>.jpeg
            │   ├── ...
            ├── <person2>/
            │   ├── <somename1>.jpeg
            │   └── <somename2>.jpeg
            └── ...

        :param model_save_path: (optional) path to save model on disk
        :param n_neighbors: (optional) number of neighbors to weigh in classification. Chosen automatically if not specified
        :param knn_algo: (optional) underlying data structure to support knn.default is ball_tree
        :param verbose: verbosity of training
        :return: returns knn classifier that was trained on the given data.
        """

        X = []
        y = []

        # Loop through each person in the training set
        for class_dir in os.listdir(train_dir):
            if not os.path.isdir(os.path.join(train_dir, class_dir)):
                continue
            
            # Loop through each training image for the current person
            for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
                image = face_recognition.load_image_file(img_path)
                face_bounding_boxes = face_recognition.face_locations(image)

                if len(face_bounding_boxes) != 1:
                    # If there are no people (or too many people) in a training image, skip the image.
                    if verbose:
                        print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
                else:
                    # Add face encoding for current image to the training set
                    X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                    y.append(class_dir)

        # Determine how many neighbors to use for weighting in the KNN classifier
        if n_neighbors is None:
            n_neighbors = int(round(math.sqrt(len(X))))
            print("Chose n_neighbors automatically:", n_neighbors)

            
        # Create and train the KNN classifier
        knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
        knn_clf.fit(X, y)

        # Save the trained KNN classifier
        if model_save_path is not None:
            with open(model_save_path, 'wb') as f:
                pickle.dump(knn_clf, f)

        return knn_clf

    def predict(self, X_img_path, knn_clf=None, model_path=None, distance_threshold=0.4):
        """
        Recognizes faces in given image using a trained KNN classifier

        :param X_img_path: path to image to be recognized
        :param knn_clf: (optional) a knn classifier object. if not specified, model_save_path must be specified.
        :param model_path: (optional) path to a pickled knn classifier. if not specified, model_save_path must be knn_clf.
        :param distance_threshold: (optional) distance threshold for face classification. the larger it is, the more chance
            of mis-classifying an unknown person as a known one.
        :return: a list of names and face locations for the recognized faces in the image: [(name, bounding box), ...].
            For faces of unrecognized persons, the name 'unknown' will be returned.
        """

        if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
            raise Exception("Invalid image path: {}".format(X_img_path))

        if knn_clf is None and model_path is None:
            raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")


        # Load a trained KNN model (if one was passed in)
        if knn_clf is None:
            with open(model_path, 'rb') as f:
                knn_clf = pickle.load(f)

        # Load image file and find face locations
        X_img = face_recognition.load_image_file(X_img_path)
        X_face_locations = face_recognition.face_locations(X_img)

        # If no faces are found in the image, return an empty result.
        if len(X_face_locations) == 0:
            return []

        # Find encodings for faces in the test iamge
        faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)

        # Use the KNN model to find the best matches for the test face
        closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)

        are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

        # Predict classes and remove classifications that aren't within the threshold
        return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

    def show_prediction_labels_on_image(self, img_path, predictions):
        """
        Shows the face recognition results visually.

        :param img_path: path to image to be recognized
        :param predictions: results of the predict function
        :return:
        """
        pil_image = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(pil_image)

        for name, (top, right, bottom, left) in predictions:
            # Draw a box around the face using the Pillow module
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

            # There's a bug in Pillow where it blows up with non-UTF-8 text
            # when using the default bitmap font
            name = name.encode("UTF-8")

            # Draw a label with a name below the face
            text_width, text_height = draw.textsize(name)
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

        # Remove the drawing library from memory as per the Pillow docs
        del draw

        # Display the resulting image
        pil_image.show()
        

    def trainingUser(self):
        # STEP 1: Train the KNN classifier and save it to disk
        # Once the model is trained and saved, you can skip this step next time.
        print("Training KNN classifier...")
        classifier = self.train(f'{INPUT_TRAINING_DIR}', model_save_path=OUTPUT_TRAINING_DIR, n_neighbors=2)
        print("Training complete!")

    def recognitionUser(self, timeout):
        # Initialize and start realine video capture
        video_capture = cv2.VideoCapture(0)
        cv2.imshow('Video', np.empty((5,5),dtype=float))
        
        # loop over the frames from the video stream
        # while cv2.getWindowProperty('Video', 0) >= 0:
        check_number_unknow = 0
        flag_check_unknow = True
        check_number_user = 0
        flag_check_user = True
        
        start_time = time.time()

        while cv2.getWindowProperty('Video', 0) >= 0:
            if time.time() - start_time > timeout:
                return list((False, 3, None))

            # Capture frame-by-frame
            ret, frame = video_capture.read()
            orig = frame.copy()
            
            # writing image
            p = os.path.join(INPUT_TEST_DIR, "{}.png".format('user1'))
            cv2.imwrite(p, orig)

            # using the trained classifier, make predictions for unknown images
            for image_file in os.listdir(INPUT_TEST_DIR):
                full_file_path = os.path.join(INPUT_TEST_DIR, image_file)

                # print("Looking for faces in {}".format(image_file))

                # Find all people in the image using a trained classifier model
                # Note: You can pass in either a classifier file name or a classifier model instance
                predictions = self.predict(full_file_path, model_path=OUTPUT_TRAINING_DIR)
                # if len(predictions) == 0:
                #     print('No faces are found in the image')
                #     video_capture.release()
                #     cv2.destroyAllWindows()
                #     return list((None, 0, None))
                # print('predictions', predictions)

                # TODO: Validate return value
                # check how many faces were recognized at this time     
                if len(predictions) > 1:
                    print('Number of faces were recognized: ', len(predictions))
                    video_capture.release()
                    cv2.destroyAllWindows()
                    return list((False, 2, None))

                # Display results overlaid on an image
                pil_image = Image.open(full_file_path).convert("RGB")
                draw = ImageDraw.Draw(pil_image)
                for name, (top, right, bottom, left) in predictions:
                    # print("- Found {} at ({}, {})".format(name, left, top))
                    if flag_check_unknow:
                        if name == 'unknow':
                            check_number_unknow += 1
                            flag_check_unknow = True
                        else:
                            flag_check_unknow == False
                        
                    if flag_check_unknow and check_number_unknow >= 3:
                        print('Unknow user')
                        video_capture.release()
                        cv2.destroyAllWindows()
                        return list((False, 1, 'unknow'))

                    # Draw a box around the face using the Pillow module
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 1)

                    # Draw a label with a name below the face
                    text_width, text_height = draw.textsize(name)
                
                    cv2.rectangle(frame, (left, bottom - text_height - 10), (right, bottom), (255, 0, 0), -1)
        
                    cv2.putText(frame, str(name), (left + 6, bottom - text_height - 12), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    # Show infor user
                    cv2.imshow('Video', frame)
                    
                    check_number_user += 1
                    print('recognized user: {} - {}'.format(str(name), check_number_user))
                    if check_number_user >= 3:
                        video_capture.release()
                        cv2.destroyAllWindows()
                        return list((True, 1, str(name)))

            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
    	        break

        video_capture.release()
        cv2.destroyAllWindows()


    # #========================================================================================
    # # Uisng haarcascade algorithm
    # #========================================================================================
    # def train(self, train_dir, model_save_path):
    #     recognizer = cv2.face.LBPHFaceRecognizer_create()
    #     detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    #     imagePaths = [os.path.join(train_dir,f) for f in os.listdir(train_dir)] 
    #     faceSamples=[]
    #     ids = []
        
    #     for imagePath in imagePaths:
    #         PIL_img = Image.open(imagePath).convert('L')
    #         img_numpy = np.array(PIL_img,'uint8')
    #         id = int(os.path.split(imagePath)[-1].split(".")[1])
    #         print(id)
    #         faces = detector.detectMultiScale(img_numpy)
    #         for (x,y,w,h) in faces:
    #             faceSamples.append(img_numpy[y:y+h,x:x+w])
    #             ids.append(id)

    #     recognizer.train(faceSamples, np.array(ids))
    #     recognizer.save(model_save_path)


    # def trainingUser(self):
    #     # STEP 1: Train the KNN classifier and save it to disk
    #     # Once the model is trained and saved, you can skip this step next time.
    #     print("Training haarCascade classifier...")
    #     classifier = self.train(f'{INPUT_TRAINING_DIR}', model_save_path=OUTPUT_TRAINING_DIR)
    #     print("Training complete!")

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
