import numpy as np
import cv2
from PIL import Image
import os

# Path for face image database
path = 'dataset'

# loads the "classifier"
cascadePath = 'Data/haarcascade_frontalface_default.xml'
detector = cv2.CascadeClassifier(cascadePath)



font = cv2.FONT_HERSHEY_SIMPLEX


class RecognitionUser():
    def __init__(self):
        pass

    def getDataSet(self, face_id):
        imagepath = ''

        # For each person, enter one numeric face id
        print('Initializing face captures. Look the camera and wait ...')
        
        # Initialize individual sampling face count
        count = 0

        cap = cv2.VideoCapture(0)
        # cap.set(3,640) # set Width
        # cap.set(4,480) # set Height
        
        while(True):
            ret, img = cap.read()
            img = cv2.flip(img, 1) # Flip camera vertically
            
            if(count == 15):
                imagepath = 'picture/image_user/User.' + face_id  + '.jpg'
                print('[INFO] The image user register', imagepath)
                cv2.imwrite(imagepath, img)

            # draw a frame in the middle of the screen so that the user 
            # can bring his face into this area
            centerH = img.shape[0] // 2 
            centerW = img.shape[1] // 2
            sizeboxW = 300
            sizeboxH = 400
            cv2.rectangle(img, (centerW - sizeboxW // 2, centerH - sizeboxH // 2),
                        (centerW + sizeboxW // 2, centerH + sizeboxH // 2), (255, 255, 255), 5)

            # convert image to gray
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # classifier function
            faceCascade = cv2.CascadeClassifier('Data/haarcascade_frontalface_default.xml')
            faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 5)

            for(x, y, w, h) in faces:
                cv2.rectangle(img, (x,y), (x+w, w+h), (255, 0, 0), 2)
                count += 1
                cv2.imwrite('dataset/User.' + face_id + '.' + str(count) + '.jpg', gray[y:y+h, x:x+w])

            cv2.imshow('video', img)
            
            k = cv2.waitKey(100) & 0xff
            if k == 27: # press 'ESC' to quit
                break
            elif count >= 30: # take 30 face sample and stop video
                break
        # Do a bit cleanup
        print('[INFO] Exiting Program and cleanup stuff')

        cap.release()
        cv2.destroyAllWindows()
        return imagepath

    def trainingUser(self):
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        print('[INFO] Traning faces. It will take a few seconds. Wait ...')
        faces, ids = self.getImagesAndLabels(path)
        recognizer.train(faces, np.array(ids))

        # Save the model into trainer/trainer.yml
        recognizer.write('trainer/trainer.yml') 

        # print the number of faces trained and end program
        print('[INFO] {0} faces trained. Exiting Program'.format(len(np.unique(ids))))


    def getImagesAndLabels(self, path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img, 'uint8')
            id = int(os.path.split(imagePath)[-1].split('.')[1])
            print('ID: ', id)
            faces = detector.detectMultiScale(img_numpy)
            for(x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y+h, x:x+w])
                ids.append(id)
        return faceSamples, ids 

    def recognitionUser(self):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('trainer/trainer.yml')
        # initiate id counter
        id = 0

        # names related to ids: example ==> Marcelo: id = 1, ...

        names = ['None', 'QuocBrave', 'Marcelo']

        # Initialize and start realine video capture
        cam = cv2.VideoCapture(0)
        cam.set(3, 640) # set video widht
        cam.set(4, 480) # set video height

        # Define min window size to be recognized as a face
        minW = 0.1*cam.get(3)
        minH = 0.1*cam.get(4)

        while True:
            # read image from camera
            ret, img = cam.read()
            img =  cv2.flip(img, 1)

            centerH = img.shape[0] // 2
            centerW = img.shape[1] // 2
            sizeboxW = 300
            sizeboxH = 400
            cv2.rectangle(img, (centerW - sizeboxW // 2, centerH - sizeboxH // 2),
                        (centerW + sizeboxW // 2, centerH + sizeboxH // 2), (255, 255, 255), 5)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faceCascade = cv2.CascadeClassifier('Data/haarcascade_frontalface_default.xml')
            faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 5,  minSize = (int(minW), int(minH)))

            for(x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                print(str(id))

                # Check if confidence is less them 100 ==> '0' is perfect match
                if(confidence < 100):
                    #TODO: loading data from database and compare the user
                    # id = names[id]
                    confidence = '{0}%'.format(round(100 - confidence))
                    cv2.putText(img, str(id), (x, y+h+30), font, 1, (0, 255, 0), 2)
                else:
                    id = 'Name: Unknown'
                    confidence = '{0}%'.format(round(100 - confidence))
                    cv2.putText(img, str(id), (x, y+h+30), font, 1, (255, 0, 0), 2)

                print(confidence)

            cv2.imshow('camera', img)

            k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
            if k == 27:
                break

        # Do a bit of cleanup
        print("[INFO] Exiting Program and cleanup stuff")
        cam.release()
        cv2.destroyAllWindows()


        
        

            

