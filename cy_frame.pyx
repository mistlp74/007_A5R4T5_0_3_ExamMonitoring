 # cy_frame.pyx

import cv2
import mediapipe as mp
import base64
import numpy as np
import time
cimport numpy as cnp

cdef double last_check_time = 0
cdef double CHECK_INTERVAL = 0.5

mp_face_detection = mp.solutions.face_detection
face_detection_model = mp_face_detection.FaceDetection(min_detection_confidence=0.2)

cdef bint gpu_available = cv2.cuda.getCudaEnabledDeviceCount() > 0

cpdef bint process_frame(str image_data):
    global last_check_time

    cdef double now = time.time()
    cdef bytes raw_data
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] nparr
    cdef object frame, results

    if now - last_check_time < CHECK_INTERVAL:
        return True

    last_check_time = now

    try:

        raw_data = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(raw_data, dtype=np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None or frame.size == 0:
            print("empty frame - skip")
            return True

        if gpu_available:
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)

            pyramid_gpu = [gpu_frame]
            for i in range(4):
                pyramid_gpu.append(cv2.cuda.pyrDown(pyramid_gpu[i]))

            for img_gpu in pyramid_gpu:
                img = img_gpu.download()

                results = face_detection_model.process(img)
                if results.detections:
                    return True
        else:
            results = face_detection_model.process(frame)
            if results.detections:
                return True

    except Exception as e:
        print(f"frame processing error: {e}")
        return False