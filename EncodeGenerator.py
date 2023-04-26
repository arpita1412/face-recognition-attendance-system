import cv2
import os
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-system-cab91-default-rtdb.firebaseio.com/",
    'storageBucket': "face-attendance-system-cab91.appspot.com"
})

folderPath = 'images'
PathList = os.listdir(folderPath)
print(PathList)
imgList = []
studentIds = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    # sending image to the storage in realtime database
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

    # separating the jpg from id
    # print(path)
    # print(os.path.splitext(path)[0])
print(studentIds)

# encoding the images


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


print("encoding started...")
encodeListKnown = findEncodings(imgList)
# adding two into a single list
encodeListKnownIds = [encodeListKnown, studentIds]
print("encoding completed..")

# creating a pickle file
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownIds,file)
file.close()
print("file saved")


