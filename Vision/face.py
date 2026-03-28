import cv2
import time
import mediapipe as mp
import numpy as np

# 전역 상태
cap = None
is_running = False

# Mediapipe 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True
)

# 눈 랜드마크 (Mediapipe 기준)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


# EAR 계산 함수 (눈 감김 판단)
def calculate_ear(landmarks, eye_indices, w, h):
    points = []

    for idx in eye_indices:
        lm = landmarks[idx]
        x, y = int(lm.x * w), int(lm.y * h)
        points.append((x, y))

    # EAR 공식
    A = np.linalg.norm(np.array(points[1]) - np.array(points[5]))
    B = np.linalg.norm(np.array(points[2]) - np.array(points[4]))
    C = np.linalg.norm(np.array(points[0]) - np.array(points[3]))

    ear = (A + B) / (2.0 * C)
    return ear


def start_camera():
    global cap, is_running

    if not is_running:
        cap = cv2.VideoCapture(0)
        is_running = True

    return True


def stop_camera():
    global cap, is_running

    is_running = False
    time.sleep(0.2)

    if cap is not None:
        cap.release()
        cap = None

    return True


def generate_frames():
    global cap, is_running

    while True:
        if not is_running:
            break

        if cap is None:
            time.sleep(0.1)
            continue

        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        h, w, _ = frame.shape

        # Mediapipe 처리
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        status_text = "No Face"

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:

                # EAR 계산
                left_ear = calculate_ear(face_landmarks.landmark, LEFT_EYE, w, h)
                right_ear = calculate_ear(face_landmarks.landmark, RIGHT_EYE, w, h)

                ear = (left_ear + right_ear) / 2.0

                # 눈 감김 판단
                if ear < 0.2:
                    status_text = "Eyes Closed 😴"
                else:
                    status_text = "Eyes Open 👀"

                # 눈 좌표 찍기 (디버그용)
                for idx in LEFT_EYE + RIGHT_EYE:
                    lm = face_landmarks.landmark[idx]
                    x, y = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # 상태 표시
        cv2.putText(frame, status_text, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255), 2)

        # 스트리밍
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

    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return {
            "face_detected": False,
            "focus": "no face"
        }

    face_landmarks = results.multi_face_landmarks[0]

    left_ear = calculate_ear(face_landmarks.landmark, LEFT_EYE, w, h)
    right_ear = calculate_ear(face_landmarks.landmark, RIGHT_EYE, w, h)

    ear = (left_ear + right_ear) / 2.0

    if ear < 0.2:
        state = "sleepy"
    else:
        state = "focused"

    return {
        "face_detected": True,
        "ear": float(ear),
        "state": state
    }

