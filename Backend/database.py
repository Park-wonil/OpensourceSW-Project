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