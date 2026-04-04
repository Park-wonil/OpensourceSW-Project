import sqlite3
import time

# DB 연결
def get_conn():
    return sqlite3.connect("focus.db")


# DB 초기화
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

    # ear 컬럼 확인 후 없으면 추가
    c.execute("PRAGMA table_info(focus_log)")
    columns = [col[1] for col in c.fetchall()]

    if "ear" not in columns:
        try:
            c.execute("ALTER TABLE focus_log ADD COLUMN ear REAL")
            print("ear 컬럼 추가 완료")
        except:
            pass

    conn.commit()
    conn.close()


init_db()


# 데이터 저장
def save_data(data):
    if "state" not in data:
        return

    try:
        conn = get_conn()
        c = conn.cursor()

        c.execute("""
        INSERT INTO focus_log (timestamp, state, absence_count, ear)
        VALUES (?, ?, ?, ?)
        """, (
            time.time(),
            data.get("state", "unknown"),
            data.get("absence_count", 0),
            data.get("ear", 0.0)
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        print("DB 저장 오류:", e)


# 점수 계산 함수
def get_score(start_time=None):
    try:
        conn = get_conn()
        c = conn.cursor()

        #  현재 세션 데이터만 사용
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

        # 데이터 부족하면 0점
        if len(rows) < 5:
            return {"score": 0}

        total_absence_count = 0
        total_absence_time = 0
        focus_score = 0
        ear_bonus = 0

        prev_time = rows[0][2]
        prev_absence = rows[0][1]

        for row in rows:
            state, absence_count, timestamp, ear = row

            #  시간 차이 (정방향)
            dt = timestamp - prev_time
            prev_time = timestamp

            #  자리비움 시간
            if state == "absent":
                total_absence_time += dt

            #  자리비움 횟수 증가량만 반영
            if absence_count > prev_absence:
                total_absence_count += (absence_count - prev_absence)
            prev_absence = absence_count

            #  점수 증가 (시간 기반)
            if state == "focused":
                focus_score += dt * 0.5
            elif state == "sleepy":
                focus_score += dt * 0.1

            #  눈 보너스
            if ear and ear > 0.25:
                ear_bonus += dt * 0.3

        # 점수 계산
        score = focus_score + ear_bonus

        # 패널티
        score -= total_absence_count * 5
        score -= total_absence_time * 0.2

        # 범위 제한
        score = max(0, min(100, score))

        return {
            "score": round(score, 1),
            "absence_count": total_absence_count,
            "absence_time": round(total_absence_time, 1),
            "focus_score": round(focus_score, 1),
            "ear_bonus": round(ear_bonus, 1)
        }

    except Exception as e:
        print("점수 계산 오류:", e)
        return {"score": 0}