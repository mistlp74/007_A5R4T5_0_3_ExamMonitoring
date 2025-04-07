import cv2
import mediapipe as mp
import base64
import numpy as np

# Ініціалізація один раз
mp_face_detection = mp.solutions.face_detection
face_detection_model = mp_face_detection.FaceDetection(min_detection_confidence=0.2)

def process_frame(image_data):
    try:
        # Декодування Base64 -> OpenCV зображення
        nparr = np.frombuffer(base64.b64decode(image_data.split(',')[1]), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None or frame.size == 0:
            print("Порожній кадр — пропускаємо")
            return True  # Повертаємо True, щоб уникнути false-спрацювання

        # Детекція обличчя
        results = face_detection_model.process(frame)
        return bool(results.detections)
    except Exception as e:
        print(f"Помилка обробки кадру: {e}")
        return False

