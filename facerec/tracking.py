import datetime
import multiprocessing
import time

import numpy as np
import queue


class FaceRecognitionWorker:
    @classmethod
    def new_process(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        return multiprocessing.Process(target=obj.run)

    def __init__(self, face_pairs_queue):
        self.face_pairs_queue = face_pairs_queue

        self.known_encodings = []
        self.known_names = []

    def run(self):
        import face_recognition

        print("Loading known face image(s)")
        obama_image = face_recognition.load_image_file("webcam_tracking/obama_small.jpg")
        self.known_encodings += [face_recognition.face_encodings(obama_image)[0]]
        self.known_names += ['Barack Obama']

        name_generator = ('Person {}'.format(i) for i in range(1, 10000000))

        print('{} booted.'.format(self.__class__.__name__))

        fps_time = time.time()
        frame_count = 0

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
                match = face_recognition.compare_faces(self.known_encodings, face_encoding)

                if any(match):
                    index = match.index(True)
                    name = self.known_names[index]
                else:
                    name = next(name_generator)

                    self.known_encodings.append(face_encoding)
                    self.known_names.append(name)

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
