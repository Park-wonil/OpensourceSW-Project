import cv2
import time
import threading
import mediapipe as mp
import numpy as np
from collections import deque
from PIL import Image, ImageDraw, ImageFont
from Backend.database import save_data
from Vision.neck import NeckPostureDetector, draw_neck_overlay

# 한글 폰트 (우선순위 순으로 탐색)
_KOREAN_FONT_PATHS = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/NotoSansGothic-Regular.ttf",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
]
_korean_font_large = None
_korean_font_small = None

def _get_korean_fonts():
    global _korean_font_large, _korean_font_small
    if _korean_font_large is not None:
        return _korean_font_large, _korean_font_small
    for path in _KOREAN_FONT_PATHS:
        try:
            _korean_font_large = ImageFont.truetype(path, 28)
            _korean_font_small = ImageFont.truetype(path, 20)
            return _korean_font_large, _korean_font_small
        except Exception:
            continue
    _korean_font_large = ImageFont.load_default()
    _korean_font_small = ImageFont.load_default()
    return _korean_font_large, _korean_font_small


def _draw_korean_overlay(frame: np.ndarray, line1: str, line2: str) -> np.ndarray:
    """프레임 중앙에 반투명 배너와 한글 텍스트를 그린다."""
    h, w = frame.shape[:2]
    font_large, font_small = _get_korean_fonts()

    # OpenCV BGR → PIL RGB
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    banner_y1, banner_y2 = h // 2 - 52, h // 2 + 52
    draw.rectangle([(0, banner_y1), (w, banner_y2)], fill=(20, 20, 20, 158))

    # 첫째 줄
    bbox = draw.textbbox((0, 0), line1, font=font_large)
    tx = (w - (bbox[2] - bbox[0])) // 2
    draw.text((tx, banner_y1 + 12), line1, font=font_large, fill=(110, 231, 192, 255))

    # 둘째 줄
    bbox2 = draw.textbbox((0, 0), line2, font=font_small)
    tx2 = (w - (bbox2[2] - bbox2[0])) // 2
    draw.text((tx2, banner_y1 + 52), line2, font=font_small, fill=(210, 210, 210, 255))

    composited = Image.alpha_composite(pil_img.convert("RGBA"), overlay)
    return cv2.cvtColor(np.array(composited.convert("RGB")), cv2.COLOR_RGB2BGR)

# --- 상수 및 설정 ---
ABSENCE_THRESHOLD_S = 2.0
RETURN_CONFIRM_S = 1.0
BUFFER_SIZE = 5

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# --- 상수 ---
STRETCH_INTERVAL_S = 3600.0   # 1시간마다 스트레칭 알림
STRETCH_SHOW_S     = 8.0      # 오버레이 표시 지속 시간

# --- 전역 상태 및 스레드 락 ---
cap = None
is_running = False
capture_thread = None
current_subject = ""   # 현재 공부 중인 과목
current_username = ""  # 현재 로그인 유저 username

# 웹 라우트에서 가져갈 최신 프레임과 데이터
latest_frame = None
latest_data = {"error": "camera off"}
lock = threading.Lock()

# 스트레칭 알림 상태
_camera_start_time  = None
_stretch_shown_at   = 0.0   # 마지막으로 알림 표시를 시작한 시각

# --- Mediapipe 초기화 (카메라 시작 후 lazy loading) ---
# mp.solutions.face_mesh는 mediapipe가 동적으로 등록하는 속성이라 Pylance가 인식 못함 → 무시
mp_face_mesh = mp.solutions.face_mesh  # type: ignore[attr-defined]
face_mesh = None

def _get_face_mesh():
    global face_mesh
    if face_mesh is None:
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True
        )
    return face_mesh

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
neck_detector = NeckPostureDetector()  # 거북목 감지기

def _capture_loop():
    global cap, is_running, latest_frame, latest_data, detector, neck_detector
    global _camera_start_time, _stretch_shown_at
    last_save_time = 0

    while is_running:
        face_mesh_model = _get_face_mesh()

        if cap is None or not cap.isOpened():
            time.sleep(0.1)
            continue

        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh_model.process(rgb)

        # 거북목 감지 (같은 rgb 프레임 재사용 - 추가 변환 없음)
        neck_data = neck_detector.update(rgb)

        face_present = bool(results.multi_face_landmarks)
        detector.update(face_present)

        current_data = {
            "face_detected": face_present,
            "is_absent": detector.is_absent,
            "absence_count": detector.absence_count,
            "total_absence_s": round(detector.total_absence_s, 1),
            "current_absence_s": round(detector.get_current_absence_duration(), 1),
            "ear": 0.0,
            "state": "absent" if detector.is_absent else "searching...",
            **neck_data   # 거북목 필드 병합
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
        draw_neck_overlay(frame, neck_data)   # 거북목 상태 오버레이
        cv2.rectangle(frame, (0, h - 40), (w, h), (30, 30, 30), -1)

        cv2.putText(frame, f"State: {status_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"Absence Count: {detector.absence_count}", (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        if detector.is_absent:
            cv2.putText(frame, f"Absent: {int(current_data['current_absence_s'])}s", (w - 150, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 255), 1)

        # 스트레칭 알림 오버레이
        now = time.time()
        elapsed = now - _camera_start_time if _camera_start_time else 0.0
        in_show_window = (now - _stretch_shown_at) < STRETCH_SHOW_S

        if elapsed >= STRETCH_INTERVAL_S and not in_show_window:
            _stretch_shown_at   = now
            _camera_start_time  = now   # 다음 1시간 카운트 리셋

        stretch_active = (now - _stretch_shown_at) < STRETCH_SHOW_S and _stretch_shown_at > 0.0
        current_data["stretch_reminder"] = stretch_active

        if stretch_active:
            frame = _draw_korean_overlay(
                frame,
                "공부한지 1시간 되었어요!",
                "잠시 스트레칭 해보는것은 어떨까요?!",
            )

        with lock:
            _, buffer = cv2.imencode('.jpg', frame)
            latest_frame = buffer.tobytes()

        now = time.time()
        if now - last_save_time >= 3:
            with lock:
                current_data["subject"] = current_subject
                current_data["username"] = current_username
                latest_data = current_data
                save_data(current_data)
            last_save_time = now

def start_camera():
    global cap, is_running, capture_thread, _camera_start_time, _stretch_shown_at

    if not is_running:
        cap = cv2.VideoCapture(0)
        is_running = True
        _camera_start_time = time.time()
        _stretch_shown_at  = 0.0
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

def set_current_username(username):
    global current_username
    current_username = username
