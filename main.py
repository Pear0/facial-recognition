import multiprocessing

import psutil

from facerec import cameras, processing, tracking


def main():
    image_queue = multiprocessing.Queue(1)
    face_pairs_queue = multiprocessing.Queue(8)

    for _ in range(3):
        worker = processing.FaceDetectionWorker.new_process(image_queue, face_pairs_queue)
        worker.start()

        process = psutil.Process(pid=worker.pid)

        if hasattr(process, 'cpu_affinity'):
            cpu_list = process.cpu_affinity()
            process.cpu_affinity(cpu_list[0: len(cpu_list) - 1])
        else:
            process.nice(process.nice() + 1)

    tracking.FaceRecognitionWorker.new_process(face_pairs_queue).start()

    try:
        camera = cameras.PiCamera()
    except ImportError:
        camera = cameras.CvCamera()

    while True:
        output = camera.capture()
        image_queue.put(output)


if __name__ == '__main__':
    main()
