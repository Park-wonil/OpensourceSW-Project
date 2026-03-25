from flask import Flask, jsonify, render_template, Response
from Vision.face import start_camera, stop_camera, get_focus_data, generate_frames

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/start')
def start():
    start_camera()
    return jsonify({"msg": "camera on"})

@app.route('/stop')
def stop():
    stop_camera()
    return jsonify({"msg": "camera off"})

@app.route('/detect')
def detect():
    result = get_focus_data()
    return jsonify(result)

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(port=5001, debug=True, threaded=True)