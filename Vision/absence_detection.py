import time
import cv2
import mediapipe as mp
import numpy as np
from collections import deque

#상수
# 이탈 확정까지 얼굴이 없어야 하는 시간 (초)
ABSENCE_THRESHOLD_S = 2.0
# 복귀 확정까지 얼굴이 유지돼야 하는 시간 (초)
RETURN_CONFIRM_S    = 1.0
# 노이즈 제거용 버퍼 크기
BUFFER_SIZE         = 5

#Mediapipe 초기화
_mp_face   = mp.solutions.face_mesh
_face_mesh = _mp_face.FaceMesh(
    max_num_faces=1,
    refine_landmarks=False,  # 자리이탈은 얼굴 존재 여부만 보면 되므로 False
)

#자체 카메라 상태
_cap: cv2.VideoCapture | None = None
_is_running: bool = False

#카메라 제어 
def start_camera(index: int = 0) -> bool:
    """
    face.py의 start_camera()와 동시에 같은 카메라 인덱스를 사용하면 충돌.
    main.py에서 호출 순서를 조율.
    """
    global _cap, _is_running

    if _is_running:
        return True

    _cap = cv2.VideoCapture(index)
    if not _cap.isOpened():
        _cap = None
        return False

    _is_running = True
    return True

def stop_camera() -> bool:
    global _cap, _is_running

    _is_running = False
    time.sleep(0.1)

    if _cap is not None:
        _cap.release()
        _cap = None

    return True

def _get_frame():
    #단일 프레임을 읽어 반환. 실패 시 None
    if _cap is None or not _cap.isOpened():
        return None
    ret, frame = _cap.read()
    return frame if ret else None

def _detect_face(frame) -> bool:
    rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = _face_mesh.process(rgb)
    return bool(results.multi_face_landmarks)

#클래스
class AbsenceDetector:
    
    #얼굴 감지 결과를 바탕으로 자리이탈/복귀 상태를 관리
    def __init__(self):
        self._is_absent      = False
        self._last_seen_ts   = time.time()
        self._return_since   = None
        self._absence_start  = None

        self._buffer = deque(maxlen=BUFFER_SIZE)

        # 세션 통계
        self.absence_count   = 0
        self.total_absence_s = 0.0
        self._events         = []   # [(시작ts, 종료ts), ...]

    #외부 인터페이스
    def update(self) -> dict:
        """
        프레임을 읽고 상태를 갱신한 뒤 결과 dict를 반환
        main.py나 Flask 라우트에서 주기적으로 호출.

        반환 키
        ───────
        frame             : 현재 프레임 (ndarray) — None이면 카메라 꺼짐
        is_absent         : 이탈 중 여부 (bool)
        absence_duration_s: 현재 이탈 경과 시간 (float, 이탈 중이 아니면 0)
        timer_action      : "pause" | "resume" | "none"
        absence_count     : 총 이탈 횟수 (int)
        total_absence_s   : 누적 이탈 시간 (float)
        """
        frame = _get_frame()

        if frame is None:
            return {
                "frame":              None,
                "is_absent":          self._is_absent,
                "absence_duration_s": self.current_absence_s,
                "timer_action":       "none",
                "absence_count":      self.absence_count,
                "total_absence_s":    self.total_absence_s,
            }

        face_present = _detect_face(frame)

        # 버퍼 다수결로 단발성 노이즈 제거
        self._buffer.append(face_present)
        smoothed     = sum(self._buffer) > len(self._buffer) // 2
        timer_action = self._update_state(smoothed)

        return {
            "frame":              frame,
            "is_absent":          self._is_absent,
            "absence_duration_s": self.current_absence_s,
            "timer_action":       timer_action,
            "absence_count":      self.absence_count,
            "total_absence_s":    self.total_absence_s,
        }

    @property
    def current_absence_s(self) -> float:
        if self._is_absent and self._absence_start:
            return time.time() - self._absence_start
        return 0.0

    def get_stats(self) -> dict:
        return {
            "absence_count":   self.absence_count,
            "total_absence_s": round(self.total_absence_s, 1),
            "avg_absence_s": (
                round(self.total_absence_s / self.absence_count, 1)
                if self.absence_count else 0.0
            ),
            "events": [
                {
                    "start":      t[0],
                    "end":        t[1],
                    "duration_s": round(t[1] - t[0], 1),
                }
                for t in self._events
            ],
        }

    #내부 상태 전이 
    def _update_state(self, face_present: bool) -> str:
        now          = time.time()
        timer_action = "none"

        if face_present:
            self._last_seen_ts = now

            if self._is_absent:
                # 이탈 중 → 얼굴 보임 → 복귀 감지 시작
                if self._return_since is None:
                    self._return_since = now
                # RETURN_CONFIRM_S 동안 유지되면 복귀 확정
                elif now - self._return_since >= RETURN_CONFIRM_S:
                    self._confirm_return(now)
                    timer_action = "resume"
            else:
                self._return_since = None

        else:
            # 얼굴 없음 → 복귀 시도 취소
            self._return_since = None

            if not self._is_absent:
                elapsed = now - self._last_seen_ts
                if elapsed >= ABSENCE_THRESHOLD_S:
                    self._absence_start = self._last_seen_ts
                    self._is_absent     = True
                    timer_action        = "pause"

        return timer_action

    def _confirm_return(self, now: float):
        #복귀 확정 시 이탈 통계를 기록하고 상태를 초기화
        self._is_absent    = False
        self._return_since = None

        if self._absence_start:
            duration              = now - self._absence_start
            self.absence_count   += 1
            self.total_absence_s += duration
            self._events.append((self._absence_start, now))
            self._absence_start   = None

#디버그용 오버레이
def draw_absence_overlay(frame, result: dict):
    #프레임에 이탈 상태를 시각화합니다
    h, w = frame.shape[:2]

    border_color = (0, 0, 220) if result["is_absent"] else (0, 200, 80)
    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), border_color, 3)

    cv2.rectangle(frame, (0, h - 40), (w, h), (30, 30, 30), -1)

    total_s    = int(result["total_absence_s"])
    count_text = f"이탈 횟수: {result['absence_count']}"
    time_text  = f"누적 이탈: {total_s // 60}m {total_s % 60}s"

    cv2.putText(frame, count_text, (10, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, time_text, (w // 2 - 70, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    if result["is_absent"]:
        cur     = int(result["absence_duration_s"])
        cur_txt = f"자리비움 {cur}s..."
        cv2.putText(frame, cur_txt, (w - 170, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 255), 1)

    return frame

#단독 실행_디버그용 
if __name__ == "__main__":
    if not start_camera():
        print("camera error")
        exit(1)

    detector = AbsenceDetector()

    while True:
        result = detector.update()

        frame = result["frame"]
        if frame is None:
            print("No frame")
            break

        frame = draw_absence_overlay(frame, result)
        cv2.imshow("Absence Detection", frame)

        action = result["timer_action"]
        if action != "none":
            print(f"[timer_action] → {action}")

        if cv2.waitKey(1) & 0xFF in (27, ord("q")):
            break

    stop_camera()
    cv2.destroyAllWindows()

    stats = detector.get_stats()
    print("\n===== result =====")
    print(f"absence count : {stats['absence_count']}")
    print(f"absence time : {stats['total_absence_s']}s")
   # for i, ev in enumerate(stats["events"], 1):
   #      print(f"  [{i}] {ev['duration_s']}s")

