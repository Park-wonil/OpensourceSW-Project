from flask import Flask, jsonify, render_template, Response, request
from Vision.vision import start_camera, stop_camera, get_focus_data, generate_frames, set_current_subject
from Backend.database import (
    get_score, get_stats, reset_data, get_all_subjects,
    set_goal, get_goals, delete_goal,
    get_weekly_stats, get_monthly_stats,
    update_my_ranking, get_ranking, add_friend,
    create_post, get_posts, get_post, add_comment, delete_post
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

# =========================
# 목표 설정
# =========================
@app.route('/goals', methods=['GET'])
def goals():
    """목표 조회"""
    return jsonify({"goals": get_goals()})


@app.route('/goals', methods=['POST'])
def add_goal():
    """목표 추가"""
    data = request.get_json()
    subject = data.get('subject')
    target = data.get('target_minutes')
    if set_goal(subject, target):
        return jsonify({"msg": "goal set", "subject": subject, "target": target})
    return jsonify({"error": "failed"}), 500


@app.route('/goals/<subject>', methods=['DELETE'])
def remove_goal(subject):
    """목표 삭제"""
    if delete_goal(subject):
        return jsonify({"msg": "goal deleted"})
    return jsonify({"error": "failed"}), 500


# =========================
# 주간/월간 통계
# =========================
@app.route('/stats/weekly', methods=['GET'])
def weekly_stats():
    return jsonify({"data": get_weekly_stats()})


@app.route('/stats/monthly', methods=['GET'])
def monthly_stats():
    return jsonify(get_monthly_stats())


# =========================
# 랭킹
# =========================
@app.route('/ranking', methods=['GET'])
def ranking():
    return jsonify({"ranking": get_ranking()})


@app.route('/ranking/update', methods=['POST'])
def update_ranking():
    """내 랭킹 업데이트"""
    data = request.get_json()
    username = data.get('username')
    minutes = data.get('minutes')
    if update_my_ranking(username, minutes):
        return jsonify({"msg": "ranking updated"})
    return jsonify({"error": "failed"}), 500


@app.route('/friends/add', methods=['POST'])
def add_new_friend():
    """친구 추가"""
    data = request.get_json()
    username = data.get('username')
    if add_friend(username):
        return jsonify({"msg": "friend added", "username": username})
    return jsonify({"error": "failed"}), 500


# =========================
# 커뮤니티
# =========================
from Backend.database import create_post, get_posts, get_post, add_comment, delete_post

@app.route('/community/posts', methods=['GET'])
def community_posts():
    """게시글 목록"""
    category = request.args.get('category')
    posts = get_posts(category)
    return jsonify({"posts": posts})



@app.route('/community/posts', methods=['POST'])
def community_create_post():
    """게시글 작성"""
    data = request.get_json()
    post_id = create_post(
        data.get('category'),
        data.get('author'),
        data.get('title'),
        data.get('content')
    )
    if post_id:
        return jsonify({"msg": "post created", "id": post_id})
    return jsonify({"error": "failed"}), 500


@app.route('/community/posts/<int:post_id>', methods=['GET'])
def community_get_post(post_id):
    """게시글 상세"""
    post = get_post(post_id)
    if post:
        return jsonify(post)
    return jsonify({"error": "not found"}), 404


@app.route('/community/posts/<int:post_id>/comments', methods=['POST'])
def community_add_comment(post_id):
    """댓글 작성"""
    data = request.get_json()
    if add_comment(post_id, data.get('author'), data.get('content')):
        return jsonify({"msg": "comment added"})
    return jsonify({"error": "failed"}), 500


@app.route('/community/posts/<int:post_id>', methods=['DELETE'])
def community_delete_post(post_id):
    """게시글 삭제"""
    if delete_post(post_id):
        return jsonify({"msg": "post deleted"})
    return jsonify({"error": "failed"}), 500

# 디버그용 테스트 페이지
@app.route('/test')
def test_page():
    return render_template('test.html')