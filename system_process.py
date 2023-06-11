import asyncio
import websockets
import cv2
import numpy as np
import base64
from download_data import DataLoading
from face_recognition_mode import DetectFaceProcess
import time

connected = False  # Flag to track the connection status

class WorkingProcess():
    INITIAL = 0
    IDLE = 1
    FACERECOG = 2
    state = INITIAL
    connected = False
    dataLoadingProcess = DataLoading()
    faceRecognition = DetectFaceProcess()

    def __init__(self):
        pass

    async def handle_message(self, websocket, path):
        client_IP = websocket.remote_address[0]
        if self.connected:
            print('New Connection was Rejected: ', client_IP)
            await websocket.close()  # Close the connection if another client is already connected
            return
        self.connected = True
        print('Establishing New Connection: ', client_IP)
        try:
            while True:
                # Initial state
                if (self.state == self.INITIAL):
                    await websocket.send("In Initial state")
                    await websocket.send("Updating")
                    # Update Data
                    while (self.dataLoadingProcess.loadData()==0):
                        print("Failed to load data in INITIAL. Attempt after 5s")
                        #TODO send response message
                        await websocket.send("Server Failed to load data in INITIAL. Attempt after 5s")
                        time.sleep(5)
                    print("Successfully Loaded")
                    await websocket.send("Successfully Loaded data")
                    time.sleep(3)
                    await websocket.send("Updated")
                    # # Move to IDLE state
                    self.state = self.IDLE
                # Continuously listen for incoming messages from the client
                try:
                    message = await websocket.recv()
                except websockets.exceptions.ConnectionClosed:
                    print("Client disconnected")
                    # need to reset all state
                    self.state = self.INITIAL
                    self.faceRecognition.resetAllAttribute()
                    break
                # IDLE state
                if (self.state == self.IDLE):
                    await websocket.send("IDLE")
                    # Read button input
                    # if recognition button is pressed
                    # --> move to Face recognition
                    if message == 'start':
                        self.state = self.FACERECOG
                    # if update button is pressed
                    # --> update data
                    elif message == 'update':
                        await websocket.send("Updating")
                        while(self.dataLoadingProcess.loadData() == 0):
                            print("Failed to load data in IDLE state. Attempt after 5s")
                            await websocket.send("Server Failed to load data in IDLE. Attempt after 5s")
                            time.sleep(5)
                        print("Successfully Updated")
                        await websocket.send("Successfully Updated")
                        time.sleep(3)
                        await websocket.send("Updated")
                elif (self.state == self.FACERECOG):
                    await websocket.send('Face')
                    await websocket.send("In Face-recognition state, wait until timeout")
                    stopSignal = 0
                    if len(message.split(',')) > 1:
                        img_data = base64.b64decode(message.split(',')[1])
                        
                        # Convert the image data to a NumPy array
                        nparr = np.frombuffer(img_data, np.uint8)
                        
                        # Decode the image array using OpenCV
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        stopSignal = self.faceRecognition.faceDetectProcess(frame, websocket)
                        if (message == 'stop') | stopSignal:
                            self.state = self.IDLE
                            self.faceRecognition.resetAllAttribute()  
                            await websocket.send('Faced')
                            if (stopSignal == 2):
                                await websocket.send('Door Unlocked') 
                            else:
                                await websocket.send('Time out')
                    elif (message == 'stop'):
                        self.state = self.IDLE
                        self.faceRecognition.resetAllAttribute() 
                        print('Receievd Stop signal from Camera') 
                        await websocket.send('Faced')
        finally:
            self.connected = False
    def runningProcess(self):
        start_server = websockets.serve(self.handle_message, '0.0.0.0', 8080)
        print('Server Start Listening')
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
