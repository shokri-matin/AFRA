import os
from typing import Type
import cv2
import datetime
import numpy as np
import json
from starlette.responses import FileResponse
from app.FaceRecognition.models import Dataset

import face_recognition

FRAME_THIKNESS = 3
FONT_THIKNESS = 2
IMGROOT = os.path.join(os.path.abspath(os.curdir), 'Predicted', 'Image')
VIDROOT = os.path.join(os.path.abspath(os.curdir), 'Predicted', 'Video')
SUBROOT = os.path.join(os.path.abspath(os.curdir), 'Predicted', 'Subtitle')

DICT_RESULTS = {}

class Singleton(Type):
    _instances ={}
    def __call__(cls, *args, **kwds):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwds)
        return cls._instances[cls]

class FaceModel(metaclass = Singleton):

    def __init__(self, model='large', tolerance=.5, db=None) -> None:
        self.model = model
        self.db = db
        self.tolerance = tolerance
        dataset = db.query(Dataset).all()
        self.json_encodings = [d.feature for d in dataset]
        self.list_encodings = [json.loads(je) for je in self.json_encodings]
        self.known_encodings = [np.array(le) for le in self.list_encodings]
        self.known_names = [d.name for d in dataset]

    def feature_extraction(self, path, filename):

        file_addr = os.path.join(path, filename)
        image = face_recognition.load_image_file(file_addr)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encoding = face_recognition.face_encodings(image, model= self.model)[0]

        return encoding

    def image_recognition(self, path, filename, model='large'):
        
        DICT_RESULTS = {}

        image_path = os.path.join(path, filename)
        image = face_recognition.load_image_file(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        locations = face_recognition.face_locations(image, model = model)
        encodings = face_recognition.face_encodings(image, locations)

        for face_encoding, face_location in zip(encodings, locations):
            distances = np.linalg.norm(self.known_encodings - face_encoding, axis=1)
            minvalue = np.min(distances)
            if minvalue <= self.tolerance:

                index = np.argmin(distances)
                match = None

                if index is not None:
                    match = self.known_names[index]

                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])

                    color = [0, 255, 0]
                    cv2.rectangle(image, top_left, bottom_right, color, FRAME_THIKNESS)

                    top_left = (face_location[3], face_location[2])
                    bottom_right = (face_location[1], face_location[2]+22)
                    cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
                    cv2.putText(image, match, (face_location[3]+10, face_location[2]+15),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), FONT_THIKNESS)
            else:
                match = 'Unknown'

            if match in DICT_RESULTS:
                loc_list = []
                loc_list.append(DICT_RESULTS[match])
                loc_list.append(face_location)
                DICT_RESULTS[match] = loc_list
            else:
                DICT_RESULTS[match] = face_location

        path = os.path.join(IMGROOT, filename)
        cv2.imwrite(path, image)

        return DICT_RESULTS

    def video_recognition(self, path, filename):

        video_path = os.path.join(path, filename)
        cap = cv2.VideoCapture(video_path)
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = cap.get(cv2.CAP_PROP_FPS)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        path = os.path.join(VIDROOT, filename)

        out = cv2.VideoWriter(path,cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width,frame_height))
        frame_number = 1

        matches = []
        base_time = datetime.timedelta(milliseconds=1000)
        line = 1
        while(frame_number < 100):
            
            ret, frame = cap.read()
            current_timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
            delta = datetime.timedelta(milliseconds=current_timestamp)
            
            print('frame {} / {}, time :{}'.format(frame_number, length, delta))
            print(ret)
            if ret == True:
                image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                locations = face_recognition.face_locations(image, model=self.model)
                encodings = face_recognition.face_encodings(image, locations)

                for face_encoding, face_location in zip(encodings, locations):

                    distances = np.linalg.norm(self.known_encodings - face_encoding, axis=1)
                    minvalue = np.min(distances)

                    if minvalue >= self.tolerance:
                        curr_match = 'Unknown'
                    else:
                        index = np.argmin(distances)
                        curr_match = self.known_names[index]

                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])

                    color = [0, 255, 0]
                    cv2.rectangle(image, top_left, bottom_right, color, FRAME_THIKNESS)

                    top_left = (face_location[3], face_location[2])
                    bottom_right = (face_location[1], face_location[2]+22)
                    cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
                    cv2.putText(image, curr_match, (face_location[3]+10, face_location[2]+15),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), FONT_THIKNESS)

                    if curr_match != 'Unknown':
                        matches.append(curr_match)

                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                out.write(image)
            else:
                break
            frame_number += 1
            
            if delta > base_time:
                base_time += datetime.timedelta(milliseconds=1000)
                line = self.write_to_subtitle(matches, filename, line)
                matches = []

        cap.release()
        out.release()
        file_location = os.path.join(SUBROOT, filename + '.srt')
        return FileResponse(file_location, media_type='application/octet-stream', filename=filename+'.srt')

    def write_to_subtitle(self, maches, filename, line):

        path = os.path.join(SUBROOT, filename + '.srt')
        with open(path, 'a') as f:
            comb_match = ''
            for match in maches:
                if match not in comb_match:
                    comb_match += match + ', '

            comb_match = comb_match.strip(' ')
            comb_match = comb_match.strip(',')
            if line == 1:
                f.write(str(line))
            else:
                f.write('\n')
                f.write('\n')
                f.write(str(line))

            f.write('\n')
            f.write(str(datetime.timedelta(milliseconds=1000*(line-1))) + ' --> ')
            f.write(str(datetime.timedelta(milliseconds=1000*(line))))
            f.write('\n')
            f.write(comb_match)

        return line+1