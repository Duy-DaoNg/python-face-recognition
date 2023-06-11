import pyrebase
import requests
import os
import glob
HOME_ID = "home64045eb4194b34d6aa91440e"
class DataLoading():
    def __init__(self):
        pass
    def clearData(self):
        folders = glob.glob('./Data/*')
        for folder in folders:
            files = glob.glob(folder+'/*')
            for file in files:
                os.remove(file)
            os.rmdir(folder)
    def findHomeID(self,str):
        beginIndex = str.find('/')
        midIndex = str.find('/',beginIndex+1)
        endIndex = str.find('/',midIndex+1)
        return [str[beginIndex+1:midIndex], str[midIndex+1:endIndex], str[endIndex+1:]]
    def findExtention(self,str):
        return str[str.rfind('.'):]
    def validURL(self, str):
        if len(str[str.rfind('/'):]) != 1:
            return 1
        else:
            return 0

    def downloadImage(self,image_url, name):
        img_data = requests.get(image_url).content
        with open(name, 'wb') as handler:
            handler.write(img_data)
    def loadData(self):
        # try:
        self.clearData()
        # config = {
        #     "apiKey": "AIzaSyCeKTx6-D62w2Sbf7MSRBR20Ksox4Z8n_c",
        #     "authDomain": "smarthome-eda8b.firebaseapp.com",
        #     "databaseURL": "https://smarthome-eda8b-default-rtdb.asia-southeast1.firebasedatabase.app",
        #     "storageBucket": "smarthome-eda8b.appspot.com",
        #     "serviceAccount": "serviceAccountKey.json"
        # }
        config = {
            "apiKey": "AIzaSyB1J39JCwdrJ4JUp23tFKr70P81AvHv-Rk",
            "authDomain": "smarthome-dadn.firebaseapp.com",
            "databaseURL": "https://smarthome-dadn-default-rtdb.asia-southeast1.firebasedatabase.app",
            "storageBucket": "smarthome-dadn.appspot.com",
            "serviceAccount": "key.json"
        }
        firebase = pyrebase.initialize_app(config)
        storage = firebase.storage()
        all_files = storage.child("images/").list_files()
        count = 1
        for file in all_files:
            # print(file.name)
            if self.validURL(file.name):
                # print("pass valid")
                homeID, personName, imageName = self.findHomeID(file.name)
                if (homeID == HOME_ID):
                    # print("pass home id")
                    z=storage.child(file.name).get_url(None)
                    if count == 1:
                        startPoint = z.rfind("images")
                        z = z[:startPoint-3] + z[startPoint+9:]
                    parentDirectory = './Data'
                    path = os.path.join(parentDirectory, personName)
                    if os.path.exists(path) == False:
                        os.mkdir(path)  
                    self.downloadImage(z, "Data/"+personName+'/'+imageName+".jpeg")
                    count += 1
        return 1
        # except:
        #     print("Error while loading Data from Database")
        #     return 0