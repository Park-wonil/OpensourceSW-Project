import sqlite3
import time
import os

# DB 경로 절대경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "focus.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS focus_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        state TEXT,
        absence_count INTEGER
    )
    """)
    c.execute("PRAGMA table_info(focus_log)")
    columns = [col[1] for col in c.fetchall()]
    if "ear" not in columns:
        try:
            c.execute("ALTER TABLE focus_log ADD COLUMN ear REAL")
            print("ear 컬럼 추가 완료")
        except:
            pass
    if "subject" not in columns:
        try:
            c.execute("ALTER TABLE focus_log ADD COLUMN subject TEXT DEFAULT ''")
            print("subject 컬럼 추가 완료")
        except:
            pass
    
    # 목표 테이블
    c.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT UNIQUE,
        target_minutes INTEGER,
        created_at REAL
    )
    """)
    
    # 랭킹 테이블 (사용자별)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        total_minutes INTEGER DEFAULT 0,
        last_updated REAL
    )
    """)
    
    conn.commit()
    conn.close()

init_db()

def save_data(data):
    if "state" not in data:
        return
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
        INSERT INTO focus_log (timestamp, state, absence_count, ear, subject)
        VALUES (?, ?, ?, ?, ?)
        """, (
            time.time(),
            data.get("state", "unknown"),
            data.get("absence_count", 0),
            data.get("ear", 0.0),
            data.get("subject", "")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB 저장 오류:", e)

def get_score(start_time=None):
    try:
        conn = get_conn()
        c = conn.cursor()
        if start_time:
            c.execute("""
            SELECT state, absence_count, timestamp, ear
            FROM focus_log
            WHERE timestamp >= ?
            ORDER BY id ASC
            """, (start_time,))
        else:
            c.execute("""
            SELECT state, absence_count, timestamp, ear
            FROM focus_log
            ORDER BY id ASC
            """)
        rows = c.fetchall()
        conn.close()
        
        # 데이터가 없으면 100점 반환
        if len(rows) == 0:
            return {"score": 100, "absence_count": 0, "absence_time": 0}
        
        score = 100.0
        prev_absence = rows[0][1]
        total_absence_count = 0
        total_absence_time = 0
        for row in rows:
            state, absence_count, timestamp, ear = row
            if absence_count > prev_absence:
                total_absence_count += (absence_count - prev_absence)
            prev_absence = absence_count
            if state == "absent":
                score -= 2.0
                total_absence_time += 1
            elif state == "sleepy":
                score -= 1.0
            elif state == "focused":
                score += 0.3
        
        score = max(0, score)  # 하한선만 0으로 제한
        
        return {
            "score": round(score, 1),
            "absence_count": total_absence_count,
            "absence_time": total_absence_time,
        }
    except Exception as e:
        print("점수 계산 오류:", e)
        return {"score": 0}

def get_stats():
    try:
        conn = get_conn()
        c = conn.cursor()
        today_start = time.mktime(time.localtime()[:3] + (0, 0, 0, 0, 0, -1))
        c.execute("""
        SELECT state, timestamp, subject
        FROM focus_log
        WHERE timestamp >= ?
        ORDER BY id ASC
        """, (today_start,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            return {
                "total_focus_time": "00:00:00",
                "avg_score": 0,
                "subject_stats": []
            }
        focused_seconds = sum(1 for r in rows if r[0] in ("focused", "sleepy"))
        h = focused_seconds // 3600
        m = (focused_seconds % 3600) // 60
        s = focused_seconds % 60
        total_focus_time = f"{h:02d}:{m:02d}:{s:02d}"
        score = 100.0
        for row in rows:
            state = row[0]
            if state == "absent":
                score -= 2.0
            elif state == "sleepy":
                score -= 1.0
            elif state == "focused":
                score += 0.3
        avg_score = round(max(0, min(100, score)), 1)
        subject_map = {}
        for row in rows:
            state, timestamp, subject = row
            if state in ("focused", "sleepy"):
                # 비어있거나 공백이면 건너뛰기 (미입력 제외)
                if not subject or not subject.strip():
                    continue
                label = subject.strip()
                subject_map[label] = subject_map.get(label, 0) + 1
        subject_stats = [
            {"subject": k, "seconds": v, "label": _fmt_seconds(v)}
            for k, v in subject_map.items()
        ]
        return {
            "total_focus_time": total_focus_time,
            "avg_score": avg_score,
            "subject_stats": subject_stats
        }
    except Exception as e:
        print("통계 계산 오류:", e)
        return {"total_focus_time": "00:00:00", "avg_score": 0, "subject_stats": []}

def get_all_subjects():
    """DB에 저장된 모든 과목 목록 반환 (최근 사용순)"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
        SELECT DISTINCT subject, MAX(timestamp) as last_used
        FROM focus_log
        WHERE subject IS NOT NULL AND subject != ''
        GROUP BY subject
        ORDER BY last_used DESC
        LIMIT 20
        """)
        rows = c.fetchall()
        conn.close()
        return [row[0].strip() for row in rows if row[0] and row[0].strip()]
    except Exception as e:
        print("과목 목록 조회 오류:", e)
        return []

def _fmt_seconds(s):
    h = s // 3600
    m = (s % 3600) // 60
    if h > 0:
        return f"{h}시간 {m}분"
    return f"{m}분"

def reset_data():
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM focus_log")
        conn.commit()
        conn.close()
        print("데이터 초기화 완료")
        return True
    except Exception as e:
        print("초기화 오류:", e)
        return False

# ========================================
# 목표 관련 함수
# ========================================

def set_goal(subject, target_minutes):
    """과목별 목표 시간 설정 (분 단위)"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
        INSERT OR REPLACE INTO goals (subject, target_minutes, created_at)
        VALUES (?, ?, ?)
        """, (subject, target_minutes, time.time()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("목표 설정 오류:", e)
        return False

def get_goals():
    """오늘 목표 달성률 조회"""
    try:
        conn = get_conn()
        c = conn.cursor()
        
        # 오늘 통계
        today_start = time.mktime(time.localtime()[:3] + (0, 0, 0, 0, 0, -1))
        c.execute("""
        SELECT subject, state
        FROM focus_log
        WHERE timestamp >= ? AND subject != ''
        """, (today_start,))
        rows = c.fetchall()
        
        # 과목별 실제 시간 (초)
        actual_times = {}
        for subject, state in rows:
            if state in ("focused", "sleepy"):
                subject = subject.strip()
                actual_times[subject] = actual_times.get(subject, 0) + 1
        
        # 목표와 비교
        c.execute("SELECT subject, target_minutes FROM goals")
        goals = c.fetchall()
        conn.close()
        
        result = []
        for subject, target_min in goals:
            actual_min = actual_times.get(subject, 0) // 60
            progress = min(100, int(actual_min / target_min * 100)) if target_min > 0 else 0
            result.append({
                "subject": subject,
                "target": target_min,
                "actual": actual_min,
                "progress": progress
            })
        
        return result
    except Exception as e:
        print("목표 조회 오류:", e)
        return []

def delete_goal(subject):
    """목표 삭제"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM goals WHERE subject = ?", (subject,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("목표 삭제 오류:", e)
        return False


# ========================================
# 주간/월간 통계
# ========================================

def get_weekly_stats():
    """최근 7일 통계"""
    try:
        conn = get_conn()
        c = conn.cursor()
        
        result = []
        for i in range(6, -1, -1):  # 6일 전부터 오늘까지
            day_start = time.mktime(time.localtime()[:3] + (0, 0, 0, 0, 0, -1)) - (i * 86400)
            day_end = day_start + 86400
            
            c.execute("""
            SELECT state FROM focus_log
            WHERE timestamp >= ? AND timestamp < ? AND state IN ('focused', 'sleepy')
            """, (day_start, day_end))
            
            count = len(c.fetchall())
            minutes = count // 60
            
            day_name = time.strftime("%m/%d", time.localtime(day_start))
            weekday = ["월", "화", "수", "목", "금", "토", "일"][time.localtime(day_start).tm_wday]
            
            result.append({
                "date": day_name,
                "weekday": weekday,
                "minutes": minutes,
                "hours": round(minutes / 60, 1)
            })
        
        conn.close()
        return result
    except Exception as e:
        print("주간 통계 오류:", e)
        return []

def get_monthly_stats():
    """이번 달 통계"""
    try:
        conn = get_conn()
        c = conn.cursor()
        
        # 이번 달 1일
        now = time.localtime()
        month_start = time.mktime((now.tm_year, now.tm_mon, 1, 0, 0, 0, 0, 0, -1))
        
        c.execute("""
        SELECT subject, state FROM focus_log
        WHERE timestamp >= ? AND subject != '' AND state IN ('focused', 'sleepy')
        """, (month_start,))
        
        rows = c.fetchall()
        conn.close()
        
        # 과목별 시간 집계
        subject_times = {}
        for subject, state in rows:
            subject_times[subject] = subject_times.get(subject, 0) + 1
        
        result = [
            {
                "subject": k,
                "minutes": v // 60,
                "hours": round(v / 3600, 1)
            }
            for k, v in sorted(subject_times.items(), key=lambda x: x[1], reverse=True)
        ]
        
        total_minutes = sum(v // 60 for v in subject_times.values())
        
        return {
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 1),
            "subjects": result
        }
    except Exception as e:
        print("월간 통계 오류:", e)
        return {"total_minutes": 0, "total_hours": 0, "subjects": []}


# ========================================
# 랭킹 시스템
# ========================================

def update_my_ranking(username, minutes):
    """내 랭킹 업데이트"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
        INSERT INTO users (username, total_minutes, last_updated)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            total_minutes = total_minutes + ?,
            last_updated = ?
        """, (username, minutes, time.time(), minutes, time.time()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("랭킹 업데이트 오류:", e)
        return False

def get_ranking():
    """전체 랭킹 조회"""
    try:
        conn = get_conn()
        c = conn.cursor()

        c.execute("""
        SELECT username, nickname, total_minutes
        FROM users
        ORDER BY total_minutes DESC
        LIMIT 10
        """)

        rows = c.fetchall()
        conn.close()
        
        return [
            {
                "rank": i + 1,
                "username": nickname if nickname else username,
                "minutes": minutes,
                "hours": round(minutes / 60, 1)
            }
            for i, (username, nickname, minutes) in enumerate(rows)
        ]

    except Exception as e:
        print("랭킹 조회 오류:", e)
        return []

def add_friend(username):
    """친구 추가 (더미 데이터)"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
        INSERT OR IGNORE INTO users (username, total_minutes, last_updated)
        VALUES (?, 0, ?)
        """, (username, time.time()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("친구 추가 오류:", e)
        return False


# ========================================
# 커뮤니티 게시판
# ========================================

def init_community():
    """커뮤니티 테이블 생성"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        author TEXT,
        title TEXT,
        content TEXT,
        created_at REAL,
        views INTEGER DEFAULT 0
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        author TEXT,
        content TEXT,
        created_at REAL
    )
    """)
    conn.commit()
    conn.close()

init_community()


def create_post(category, author, title, content):
    """게시글 작성"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
        INSERT INTO posts (category, author, title, content, created_at, views)
        VALUES (?, ?, ?, ?, ?, 0)
        """, (category, author, title, content, time.time()))
        post_id = c.lastrowid
        conn.commit()
        conn.close()
        return post_id
    except Exception as e:
        print("게시글 작성 오류:", e)
        return None


def get_posts(category=None, limit=50):
    """게시글 목록"""
    try:
        conn = get_conn()
        c = conn.cursor()
        if category:
            c.execute("""
            SELECT id, category, author, title, created_at, views
            FROM posts WHERE category = ?
            ORDER BY created_at DESC LIMIT ?
            """, (category, limit))
        else:
            c.execute("""
            SELECT id, category, author, title, created_at, views
            FROM posts ORDER BY created_at DESC LIMIT ?
            """, (limit,))
        rows = c.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "category": row[1],
                "author": row[2],
                "title": row[3],
                "created_at": time.strftime("%m/%d %H:%M", time.localtime(row[4])),
                "views": row[5]
            })
        return result
    except Exception as e:
        print("게시글 조회 오류:", e)
        return []


def get_post(post_id):
    """게시글 상세"""
    try:
        conn = get_conn()
        c = conn.cursor()
        
        # 조회수 증가
        c.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
        
        c.execute("""
        SELECT id, category, author, title, content, created_at, views
        FROM posts WHERE id = ?
        """, (post_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # 댓글 조회
        c.execute("""
        SELECT id, author, content, created_at
        FROM comments WHERE post_id = ? ORDER BY created_at ASC
        """, (post_id,))
        comments = c.fetchall()
        
        conn.commit()
        conn.close()
        
        return {
            "id": row[0],
            "category": row[1],
            "author": row[2],
            "title": row[3],
            "content": row[4],
            "created_at": time.strftime("%Y-%m-%d %H:%M", time.localtime(row[5])),
            "views": row[6],
            "comments": [
                {
                    "id": c[0],
                    "author": c[1],
                    "content": c[2],
                    "created_at": time.strftime("%m/%d %H:%M", time.localtime(c[3]))
                }
                for c in comments
            ]
        }
    except Exception as e:
        print("게시글 상세 오류:", e)
        return None


def add_comment(post_id, author, content):
    """댓글 작성"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
        INSERT INTO comments (post_id, author, content, created_at)
        VALUES (?, ?, ?, ?)
        """, (post_id, author, content, time.time()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("댓글 작성 오류:", e)
        return False


def delete_post(post_id):
    """게시글 삭제"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
        c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("게시글 삭제 오류:", e)
        return False
def create_user(username, password, nickname):
    conn = get_conn()
    c = conn.cursor()

    try:
        # 🔥 users 테이블에 nickname까지 저장
        c.execute("""
        INSERT INTO users (username, nickname, total_minutes, last_updated)
        VALUES (?, ?, 0, ?)
        """, (username, nickname, time.time()))

        # auth 테이블 생성
        c.execute("""
        CREATE TABLE IF NOT EXISTS auth (
            username TEXT PRIMARY KEY,
            password TEXT
        )
        """)

        # 중복 체크
        c.execute("SELECT username FROM auth WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return False

        # 비밀번호 저장
        c.execute("""
        INSERT INTO auth (username, password)
        VALUES (?, ?)
        """, (username, password))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print("회원가입 오류:", e)
        conn.close()
        return False
    
def verify_user(username, password):
    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute("""
        SELECT password FROM auth WHERE username = ?
        """, (username,))
        row = c.fetchone()
        conn.close()

        if row and row[0] == password:
            return True
        return False
    except:
        conn.close()
        return False