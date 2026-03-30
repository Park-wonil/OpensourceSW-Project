import time
import cv2
from collections import deque
from face import get_frame, detect_faces, release_camera

# 이탈 확정까지 얼굴이 없어야 하는 시간 (초)
ABSENCE_THRESHOLD_S = 2.0
# 복귀 확정까지 얼굴이 유지돼야 하는 시간 (초)
RETURN_CONFIRM_S = 1.0
# 노이즈 제거용 버퍼 크기 (최근 N프레임 다수결)
BUFFER_SIZE = 5


class AbsenceDetector:

    def __init__(self):
        # 현재 이탈 중인지 여부
        self._is_absent = False
        # 마지막으로 얼굴이 감지된 시각
        self._last_seen_ts = time.time()
        # 복귀 감지가 시작된 시각
        self._return_since = None
        # 현재 이탈이 시작된 시각
        self._absence_start = None

        # 최근 N프레임 감지 결과 저장 (카메라가 잠깐 놓쳐도 오탐 방지)
        self._buffer = deque(maxlen=BUFFER_SIZE)

        # 세션 통계
        self.absence_count = 0       # 총 이탈 횟수
        self.total_absence_s = 0.0   # 총 이탈 시간 (초)
        self._events = []            # 이탈 이력 [(시작ts, 종료ts), ...]

    def update_from_camera(self) -> dict:
        frame = get_frame()
        if frame is None:
            return {"frame": None, "is_absent": self._is_absent,
                    "absence_duration_s": self.current_absence_s,
                    "timer_action": "none",
                    "absence_count": self.absence_count,
                    "total_absence_s": self.total_absence_s}

        faces = detect_faces(frame)
        face_present = len(faces) > 0

        # 버퍼에 이번 프레임 감지 결과 추가
        self._buffer.append(face_present)
        # 버퍼 다수결로 노이즈 제거
        smoothed = sum(self._buffer) > len(self._buffer) // 2
        # 상태 전이 실행
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
        # 이탈 중일 때만 경과 시간 계산, 아니면 0
        if self._is_absent and self._absence_start:
            return time.time() - self._absence_start
        return 0.0

    def get_stats(self) -> dict:
        # 세션 종료 후 main.py나 백엔드로 넘길 통계
        return {
            "absence_count":   self.absence_count,
            "total_absence_s": round(self.total_absence_s, 1),
            "avg_absence_s":   round(self.total_absence_s / self.absence_count, 1)
                               if self.absence_count else 0.0,
            "events": [
                {"start": t[0], "end": t[1], "duration_s": round(t[1] - t[0], 1)}
                for t in self._events
            ],
        }

    def _update_state(self, face_present: bool) -> str:
        now = time.time()
        timer_action = "none"

        if face_present:
            self._last_seen_ts = now

            if self._is_absent:
                # 이탈 중 → 얼굴 다시 보임 → 복귀 감지 시작
                if self._return_since is None:
                    self._return_since = now
                # RETURN_CONFIRM_S 동안 얼굴 유지되면 복귀 확정
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
                # ABSENCE_THRESHOLD_S 이상 얼굴 없으면 이탈 확정
                if elapsed >= ABSENCE_THRESHOLD_S:
                    self._absence_start = self._last_seen_ts
                    self._is_absent = True
                    timer_action = "pause"

        return timer_action

    def _confirm_return(self, now: float):
        # 복귀 확정 시 통계에 이번 이탈 기록 추가
        self._is_absent = False
        self._return_since = None
        if self._absence_start:
            duration = now - self._absence_start
            self.absence_count += 1
            self.total_absence_s += duration
            self._events.append((self._absence_start, now))
            self._absence_start = None


def draw_info(frame, result: dict):
    h, w = frame.shape[:2]

    # 이탈 중이면 빨간 테두리, 아니면 초록 테두리
    border_color = (0, 0, 220) if result["is_absent"] else (0, 200, 80)
    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), border_color, 3)

    # 하단 배경 바
    cv2.rectangle(frame, (0, h - 40), (w, h), (30, 30, 30), -1)

    # 이탈 횟수
    count_text = f"absence_count: {result['absence_count']}"
    cv2.putText(frame, count_text, (10, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # 총 이탈 시간 (분:초 형식)
    total_s = int(result["total_absence_s"])
    time_text = f"absence_time: {total_s // 60}m {total_s % 60}s"
    cv2.putText(frame, time_text, (w // 2 - 60, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # 이탈 중이면 현재 이탈 시간도 표시
    if result["is_absent"]:
        cur = int(result["absence_duration_s"])
        cur_text = f"자리비움 {cur}s..."
        cv2.putText(frame, cur_text, (w - 160, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 255), 1)

    return frame


if __name__ == "__main__":
    detector = AbsenceDetector()

    while True:
        result = detector.update_from_camera()

        frame = result["frame"]
        if frame is None:
            break

        # 카메라 화면에 이탈 정보 표시
        frame = draw_info(frame, result)
        cv2.imshow("Absence Detection", frame)

        if cv2.waitKey(1) & 0xFF in (27, ord("q")):
            break

    release_camera()
    cv2.destroyAllWindows()

    # 세션 결과 저장 및 터미널 출력
    session_result = detector.get_stats()
    print("\n===== result =====")
    print(f"absence_count : {session_result['absence_count']}")
    print(f"absence_time : {session_result['total_absence_s']}s")
    