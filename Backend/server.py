from flask import Flask, jsonify, render_template, Response
from Vision.vision import start_camera, stop_camera, get_focus_data, generate_frames
from Backend.database import get_score
import os
import time

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates")
)

# 세션 시작 시간
start_time = None


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
    start_time = time.time()  # 세션 시작 시점 기록
    start_camera()
    return jsonify({"msg": "camera on"})


@app.route('/stop')
def stop():
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
        return jsonify({"score": 0})  # 카메라가 켜지지 않았을 때 점수 0
    return jsonify(get_score(start_time))


# =========================
# 서버 실행
# =========================
if __name__ == "__main__":
    app.run(port=5001, debug=True, use_reloader=False)