import cv2
import time
import threading
import mediapipe as mp
import numpy as np
from collections import deque
from Backend.database import save_data

# --- 상수 및 설정 ---
ABSENCE_THRESHOLD_S = 2.0
RETURN_CONFIRM_S = 1.0
BUFFER_SIZE = 5

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# --- 전역 상태 및 스레드 락 ---
cap = None
is_running = False
capture_thread = None
current_subject = ""  # 현재 공부 중인 과목

# 웹 라우트에서 가져갈 최신 프레임과 데이터
latest_frame = None
latest_data = {"error": "camera off"}
lock = threading.Lock()

# --- Mediapipe 초기화 ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True
)

def calculate_ear(landmarks, eye_indices, w, h):
    points = []
    for idx in eye_indices:
        lm = landmarks[idx]
        x, y = int(lm.x * w), int(lm.y * h)
        points.append((x, y))

    A = np.linalg.norm(np.array(points[1]) - np.array(points[5]))
    B = np.linalg.norm(np.array(points[2]) - np.array(points[4]))
    C = np.linalg.norm(np.array(points[0]) - np.array(points[3]))

    return (A + B) / (2.0 * C)

class AbsenceDetector:
    def __init__(self):
        self.is_absent = False
        self.absence_start = None
        self.return_since = None
        self.last_seen_ts = time.time()
        self.buffer = deque(maxlen=BUFFER_SIZE)
        
        self.absence_count = 0
        self.total_absence_s = 0.0

    def update(self, face_present: bool):
        now = time.time()
        
        self.buffer.append(face_present)
        smoothed_present = sum(self.buffer) > len(self.buffer) // 2

        if smoothed_present:
            self.last_seen_ts = now
            if self.is_absent:
                if self.return_since is None:
                    self.return_since = now
                elif now - self.return_since >= RETURN_CONFIRM_S:
                    self.is_absent = False
                    if self.absence_start:
                        self.total_absence_s += (now - self.absence_start)
                        self.absence_count += 1
                        self.absence_start = None
                    self.return_since = None
            else:
                self.return_since = None
        else:
            self.return_since = None
            if not self.is_absent:
                if (now - self.last_seen_ts) >= ABSENCE_THRESHOLD_S:
                    self.is_absent = True
                    self.absence_start = self.last_seen_ts

    def get_current_absence_duration(self):
        if self.is_absent and self.absence_start:
            return time.time() - self.absence_start
        return 0.0

detector = AbsenceDetector()

def _capture_loop():
    global cap, is_running, latest_frame, latest_data, detector
    last_save_time = 0

    while is_running:
        if cap is None or not cap.isOpened():
            time.sleep(0.1)
            continue

        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        face_present = bool(results.multi_face_landmarks)
        detector.update(face_present)

        current_data = {
            "face_detected": face_present,
            "is_absent": detector.is_absent,
            "absence_count": detector.absence_count,
            "total_absence_s": round(detector.total_absence_s, 1),
            "current_absence_s": round(detector.get_current_absence_duration(), 1),
            "ear": 0.0,
            "state": "absent" if detector.is_absent else "searching..."
        }

        status_text = "No Face"
        status_color = (0, 0, 255)

        if face_present:
            face_landmarks = results.multi_face_landmarks[0]
            left_ear = calculate_ear(face_landmarks.landmark, LEFT_EYE, w, h)
            right_ear = calculate_ear(face_landmarks.landmark, RIGHT_EYE, w, h)
            ear = (left_ear + right_ear) / 2.0
            current_data["ear"] = float(ear)

            if ear < 0.2:
                current_data["state"] = "sleepy"
                status_text = "Eyes Closed (Sleepy)"
                status_color = (0, 165, 255)
            else:
                current_data["state"] = "focused"
                status_text = "Eyes Open (Focused)"
                status_color = (0, 255, 0)

            for idx in LEFT_EYE + RIGHT_EYE:
                lm = face_landmarks.landmark[idx]
                cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 2, (255, 0, 0), -1)

        border_color = (0, 0, 220) if detector.is_absent else (0, 200, 80)
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), border_color, 3)
        cv2.rectangle(frame, (0, h - 40), (w, h), (30, 30, 30), -1)

        cv2.putText(frame, f"State: {status_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"Absence Count: {detector.absence_count}", (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        if detector.is_absent:
            cv2.putText(frame, f"Absent: {int(current_data['current_absence_s'])}s", (w - 150, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 255), 1)

        with lock:
            _, buffer = cv2.imencode('.jpg', frame)
            latest_frame = buffer.tobytes()

        now = time.time()
        if now - last_save_time >= 3:
            with lock:
                current_data["subject"] = current_subject
                latest_data = current_data
                save_data(current_data)
            last_save_time = now

def start_camera():
    global cap, is_running, capture_thread

    if not is_running:
        cap = cv2.VideoCapture(0)
        is_running = True
        capture_thread = threading.Thread(target=_capture_loop, daemon=True)
        capture_thread.start()
    return True

def stop_camera():
    global cap, is_running, latest_data, latest_frame

    is_running = False
    time.sleep(0.5)

    with lock:
        if cap is not None:
            cap.release()
            cap = None
        latest_data = {"error": "camera off"}
        latest_frame = None
    return True

def generate_frames():
    while True:
        with lock:
            running = is_running
            frame_bytes = latest_frame

        if not running:
            time.sleep(0.1)
            continue

        if frame_bytes is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)

def get_focus_data():
    with lock:
        return latest_data

def set_current_subject(subject):
    global current_subject
    current_subject = subject