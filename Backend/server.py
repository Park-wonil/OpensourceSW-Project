from flask import Flask, jsonify, render_template, Response
<<<<<<< HEAD
from Vision.face import start_camera, stop_camera, get_focus_data, generate_frames

app = Flask(__name__)

=======
from Vision.vision import start_camera, stop_camera, get_focus_data, generate_frames
from Backend.database import get_score
import os

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates")
)

# =========================
# 페이지
# =========================
>>>>>>> dev
@app.route('/')
def home():
    return render_template("index.html")

<<<<<<< HEAD
=======

# =========================
# 카메라 제어
# =========================
>>>>>>> dev
@app.route('/start')
def start():
    start_camera()
    return jsonify({"msg": "camera on"})

<<<<<<< HEAD
=======

>>>>>>> dev
@app.route('/stop')
def stop():
    stop_camera()
    return jsonify({"msg": "camera off"})

<<<<<<< HEAD
@app.route('/detect')
def detect():
    result = get_focus_data()
    return jsonify(result)

=======

# =========================
# 상태 데이터
# =========================
@app.route('/detect')
def detect():
    return jsonify(get_focus_data())


# =========================
# 영상 스트리밍
# =========================
>>>>>>> dev
@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

<<<<<<< HEAD
if __name__ == "__main__":
    app.run(port=5001, debug=True, threaded=True)
=======

# =========================
# 점수
# =========================
@app.route('/score')
def score():
    return jsonify(get_score())


# =========================
# 서버 실행
# =========================
if __name__ == "__main__":
    app.run(port=5001, debug=True)
>>>>>>> dev
