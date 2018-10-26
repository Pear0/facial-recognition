import datetime
import multiprocessing
import time
import os
import numpy as np
import queue
import re
import json

class FaceRecognitionWorker:
    @classmethod
    def new_process(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        return multiprocessing.Process(target=obj.run)

    def __init__(self, face_pairs_queue):
        self.face_pairs_queue = face_pairs_queue

        self.known_encodings = []
        self.known_names = []

    def scan_known_people(self, known_people_folder):
        import face_recognition

        known_names = []
        known_face_encodings = []

        for file in self.image_files_in_folder(known_people_folder):
            basename = os.path.splitext(os.path.basename(file))[0]
            img = face_recognition.load_image_file(file)
            encodings = face_recognition.face_encodings(img)

            if len(encodings) > 1:
                print("WARNING: More than one face found in {}. Only considering the first face.".format(file))

            if len(encodings) == 0:
                print("WARNING: No faces found in {}. Ignoring file.".format(file))
            else:
                known_names.append(basename)
                known_face_encodings.append(encodings[0])

        return known_names, known_face_encodings

    def image_files_in_folder(self, folder):
        return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]



    def run(self):
        import face_recognition

        print("Loading known face image(s)")
        #obama_image = face_recognition.load_image_file("webcam_tracking/obama_small.jpg")
        #self.known_encodings += [face_recognition.face_encodings(obama_image)[0]]
        #self.known_names += ['Barack Obama']

        self.known_names, self.known_face_encodings = self.scan_known_people("webcam_tracking")

        name_generator = ('Person {}'.format(i) for i in range(1, 10000000))

        print('{} booted.'.format(self.__class__.__name__))

        fps_time = time.time()
        frame_count = 0
        data = []

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

                if name not in data:
                    data.append(name)
                #print (data)
                with open('data.json', 'w') as outfile:
                    json.dump(data, outfile)
                print("{} - I see someone named {}!".format(datetime.datetime.now(), name))

            if time.time() - st > 0.5:
                print('Face recognition took {} seconds'.format(time.time() - st))

            curr_time = time.time()
            frame_count += 1
            if curr_time - fps_time > 1:
                fps = frame_count / (curr_time - fps_time)
                print('Detections ran {} times in {} seconds ({} times/s)'
                      .format(frame_count, curr_time - fps_time, fps))
                frame_count = 0
                fps_time = curr_time
