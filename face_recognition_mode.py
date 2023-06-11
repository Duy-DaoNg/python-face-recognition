from cvzone.FaceMeshModule import FaceMeshDetector
import face_recognition
import os
# from cvzone.PlotModule import LivePlot
import sys
import cv2
import time
from Adafruit_IO import MQTTClient
# AIO_FEED_ID = "door"
# AIO_USERNAME = "DuyNg"
# AIO_KEY = "aio_xfil24r04CwMri8I3mmHutlGUUlM"
AIO_FEED_ID = "bbc_door"
AIO_USERNAME = "leductai"
# AIO_KEY = "aio_jHnD49N9P3CVWfQKZwgie5SFZ3ty"
AIO_KEY = "aio_ndSZ84ujGOqbjpzrK1HPKFoZz9lY"
class DoorController():
    client = MQTTClient(AIO_USERNAME, AIO_KEY)
    def __init__(self):
        self.client.on_connect = self.connected
        self.client.on_disconnect = self.disconnected
        # self.client.on_message = self.message
        self.client.on_subscribe = self.subscribe
        self.client.connect()
        # self.client.loop_background()

    def connected(self,client):
        print("Ket noi thanh cong...")
        client.subscribe(AIO_FEED_ID)
    def subscribe(self,client, userdata, mid, granted_qos):
        print("Subcribe thanh cong")
    def disconnected(self,client):
        print("Ngat ket noi...")
        sys.exit(1)
    def message(self,client, feed_id, payload):
        print("Nhan du lieu: "+ payload)

class HumanEye:
    # Attributes for counting Eyes blink
    ratioList = []
    blinkCounter = 0
    counterFrame = 0
    ratioAverage = 0
    # Attributes for collecting eyes landmarks
    detector = FaceMeshDetector(maxFaces=1)
    # plotY = LivePlot(640,360, [20,50], invert=True)
    # framePlot = []
    frameAfterDetect = []
    # face was detected
    isFace = 0


    
    def __init__(self):
        pass
    # Check the ratio to decide eyes blink or not
    # skip 10 frame after received signal
    # if eyes were blinked 2 time then return True to 
    # move next phrase
    def handleRatioResult(self):
        if self.ratioAverage < 33 and self.counterFrame == 0:
            self.counterFrame = 1
        if self.counterFrame != 0:
            self.counterFrame += 1
            if self.counterFrame > 10:
                self.counterFrame = 0
                if self.ratioAverage > 33:
                    self.blinkCounter += 1
                    # print("Blink detect")
        if self.blinkCounter >= 1:
            # self.resetAttributesValue()
            return True
        return False
    def blinkDetect(self, up, down, left, right, detector):
        # calculate distance 
        lengthVer,_ = detector.findDistance(up, down)
        lengthHor,_ = detector.findDistance(left, right)
        # calculate ratio
        ratio = int(lengthVer/lengthHor*100)
        self.ratioList.append(ratio)
        if len(self.ratioList) > 3:
            self.ratioList.pop(0)
        self.ratioAverage = int(sum(self.ratioList)/len(self.ratioList))
        # return value
        return self.handleRatioResult()
    
    # reset all attributes if can't detect face
    def resetAttributesValue(self):
        self.blinkCounter = 0
        self.counterFrame = 0
        self.ratioList = []
        # self.framePlot = []
        self.frameAfterDetect = []
        # self.isFace = 0

    def checkEyeBlink(self, checkingFrame, isLeftEye):

        self.frameAfterDetect, faces = self.detector.findFaceMesh(checkingFrame, draw=False)
        if faces:
            # self.isFace = 1
            face = faces[0]
            if isLeftEye:
                result = self.blinkDetect(face[159], face[23], face[130], face[243], self.detector)
            else:
                result = self.blinkDetect(face[386], face[253], face[463], face[359], self.detector)
            # self.framePlot = self.plotY.update(self.ratioAverage)
            # cvzone.putTextRect(self.frameAfterDetect, f'Blink count: {self.blinkCounter}', (50, 100))
        else:
            result = 0
            self.resetAttributesValue()
        return result

class DetectFaceProcess:
    phraseDetectFace = 1
    phraseOneValid = 0
    face_step_one_encoding = []
    face_step_two_encoding = []
    leftEye = HumanEye()
    rightEye = HumanEye()
    doorController = DoorController()
    detector = FaceMeshDetector(maxFaces=1)
    # time to calculate timeout 
    start_time = 0
    isPrint = 0
    def __init__(self):
        pass
    
    def unlockDoor(self):
        self.doorController.client.publish(AIO_FEED_ID, 1)
        
    def resetAllAttribute(self):
        self.phraseDetectFace = 1
        self.phraseOneValid = 0
        self.start_time = 0
        self.isPrint = 0
        self.leftEye.resetAttributesValue()    
        self.rightEye.resetAttributesValue()
    def faceDetectProcess(self, frame, websocket):
        frameCopy = frame
        frame = cv2.resize(frame, (0,0), None, 0.4, 0.4)
        face_bounding_boxes = face_recognition.face_locations(frame)
        if len(face_bounding_boxes) == 1:
            self.start_time = 0
            try:
            # if True:
                # Phrase 1: Detect and save image
                if self.phraseDetectFace == 1:
                    # print("In phrase 1")
                    self.phraseOneValid += 1
                    if self.phraseOneValid > 10:
                        self.phraseOneValid = 0
                        tmp = cv2.cvtColor(frameCopy, cv2.COLOR_RGB2BGR)
                        self.face_step_one_encoding = face_recognition.face_encodings(tmp,face_bounding_boxes)[0]
                        self.phraseDetectFace = 2
                # Pharse 2: Blink check
                elif self.phraseDetectFace == 2:
                    if self.isPrint == 0:
                        print("In pharse 2: Check Blink")
                        self.isPrint = 1
                    result = 0
                    result = self.leftEye.checkEyeBlink(frameCopy, True)
                    if result == False:
                        result = self.rightEye.checkEyeBlink(frameCopy, False)
                        # TODO: set time_out
                    if result:
                        # leftEye.resetAttributesValue()
                        self.phraseDetectFace = 3   
                        self.isPrint = 0
                # Pharse 3: compare there 2 face
                elif self.phraseDetectFace == 3:
                    if self.isPrint == 0:
                        print("In phrase 3: Comapre 2 face")
                        self.isPrint = 1
                    # cv2.imwrite('./Image_2.jpg', frame_copy)
                    # tmp = face_recognition.load_image_file('./Image_2.jpg')
                    tmp = cv2.cvtColor(frameCopy, cv2.COLOR_RGB2BGR)
                    self.face_step_two_encoding = face_recognition.face_encodings(tmp)[0]
                    result = face_recognition.compare_faces([self.face_step_one_encoding], self.face_step_two_encoding)
                    if result:
                        self.phraseDetectFace = 4
                        self.isPrint = 0
                    else: 
                        self.phraseDetectFace = 1
                        self.isPrint = 0
                        # TODO: raise Error
                        print("Face in phrase 1 and 2 didn't match")   
                # Pharse 4: Retrieve Folder Data and compare
                elif self.phraseDetectFace == 4:
                    # print("In pharse 4")
                    print("Your face was detected")
                    print("Waiting for serveral times to recognize")
                    result = False
                    statusBar = 0
                    slideBar = 0
                    percent = 0
                    person_unlock = ""
                    dataDirectory = os.listdir('./Data/')
                    for person in dataDirectory:
                        pix = os.listdir("./Data/" + person)
                        for person_img in pix:
                            face = face_recognition.load_image_file("./Data/" + person + "/" + person_img)
                            faceFromData = face_recognition.face_encodings(face)[0]
                            result = face_recognition.compare_faces([faceFromData], self.face_step_two_encoding)[0]
                            statusBar += 1
                            sys.stdout.write('\r')
                            # the exact output you're looking for:
                            slideBar = int(21/len(dataDirectory))*(statusBar+1)
                            if slideBar >= 21:
                                slideBar = 20
                            percent = int(21/len(dataDirectory))*5*(1+statusBar)
                            if percent >= 100:
                                percent = 99
                            sys.stdout.write("[%-20s] %d%%" % ('='*slideBar, percent))
                            sys.stdout.flush()
                            if result:
                                person_unlock = person
                                break
                        if result:
                            break
                    if result:
                        # TODO: call API Adafruit
                        # print('\n')
                        self.unlockDoor()
                        # Message successful
                        sys.stdout.write('\r')
                        sys.stdout.write("[%-20s] %d%%" % ('='*21, 100))
                        sys.stdout.write('\n')
                        # print('\n')
                        # print(person_unlock)

                        print("The Door was unclocked by "+ person_unlock)
                        time.sleep(5)
                        self.resetAllAttribute()    
                        return 2  
                    else:
                        print("Dont Matched")
                        self.resetAllAttribute()              
            except:
                print("Something wrong!!!")
                self.resetAllAttribute()

        elif len(face_bounding_boxes) >= 2:
            print("Too many faces in the Frame")
            self.resetAllAttribute()
        else:
            # TODO: no face in frame move to 
            # Normal state after 60s
                # time to calculate timeout 
            if (self.start_time == 0):
                self.start_time = time.time()  
            end_time = time.time()
            elapsedTime = end_time - self.start_time 
            if (elapsedTime >= 30):
                self.resetAllAttribute()
                return 1
        return False

