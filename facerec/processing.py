import multiprocessing
import queue
import time


class FaceDetectionWorker:
    @classmethod
    def new_process(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        return multiprocessing.Process(target=obj.run)

    def __init__(self, image_queue, result_queue):
        # affinity: main
        self.image_queue = image_queue
        self.result_queue = result_queue

    def _get_latest_image(self):
        image = None
        try:
            while True:
                image = self.image_queue.get(False)
        except queue.Empty:
            pass
        return image

    def run(self):
        # affinity: worker
        import face_recognition
        print('{} booted.'.format(self.__class__.__name__))

        while True:
            image = self._get_latest_image()
            if type(image) == str and image == 'quit':
                self.result_queue.put('quit')
                break

            if image is None:
                time.sleep(0.1)
                continue

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            pairs = list(zip(face_locations, [enc.tolist() for enc in face_encodings]))

            self.result_queue.put(pairs)
