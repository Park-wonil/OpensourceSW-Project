import cv2
import time
import threading
import mediapipe as mp
import numpy as np
import sqlite3
from collections import deque
from flask import Flask, Response, jsonify, render_template

# ===================== 설정 =====================
ABSENCE_THRESHOLD_S = 2.0
RETURN_CONFIRM_S = 1.0
BUFFER_SIZE = 5

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# ===================== 전역 상태 =====================
cap = None
is_running = False
capture_thread = None

latest_frame = None
latest_data = {"error": "camera off"}
lock = threading.Lock()

# ===================== Mediapipe =====================
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True
)

# ===================== DB =====================
# DB 초기화 (테이블 생성)
def init_db():
    conn = sqlite3.connect("focus.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS focus_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        state TEXT,
        absence_count INTEGER,
        total_absence REAL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# DB에 데이터 저장 (로그 기록)
def save_data(data):
    conn = sqlite3.connect("focus.db")
    c = conn.cursor()
    c.execute("""
    INSERT INTO focus_log (timestamp, state, absence_count, total_absence)
    VALUES (?, ?, ?, ?)
    """, (
        time.time(),              # 현재 시간
        data["state"],           # 상태 (focused, sleepy, absent)
        data["absence_count"],   # 이탈 횟수
        data["total_absence_s"]  # 총 이탈 시간
    ))
    conn.commit()
    conn.close()

# ===================== EAR 계산 =====================
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

# ===================== 이탈 감지 =====================
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

# ===================== 캡처 루프 =====================
# 카메라 프레임을 계속 읽으면서 상태 분석하는 핵심 루프
def _capture_loop():
    global cap, is_running, latest_frame, latest_data

    while is_running:
        if cap is None or not cap.isOpened():
            time.sleep(0.1)
            continue

        ret, frame = cap.read()
        if not ret:
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
            "state": "absent" if detector.is_absent else "searching"
        }

        if face_present:
            face_landmarks = results.multi_face_landmarks[0]
            left_ear = calculate_ear(face_landmarks.landmark, LEFT_EYE, w, h)
            right_ear = calculate_ear(face_landmarks.landmark, RIGHT_EYE, w, h)
            ear = (left_ear + right_ear) / 2.0
            current_data["ear"] = float(ear)

            if ear < 0.2:
                current_data["state"] = "sleepy"
            else:
                current_data["state"] = "focused"

        # 🔥 백엔드 핵심: 데이터 저장 + 프레임 공유
        with lock:
            latest_data = current_data   # API에서 가져갈 데이터
            save_data(current_data)     # DB 저장
            _, buffer = cv2.imencode('.jpg', frame)
            latest_frame = buffer.tobytes()  # 영상 스트리밍용

# ===================== 카메라 제어 =====================
# 카메라 시작 (API에서 호출됨)
def start_camera():
    global cap, is_running, capture_thread

    if not is_running:
        cap = cv2.VideoCapture(0)
        is_running = True
        capture_thread = threading.Thread(target=_capture_loop, daemon=True)
        capture_thread.start()

# 카메라 종료 (API에서 호출됨)
def stop_camera():
    global cap, is_running
    is_running = False
    time.sleep(0.2)
    if cap:
        cap.release()

# ===================== 스트리밍 =====================
# 영상 데이터를 웹으로 계속 보내주는 함수
def generate_frames():
    global latest_frame
    while True:
        if not is_running:
            break
        with lock:
            frame = latest_frame
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ===================== Flask (백엔드 핵심) =====================
app = Flask(__name__)

# 메인 페이지 (HTML 렌더링)
@app.route("/")
def index():
    return render_template("index.html")

# 카메라 시작 API
@app.route("/start")
def start():
    start_camera()
    return jsonify({"status": "started"})

# 카메라 종료 API
@app.route("/stop")
def stop():
    stop_camera()
    return jsonify({"status": "stopped"})

# 현재 상태 데이터 API (프론트에서 fetch로 호출)
@app.route("/data")
def data():
    with lock:
        return jsonify(latest_data)

# 영상 스트리밍 API
@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# 집중도 점수 계산 API
@app.route("/score")
def score():
    conn = sqlite3.connect("focus.db")
    c = conn.cursor()

    c.execute("SELECT state FROM focus_log")
    rows = c.fetchall()

    total = len(rows)
    focus = sum(1 for r in rows if r[0] == "focused")
    sleepy = sum(1 for r in rows if r[0] == "sleepy")
    absent = sum(1 for r in rows if r[0] == "absent")

    conn.close()

    if total == 0:
        return jsonify({"score": 0})

    score = (focus / total) * 100 - (sleepy * 2) - (absent * 5)

    return jsonify({
        "score": round(score, 1),
        "focus": focus,
        "sleepy": sleepy,
        "absent": absent
    })

# ===================== 실행 =====================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
