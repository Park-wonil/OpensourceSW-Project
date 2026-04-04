from flask import Flask, Response, jsonify, render_template
import time

# vision.py
from Vision.vision import start_camera, stop_camera, generate_frames, get_focus_data

# database.py
from Backend.database import get_score

app = Flask(__name__)

# 세션 시작 시간
start_time = None


# 메인 페이지
@app.route("/")
def index():
    return render_template("index.html")


# 카메라 시작
@app.route("/start")
def start():
    global start_time
    start_time = time.time()  #  시작 시점 기록
    start_camera()
    return jsonify({"status": "started"})


# 카메라 종료
@app.route("/stop")
def stop():
    stop_camera()
    return jsonify({"status": "stopped"})


# 현재 상태 데이터
@app.route("/detect")
def data():
    return jsonify(get_focus_data())


# 영상 스트리밍
@app.route("/video")
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# 점수 반환
@app.route("/score")
def score():
    return jsonify(get_score(start_time))


# 서버 실행
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)