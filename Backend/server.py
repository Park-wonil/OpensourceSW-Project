from flask import Flask, jsonify, render_template, Response, request, session
from Vision.vision import start_camera, stop_camera, get_focus_data, generate_frames, set_current_subject
from Backend.database import (
    get_score, get_stats, reset_data, get_all_subjects,
    set_goal, get_goals, delete_goal,
    get_weekly_stats, get_monthly_stats,
    update_my_ranking, get_ranking, add_friend,
    create_post, get_posts, get_post, add_comment, delete_post, create_user, verify_user,get_conn
)
import os
import time

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates")
)

start_time = None
current_subject = ""

# =========================
# 페이지
# =========================
app.secret_key = "focus-secret-key"
@app.route('/')
def home():
    return render_template("index.html")
# 로그인
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    nickname = data.get('nickname')

    # 🔥 필수 입력 체크
    if not username or not password or not nickname:
        return jsonify({"error": "아이디, 비밀번호, 닉네임을 입력하세요"}), 400

    # 🔥 길이 제한 (선택)
    if len(username) < 2 or len(password) < 2:
        return jsonify({"error": "너무 짧습니다"}), 400

    if create_user(username, password,nickname):
        return jsonify({"msg": "registered"})
    return jsonify({"error": "이미 존재하는 계정"}), 400
@app.route('/login', methods=['POST'])
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "입력하세요"}), 400

    # 🔥 비밀번호 검증
    if not verify_user(username, password):
        return jsonify({"error": "아이디 또는 비밀번호 틀림"}), 401

    # 🔥 nickname 가져오기
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT nickname FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()

    nickname = row[0] if row else username

    # 🔥 세션 저장 (중요)
    session['user'] = nickname

    return jsonify({
        "msg": "login success",
        "nickname": nickname
    })
@app.route('/me')
def me():
    user = session.get('user')
    return jsonify({"user": user})

# =========================
# 카메라
# =========================
@app.route('/start')
def start():
    global start_time
    if start_time is None:
        start_time = time.time()
    start_camera()
    return jsonify({"msg": "camera on"})

@app.route('/stop')
def stop():
    stop_camera()
    return jsonify({"msg": "camera off"})

@app.route('/detect')
def detect():
    return jsonify(get_focus_data())

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# =========================
# 점수 / 통계
# =========================
@app.route('/score')
def score():
    if start_time is None:
        return jsonify({"score": 0})
    return jsonify(get_score(start_time))

@app.route('/stats')
def stats():
    return jsonify(get_stats())

@app.route('/stats/weekly')
def weekly_stats():
    return jsonify({"data": get_weekly_stats()})

@app.route('/stats/monthly')
def monthly_stats():
    return jsonify(get_monthly_stats())

# =========================
# 과목
# =========================
@app.route('/subject', methods=['POST'])
def set_subject():
    global current_subject
    data = request.get_json(force=True)
    current_subject = data.get('subject', '')
    set_current_subject(current_subject)
    return jsonify({"subject": current_subject})

@app.route('/subjects')
def get_subjects():
    return jsonify({"subjects": get_all_subjects()})

# =========================
# 목표
# =========================
@app.route('/goals', methods=['GET'])
def goals():
    return jsonify({"goals": get_goals()})

@app.route('/goals', methods=['POST'])
def add_goal():
    data = request.get_json(force=True)
    if set_goal(data.get('subject'), data.get('target_minutes')):
        return jsonify({"msg": "goal set"})
    return jsonify({"error": "failed"}), 500

@app.route('/goals/<subject>', methods=['DELETE'])
def remove_goal(subject):
    if delete_goal(subject):
        return jsonify({"msg": "deleted"})
    return jsonify({"error": "failed"}), 500

# =========================
# 랭킹
# =========================
@app.route('/ranking')
def ranking():
    return jsonify({"ranking": get_ranking()})

@app.route('/ranking/update', methods=['POST'])
def update_ranking():
    data = request.get_json(force=True)
    if update_my_ranking(data.get('username'), data.get('minutes')):
        return jsonify({"msg": "updated"})
    return jsonify({"error": "failed"}), 500

@app.route('/friends/add', methods=['POST'])
def add_new_friend():
    data = request.get_json(force=True)
    if add_friend(data.get('username')):
        return jsonify({"msg": "friend added"})
    return jsonify({"error": "failed"}), 500

# =========================
# 커뮤니티
# =========================
@app.route('/community/posts', methods=['GET'])
def community_posts():
    category = request.args.get('category')
    return jsonify({"posts": get_posts(category)})

@app.route('/community/posts', methods=['POST'])
def community_create_post():
    data = request.get_json(force=True)

    post_id = create_post(
        data.get('category'),
        data.get('author'),
        data.get('title'),
        data.get('content')
    )

    if post_id:
        return jsonify({"msg": "created", "id": post_id})
    return jsonify({"error": "failed"}), 500

@app.route('/community/posts/<int:post_id>')
def community_get_post(post_id):
    post = get_post(post_id)
    if post:
        return jsonify(post)
    return jsonify({"error": "not found"}), 404

@app.route('/community/posts/<int:post_id>/comments', methods=['POST'])
def community_add_comment(post_id):
    data = request.get_json(force=True)

    if add_comment(post_id, data.get('author'), data.get('content')):
        return jsonify({"msg": "comment added"})
    return jsonify({"error": "failed"}), 500

@app.route('/community/posts/<int:post_id>', methods=['DELETE'])
def community_delete_post(post_id):
    if delete_post(post_id):
        return jsonify({"msg": "deleted"})
    return jsonify({"error": "failed"}), 500

# =========================
# 데이터 초기화
# =========================
@app.route('/reset', methods=['POST'])
def reset():
    global start_time
    start_time = None
    reset_data()
    return jsonify({"msg": "reset"})

# =========================
# 🔥 중요: 반드시 맨 아래
# =========================
if __name__ == "__main__":
    app.run(port=5001, debug=True, use_reloader=False)