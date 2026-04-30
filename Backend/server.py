from flask import Flask, jsonify, render_template, Response, request
from Vision.vision import start_camera, stop_camera, get_focus_data, generate_frames, set_current_subject
from Backend.database import get_score, get_stats, reset_data, get_all_subjects
import os
import time

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates")
)

# 세션 시작 시간 (카메라 OFF 해도 유지됨)
start_time = None
current_subject = ""  # 현재 공부 중인 과목


# =========================
# 페이지
# =========================
@app.route('/')
def home():
    return render_template("index.html")


# =========================
# 카메라 제어
# =========================
@app.route('/start')
def start():
    global start_time
    # start_time이 None일 때만 새로 기록 (OFF 후 ON 해도 유지)
    if start_time is None:
        start_time = time.time()
    start_camera()
    return jsonify({"msg": "camera on"})


@app.route('/stop')
def stop():
    # start_time은 유지 (초기화 안 함)
    stop_camera()
    return jsonify({"msg": "camera off"})


# =========================
# 상태 데이터
# =========================
@app.route('/detect')
def detect():
    return jsonify(get_focus_data())


# =========================
# 영상 스트리밍
# =========================
@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# =========================
# 점수
# =========================
@app.route('/score')
def score():
    if start_time is None:
        return jsonify({"score": 0})
    return jsonify(get_score(start_time))


# =========================
# 상세 통계
# =========================
@app.route('/stats')
def stats():
    return jsonify(get_stats())


# =========================
# 과목 설정
# =========================
@app.route('/subject', methods=['POST'])
def set_subject():
    global current_subject
    data = request.get_json()
    current_subject = data.get('subject', '')
    set_current_subject(current_subject)  # Vision 모듈에 전달
    return jsonify({"msg": "subject updated", "subject": current_subject})


@app.route('/subjects', methods=['GET'])
def get_subjects():
    """저장된 과목 목록 반환"""
    subjects = get_all_subjects()
    return jsonify({"subjects": subjects})


# =========================
# 데이터 초기화
# =========================
@app.route('/reset', methods=['POST'])
def reset():
    global start_time
    start_time = None  # 세션 시작 시간 리셋
    reset_data()  # DB 전체 삭제
    return jsonify({"msg": "data reset"})


# =========================
# 서버 실행
# =========================
if __name__ == "__main__":
    app.run(port=5001, debug=True, use_reloader=False)