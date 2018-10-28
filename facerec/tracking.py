import datetime
import multiprocessing
import time
import os
import numpy as np
import queue
import re
import json
import face_recognition

class FaceRecognitionWorker:
    @classmethod
    def new_process(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        return multiprocessing.Process(target=obj.run)

    def __init__(self, face_pairs_queue):
        self.face_pairs_queue = face_pairs_queue

        self.known_encodings = []
        self.known_names = []
        self.person_info = []

    def scan_known_people(self, known_people_folder):
        known_names = []
        known_face_encodings = []
        person_info = []

        for file in self.image_files_in_folder(known_people_folder):
            basename = os.path.splitext(os.path.basename(file))[0]
            splitBase = basename.split("_")
            if(len(splitBase) == 3 ):
                basename = splitBase[0] + " " + splitBase[1][0] + "."
                person_info.append([basename, splitBase[0] + " " + splitBase[1],
                                    splitBase[2]])

            img = face_recognition.load_image_file(file)
            encodings = face_recognition.face_encodings(img)

            if len(encodings) > 1:
                print("WARNING: More than one face found in {}. Only considering the first face.".format(file))

            if len(encodings) == 0:
                print("WARNING: No faces found in {}. Ignoring file.".format(file))
            else:
                known_names.append(basename)
                known_face_encodings.append(encodings[0])
        return known_names, known_face_encodings, person_info

    def image_files_in_folder(self, folder):
        return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]



    def run(self):
        print("Loading known face image(s)")
        self.known_names, self.known_face_encodings, self.person_info = self.scan_known_people("webcam_tracking")

        name_generator = ('Person {}'.format(i) for i in range(1, 10000))

        print('{} booted.'.format(self.__class__.__name__))

        fps_time = time.time()
        frame_count = 0
        data = []
        dump = {}
        checker = ['' for x in range(4)]
        frameTotal = 0
        bias = 4  #Number of frame allowed for mistake
        while True:
            try:
                face_pairs = self.face_pairs_queue.get(False)
            except queue.Empty:
                time.sleep(0.1)
                continue

            if type(face_pairs) == str and face_pairs == 'quit':
                break

            st = time.time()
            # Loop over each face found in the frame to see if it's someone we know.
            for face_location, face_encoding in face_pairs:
                face_encoding = np.array(face_encoding)

                # See if the face is a match for the known face(s)
                #match = face_recognition.compare_faces(self.known_encodings, face_encoding)

                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                result = list(distances <= 0.6)

                if any(result):
                    index = result.index(True)
                    name = self.known_names[index]
                else:
                    name = next(name_generator)

                    self.known_face_encodings.append(face_encoding)
                    self.known_names.append(name)

                checker[frameTotal%bias] = name

                if name not in data and checker.count(checker[0]) == len(checker):
                    data.append(name)
                    #Search person_info for it
                    full_name = name
                    gtid = "Unknown"
                    for i in range(len(self.person_info)):
                        if name == self.person_info[i][0]:
                            full_name = self.person_info[i][1]
                            gtid = self.person_info[i][2]
                    dump[name] = {'name': full_name, 'id': gtid}
                filename = 'Attendence ' + time.strftime("%m.%d") + '.json'
                with open(filename, 'w') as outfile:
                    json.dump(dump, outfile, sort_keys=True, indent=4)


                print("{} - I see someone named {}".format(datetime.datetime.now(), name))

            frameTotal += 1
