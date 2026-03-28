import cv2
import time

# 전역 상태
cap = None
is_running = False

# 얼굴 인식 모델
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def start_camera():
    global cap, is_running

    if not is_running:
        cap = cv2.VideoCapture(0)
        is_running = True

    return True


def stop_camera():
    global cap, is_running

    # 먼저 상태 OFF
    is_running = False

    # 카메라 해제 (여기서만 담당)
    if cap is not None:
        cap.release()
        cap = None

    return True


def generate_frames():
    global cap, is_running

    try:
        while True:
            if not is_running or cap is None:
                break

            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    finally:
        # 🔥 이게 핵심
        if cap is not None:
            cap.release()


def get_focus_data():
    global cap

    # 카메라 꺼져있으면
    if cap is None:
        return {"error": "camera off"}

    ret, frame = cap.read()

    if not ret:
        return {"error": "no frame"}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    return {
        "face_detected": len(faces) > 0,
        "face_count": len(faces)
    }
