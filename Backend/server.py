from flask import Flask, jsonify, render_template, Response, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from Vision.vision import start_camera, stop_camera, get_focus_data, generate_frames, set_current_subject, set_current_username
from Vision.neck import STRETCHING_GUIDE
from Backend.database import (
    get_score, get_stats, reset_data, get_all_subjects,
    set_goal, get_goals, delete_goal,
    get_weekly_stats, get_monthly_stats,
    update_my_ranking, get_ranking, add_friend,
    create_post, get_posts, get_post, add_comment, delete_post, create_user, verify_user, get_conn,
    save_subject
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

# Socket.IO 초기화 (같은 와이파이 LAN 환경용)
socketio = SocketIO(app, cors_allowed_origins="*")

start_time = None
current_subject = ""

# 스터디룸 접속 유저 관리 {sid: nickname}
study_room_users = {}

# =========================
# 페이지
# =========================
app.secret_key = "focus-secret-key"

def get_current_username():
    """세션의 nickname으로 username 조회"""
    nickname = session.get('user')
    if not nickname:
        return ""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE nickname = ?", (nickname,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else ""

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
    set_current_username(username)

    return jsonify({
        "msg": "login success",
        "nickname": nickname
    })
@app.route('/me')
def me():
    user = session.get('user')
    return jsonify({"user": user})

@app.route('/logout', methods=['POST'])
def logout():
    """로그아웃 - 세션 초기화"""
    session.clear()
    return jsonify({"msg": "logged out"})

# =========================
# 카메라
# =========================
@app.route('/start')
def start():
    global start_time
    if start_time is None:
        start_time = time.time()
    set_current_username(get_current_username())
    start_camera()
    return jsonify({"msg": "camera on"})

@app.route('/stop')
def stop():
    stop_camera()
    return jsonify({"msg": "camera off"})

@app.route('/detect')
def detect():
    return jsonify(get_focus_data())

@app.route('/stretching')
def stretching():
    """거북목 스트레칭 가이드 반환"""
    return jsonify({"guides": STRETCHING_GUIDE})

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
    return jsonify(get_score(start_time, username=get_current_username()))

@app.route('/stats')
def stats():
    return jsonify(get_stats(username=get_current_username()))

@app.route('/stats/weekly')
def weekly_stats():
    return jsonify({"data": get_weekly_stats(username=get_current_username())})

@app.route('/stats/monthly')
def monthly_stats():
    return jsonify(get_monthly_stats(username=get_current_username()))

# =========================
# 과목
# =========================
@app.route('/subject', methods=['POST'])
def set_subject():
    global current_subject
    data = request.get_json(force=True)
    current_subject = data.get('subject', '')
    set_current_subject(current_subject)
    # 과목을 saved_subjects에 저장 (목표 섹션 드롭다운에 표시)
    if current_subject:
        save_subject(current_subject, username=get_current_username())
    return jsonify({"subject": current_subject})

@app.route('/subjects')
def get_subjects():
    return jsonify({"subjects": get_all_subjects(username=get_current_username())})

# =========================
# 목표
# =========================
@app.route('/goals', methods=['GET'])
def goals():
    return jsonify({"goals": get_goals(username=get_current_username())})

@app.route('/goals', methods=['POST'])
def add_goal():
    data = request.get_json(force=True)
    if set_goal(data.get('subject'), data.get('target_minutes'), username=get_current_username()):
        return jsonify({"msg": "goal set"})
    return jsonify({"error": "failed"}), 500

@app.route('/goals/<subject>', methods=['DELETE'])
def remove_goal(subject):
    if delete_goal(subject, username=get_current_username()):
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
    minutes = data.get('minutes', 0)

    # nickname은 body 또는 세션에서 가져옴
    nickname = data.get('nickname') or session.get('user')
    if not nickname:
        return jsonify({"error": "not logged in"}), 401

    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE nickname = ?", (nickname,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "user not found"}), 404

    username = row[0]
    if update_my_ranking(username, minutes, nickname=nickname):
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
    reset_data(username=get_current_username())
    return jsonify({"msg": "reset"})

# =========================
# WebRTC 시그널링 + 초대 시스템 (Socket.IO)
# 같은 와이파이 LAN 환경 전용
# =========================

STUDY_ROOM = "study_room"

# study_room_users: {sid: nickname}
# 접속하면 자동 등록, 끊으면 자동 제거

@socketio.on("connect")
def on_connect():
    """소켓 연결 시 - 아직 닉네임 없음, 로그인 후 register_user 호출 대기"""
    pass

@socketio.on("register_user")
def on_register(data):
    """로그인된 유저가 소켓 등록 - 온라인 목록에 추가"""
    nickname = data.get("nickname", "익명")
    study_room_users[request.sid] = nickname
    join_room(STUDY_ROOM)

    # 본인에게: 현재 온라인 유저 목록 전달
    online = [
        {"sid": sid, "nickname": nick}
        for sid, nick in study_room_users.items()
        if sid != request.sid
    ]
    emit("online_users", {"users": online})

    # 다른 유저들에게: 새 유저 온라인 알림
    emit("user_online", {"sid": request.sid, "nickname": nickname},
         to=STUDY_ROOM, include_self=False)
    print(f"[온라인] {nickname} 등록 (총 {len(study_room_users)}명)")

@socketio.on("disconnect")
def on_disconnect():
    """연결 끊김 - 온라인 목록에서 제거, 연결된 캠도 정리"""
    if request.sid in study_room_users:
        nickname = study_room_users.pop(request.sid)
        emit("user_offline", {"sid": request.sid}, to=STUDY_ROOM)
        print(f"[오프라인] {nickname} 연결 끊김 (총 {len(study_room_users)}명)")

# --- 초대 시스템 ---

@socketio.on("send_invite")
def on_send_invite(data):
    """A → B 초대 전송"""
    target_sid = data.get("target_sid")
    from_nickname = study_room_users.get(request.sid, "누군가")
    if target_sid not in study_room_users:
        emit("invite_failed", {"msg": "상대방이 오프라인입니다."})
        return
    # B에게 초대 알림
    emit("invite_received", {
        "from_sid": request.sid,
        "from_nickname": from_nickname
    }, to=target_sid)
    print(f"[초대] {from_nickname} → {study_room_users.get(target_sid)}")

@socketio.on("accept_invite")
def on_accept(data):
    """B가 수락 → A에게 알림, 양쪽 WebRTC 시작"""
    from_sid = data.get("from_sid")
    my_nickname = study_room_users.get(request.sid, "누군가")
    # A에게 수락 알림 (A가 offer 생성 시작)
    emit("invite_accepted", {
        "from_sid": request.sid,
        "from_nickname": my_nickname
    }, to=from_sid)
    print(f"[수락] {my_nickname} → {study_room_users.get(from_sid)}")

@socketio.on("reject_invite")
def on_reject(data):
    """B가 거절 → A에게 알림"""
    from_sid = data.get("from_sid")
    my_nickname = study_room_users.get(request.sid, "누군가")
    emit("invite_rejected", {
        "from_nickname": my_nickname
    }, to=from_sid)
    print(f"[거절] {my_nickname} → {study_room_users.get(from_sid)}")

@socketio.on("end_cam")
def on_end_cam(data):
    """캠 연결 종료 요청 → 상대에게 알림"""
    target_sid = data.get("target_sid")
    emit("cam_ended", {"from_sid": request.sid}, to=target_sid)

# --- WebRTC 시그널링 중계 ---

@socketio.on("webrtc_offer")
def on_offer(data):
    """Offer를 특정 유저에게 전달"""
    emit("webrtc_offer", {"sid": request.sid, "sdp": data["sdp"]}, to=data["target"])

@socketio.on("webrtc_answer")
def on_answer(data):
    """Answer를 특정 유저에게 전달"""
    emit("webrtc_answer", {"sid": request.sid, "sdp": data["sdp"]}, to=data["target"])

@socketio.on("webrtc_ice")
def on_ice(data):
    """ICE candidate를 특정 유저에게 전달"""
    emit("webrtc_ice", {"sid": request.sid, "candidate": data["candidate"]}, to=data["target"])

# =========================
#  중요: 반드시 맨 아래
# =========================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)