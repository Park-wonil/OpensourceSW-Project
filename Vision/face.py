import cv2

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
is_running = False  # 🔥 상태 관리 추가

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
    if cap is not None:
        cap.release()
        cap = None
    is_running = False
    return True

def generate_frames():
    global cap, is_running

    while True:
        if not is_running or cap is None:
            # 🔥 빈 프레임이라도 보내줘야 브라우저가 안 죽음
            import time
            time.sleep(0.1)
            continue

        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def get_focus_data():
    global cap

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