# Focus AI — AI 기반 스마트 학습 관리 시스템

> 컴퓨터 비전으로 집중도를 측정하고, AI 튜터·스터디룸·커뮤니티까지 하나로 연결한 통합 학습 플랫폼

---

## 프로젝트 소개

**Focus AI**는 웹캠으로 사용자의 얼굴·눈 상태·자세(거북목)를 실시간 분석하여 집중 여부를 판단하고, 타이머를 자동 제어하는 **AI 집중도 분석 스터디 타이머**입니다.

단순한 타이머를 넘어, AI 튜터 채팅·실시간 스터디룸·커뮤니티·랭킹·아바타 커스터마이징까지 갖춘 **통합형 스마트 학습 관리 시스템**입니다.

---

## 주요 기능

### 집중도 분석 (AI 비전)
- 웹캠 기반 얼굴 인식 — 자리 이탈 감지 시 타이머 자동 정지
- 눈 감김 감지 — 졸음 상태 판단 및 경고
- 거북목(목 기울기) 분석 — 나쁜 자세 감지 및 스트레칭 가이드 제공
- MediaPipe 기반 포즈/얼굴 랜드마크 처리

### 학습 관리
- 과목별 집중 시간 자동 기록 및 일간/주간/월간 통계
- 과목별 목표 설정 및 달성률 추적
- 학습 점수 자동 산출

### AI 튜터 (깜찍이)
- Groq (Llama 3.1) 서버 사이드 AI — API 키를 프론트에 노출하지 않음
- 현재 공부 중인 과목 컨텍스트 자동 반영
- 대화 히스토리 유지 (최근 10턴)

### 실시간 스터디룸
- Socket.IO 기반 실시간 채팅
- WebRTC 화상 통화 (같은 Wi-Fi LAN 환경)
- 방 생성·입장·초대 시스템

### 커뮤니티
- 게시글 작성/조회/삭제 (익명·닉네임 선택)
- 댓글 기능

### 아바타 & 레벨 시스템
- 캐릭터(고양이·비숑·공부메이트) 선택 및 색상 커스터마이징
- 모자·옷·악세서리·표정 꾸미기
- 누적 공부 시간 기반 레벨 시스템 (Lv.1~10) — 특정 레벨 달성 시 아이템 해금
- 내비게이션 바 레벨 뱃지 표시

### 기타
- 회원가입·로그인 (세션 기반 인증)
- 닉네임 기반 글로벌 랭킹
- 친구 추가 기능
- 다크모드 / 라이트모드 전환
- 반응형 UI

---

## 프로젝트 구조

```
OpensourceSW-Project/
├── Backend/
│   ├── __init__.py
│   ├── server.py            # Flask 앱, REST API, Socket.IO 이벤트 핸들러
│   ├── database.py          # SQLite DB 연동 (유저·통계·목표·랭킹·커뮤니티)
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   └── templates/
│       └── index.html       # SPA 단일 페이지 (모든 탭 포함)
│
├── Vision/
│   ├── __init__.py
│   ├── vision.py            # 웹캠 스트리밍, 얼굴·눈 감김 감지, 집중도 판단
│   ├── pose_detection.py    # MediaPipe 포즈 기반 자세 분석
│   └── neck.py              # 거북목 감지 및 스트레칭 가이드 데이터
│
├── Data/                    # 학습 데이터 저장 디렉토리
├── Docs/
│   └── naming_rules.md      # 팀 코딩 컨벤션
│
├── focus.db                 # SQLite 데이터베이스
├── requirements.txt
├── .env                     # API 키 설정 (git 제외)
└── README.md
```

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| Backend | Python 3.11, Flask, Flask-SocketIO |
| AI 비전 | MediaPipe|
| AI 튜터 | Groq API (Llama 3.1) |
| Frontend | Vanilla JS, SVG 아바타 렌더링 |
| DB | SQLite |
| 실시간 통신 | Socket.IO, WebRTC |

---

## 실행 방법

### 1. 저장소 클론

```bash
git clone https://github.com/Park-wonil/OpensourceSW-Project.git
cd OpensourceSW-Project
```

### 2. Python 가상환경 생성 (Python 3.11 권장)

```bash
python3.11 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. 의존성 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install openai              # AI 튜터 기능 사용 시
```

### 4. AI 튜터 API 키 설정 (선택)

프로젝트 루트에 `.env` 파일 생성:

```env
# Groq (무료) — console.groq.com → API Keys → Create API Key
GROQ_API_KEY=gsk_...
```

> 키가 없으면 AI 튜터 기능만 비활성화되고 나머지 기능은 정상 동작합니다.

### 5. 서버 실행

```bash
python3 -m Backend.server
```

브라우저에서 `http://localhost:5000` 접속

---

## 팀 개발 브랜치 전략

```bash
# 작업 시작 전
git checkout dev
git pull origin dev
git checkout feature/본인브랜치
git merge dev

# 작업 후
git add .
git commit -m "작업 내용"
git push origin feature/본인브랜치

# PR: compare → feature/본인브랜치 / base → dev
```
