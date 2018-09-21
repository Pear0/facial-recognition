import numpy as np


class PiCamera:
    def __init__(self):
        import picamera
        self._camera = picamera.PiCamera()
        self._camera.resolution = (320, 240)

    def capture(self):
        out = np.empty((240, 320, 3), dtype=np.uint8)
        self._camera.capture(out, format="rgb", use_video_port=True)

        return out


class CvCamera:
    def __init__(self):
        import cv2
        self._video_capture = cv2.VideoCapture(0)

    def capture(self):
        import cv2
        ret, frame = self._video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        return small_frame[:, :, ::-1]
