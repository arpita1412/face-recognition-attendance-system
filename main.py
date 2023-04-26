import pickle
import cvzone
import numpy as np
import cv2
import os
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import  datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-system-cab91-default-rtdb.firebaseio.com/",
    'storageBucket': "face-attendance-system-cab91.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # width
cap.set(4, 480)  # height

imgBackground = cv2.imread("resources/background.png")

# importing all the modes(1.png,2.png,3.png,4.png) into a list
folderModePath = 'resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# load the encoding file
print("Loading Encode File....")
file = open('EncodeFile.p', 'rb')
encodeListKnownIds = pickle.load(file)
file.close()
# separate 2 from the list
encodeListKnown, studentIds = encodeListKnownIds
# print(studentIds)  [for testing if it's working or not]
print("Encode File Loaded....")

modeType = 0
counter = 0
index = -1
imgStudent = []

while True:
    Success, img = cap.read()
    # scale our image to 1/4th as it takes a lot of computational time
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    # converting into rgb from bgr
    # OpenCV uses BGR image format. So, when we read an image using cv2.imread() it interprets in BGR format by default.
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # find the encoding of current images taken from webcam
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    # we don't want the encoding of entire image, hence we pass the location from where image is extracted and encoded

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:

         # comparing encoding of current face and already known face, also finding distance


        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            # finding index of the least distance
            matchIndex = np.argmin(faceDis)
            # print("matchIndex", matchIndex)

            # checking if match index is equal to true in matches[matchIndex]
            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                # print("known faces detected")
                # print(studentIds[matchIndex])
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
        if counter != 0:
            if counter == 1:
                # get the data from database
                studentInfo = db.reference(f'students/{id}').get()
                print(studentInfo)
                # get the image from storage
                blob = bucket.get_blob(f'images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed >30:
                    ref = db.reference(f'students/{id}')
                    studentInfo['total_attendance'] += 1
                    # keep updating in database also simultaneously
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2
                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),cv2.FONT_HERSHEY_COMPLEX, 1,
                            (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                            (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                            (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['CGPA']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['heading1']), (860, 665), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (30, 30, 30), 1)
                    cv2.putText(imgBackground, str(studentInfo['current_sem']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['heading2']), (950, 665), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (30, 30, 30), 1)
                    cv2.putText(imgBackground, str(studentInfo['pass_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['heading3']), (1090, 665), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (30, 30, 30), 1)

                    # to center the name
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    imgBackground[175:175+216, 909:909+216] = imgStudent


                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


    else:
        modeType = 0
        counter = 0



    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
