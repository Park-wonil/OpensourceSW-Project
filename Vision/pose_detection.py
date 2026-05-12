"""
거북목(Forward Head Posture) 감지 모듈
======================================
MediaPipe Pose를 사용해 귀-어깨 벡터와 수직축 사이의 각도로 거북목을 판정

측정 원리
  - 좌우 귀(landmark 7, 8) 중점과 좌우 어깨(landmark 11, 12) 중점을 잇는 벡터를
    수직축(위 방향)에 대해 측정
  - 0° = 머리가 수직으로 똑바로 세워진 자세
  - 각도가 클수록 목이 앞으로 기울어진 거북목 자세

자세 판정 기준
  - Good  :  0° ~ 20°
  - Warn  : 20° ~ 35°
  - Bad   : 35° 이상  → ALERT_HOLD_S 초 지속 시 알림 발생 


/detect API 응답에 추가될? 필드
  pose_detected    (bool)  : 포즈 랜드마크 감지 여부
  neck_angle       (float) : 현재 목 기울기 각도 (도)
  neck_status      (str)   : "good" | "warn" | "bad" | "unknown"
  neck_bad_seconds (float) : 나쁜 자세 연속 지속 시간 (초)
  neck_should_alert(bool)  : 프론트엔드에 알림을 보낼 타이밍이면 True
  neck_alert_count (int)   : 누적 알림 횟수

프론트엔드 연동 형식 (index.html)
  // checkAll() 안의 fetch('/detect') 콜백에서:
  if (data.neck_should_alert) {
      showNeckAlert();
  }
  updateNeckBadge(data.neck_status, data.neck_angle);
"""

import math
import time
import cv2
import numpy as np
import mediapipe as mp

# --- 판정값 ---
NECK_WARN_ANGLE = 20.0   # 도(°) — 이 이상이면 경고
NECK_BAD_ANGLE  = 35.0   # 도(°) — 이 이상이면 나쁜 자세
ALERT_HOLD_S    = 10.0   # 나쁜 자세 지속 n초 후 알림
ALERT_COOLDOWN_S = 300.0  # 알림 재발생 최소 간격 (초)

# --- MediaPipe Pose 초기화 (모듈 로드 시 1회) ---
_mp_pose = mp.solutions.pose
_pose = _mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0,       # Lite 모델: 실시간 성능 우선
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)


def _calc_neck_angle(lm) -> float:
    #귀 중심 → 어깨 중심 벡터와 수직축 사이 각도(도) 반환
    ear_mid = np.array([
        (lm[7].x + lm[8].x) / 2,
        (lm[7].y + lm[8].y) / 2,
    ])
    shoulder_mid = np.array([
        (lm[11].x + lm[12].x) / 2,
        (lm[11].y + lm[12].y) / 2,
    ])
    vec = ear_mid - shoulder_mid
    norm = np.linalg.norm(vec)
    if norm < 1e-6:
        return 0.0
    # 이미지 좌표계: 위쪽 = (0, -1)
    cos_val = np.dot(vec / norm, np.array([0.0, -1.0]))
    return math.degrees(math.acos(np.clip(cos_val, -1.0, 1.0)))


class NeckPostureDetector:
    
    #프레임마다 update(rgb_frame)를 호출해 거북목 여부를 판정
    #반환값 dict는 current_data에 **스프레드해서 사용
    

    def __init__(self):
        self.neck_angle = 0.0
        self.status = "good"            # "good" | "warn" | "bad" | "unknown"
        self._bad_start: float | None = None
        self.bad_seconds = 0.0
        self._last_alert = 0.0
        self.alert_count = 0

    def update(self, frame_rgb: np.ndarray) -> dict:
        results = _pose.process(frame_rgb)

        if not results.pose_landmarks:
            self.status = "unknown"
            return self._make(False)

        lm = results.pose_landmarks.landmark
        # 양 귀·어깨 visibility가 낮으면 신뢰도 부족으로 skip
        if any(lm[i].visibility < 0.5 for i in [7, 8, 11, 12]):
            self.status = "unknown"
            return self._make(False)

        angle = _calc_neck_angle(lm)
        self.neck_angle = angle
        now = time.time()

        if angle >= NECK_BAD_ANGLE:
            self.status = "bad"
            if self._bad_start is None:
                self._bad_start = now
            self.bad_seconds = now - self._bad_start
        elif angle >= NECK_WARN_ANGLE:
            self.status = "warn"
            self._bad_start = None
            self.bad_seconds = 0.0
        else:
            self.status = "good"
            self._bad_start = None
            self.bad_seconds = 0.0

        should_alert = (
            self.status == "bad"
            and self.bad_seconds >= ALERT_HOLD_S
            and (now - self._last_alert) >= ALERT_COOLDOWN_S
        )
        if should_alert:
            self._last_alert = now
            self.alert_count += 1

        return self._make(True, angle, should_alert)

    def _make(self, detected: bool, angle: float = 0.0, should_alert: bool = False) -> dict:
        return {
            "pose_detected":     detected,
            "neck_angle":        round(angle, 1),
            "neck_status":       self.status if detected else "unknown",
            "neck_bad_seconds":  round(self.bad_seconds, 1),
            "neck_should_alert": should_alert,
            "neck_alert_count":  self.alert_count,
        }


# ---------------------------------------------------------------------------
# 프레임 오버레이  vision.py의 _capture_loop에서 선택적으로 사용
# ---------------------------------------------------------------------------

_STATUS_COLOR = {
    "good":    (0, 220, 100),   # 초록
    "warn":    (0, 165, 255),   # 주황
    "bad":     (0, 60, 255),    # 빨강
    "unknown": (150, 150, 150), # 회색
}
_STATUS_LABEL = {
    "good": "Good", "warn": "Warn", "bad": "BAD!", "unknown": "--",
}


def draw_neck_overlay(frame: np.ndarray, neck_data: dict) -> None:
    
    #캡처 프레임에 거북목 상태 텍스트를 그린다.
    #vision.py의 _capture_loop에서 face overlay 직후에 호출

     #   Usage:
     #   draw_neck_overlay(frame, neck_data)
    
    status = neck_data.get("neck_status", "unknown")
    angle  = neck_data.get("neck_angle", 0.0)
    color  = _STATUS_COLOR.get(status, (150, 150, 150))
    label  = _STATUS_LABEL.get(status, "--")
    cv2.putText(
        frame,
        f"Neck: {angle}deg ({label})",
        (10, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6, color, 2,
    )


# ---------------------------------------------------------------------------
# 프론트엔드 스트레칭 가이드 (server.py 또는 index.html에서 참조)
# ---------------------------------------------------------------------------

STRETCHING_GUIDE = [
    {"title": "턱 당기기 (Chin Tuck)",         "desc": "턱을 뒤로 당겨 5초 유지, 10회 반복"},
    {"title": "목 좌우 기울이기",               "desc": "귀를 어깨 쪽으로 천천히 기울여 15초 유지, 양쪽 각 3회"},
    {"title": "목 앞뒤 스트레칭",               "desc": "고개를 천천히 앞으로 숙였다가 뒤로 젖히기, 각 10초"},
    {"title": "어깨 뒤로 돌리기",               "desc": "어깨를 크게 뒤로 10회 돌리기"},
    {"title": "가슴 펴기 (Chest Opener)",       "desc": "양손을 등 뒤에서 깍지 끼고 가슴을 펴며 10초 유지"},
]
