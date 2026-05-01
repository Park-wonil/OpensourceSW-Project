# 오픈소스SW 프로젝트

## 프로젝트명 : Focus AI
프로젝트 소개
```bash
AI 기반 컴퓨터 비전 기술을 활용한 집중도 분석 스터디 타이머입니다.
사용자의 얼굴, 눈 상태, 그리고 자세(거북목)를 실시간으로 분석하여
학습 집중도를 정량적으로 측정하고, 이를 기반으로 타이머를 자동 제어합니다.

또한 사용자 계정 시스템을 통해 학습 데이터를 저장하고,
커뮤니티 및 랭킹 기능을 통해 학습 동기 부여를 강화하는
통합형 스마트 학습 관리 시스템입니다.

프로젝트 목표
얼굴 인식을 통해 사용자 존재 여부 판단
눈 감김 여부를 통해 졸음 상태 감지
목 기울기(거북목) 분석을 통한 자세 기반 집중도 판단
AI 기반 상태 분석을 통한 자동 타이머 제어 (시작/정지)
사용자별 학습 시간 및 집중도 데이터 기록
닉네임 기반 랭킹 시스템으로 학습 경쟁 유도
커뮤니티 기능을 통한 학습 경험 공유 및 상호 동기 부여
익명/닉네임 선택 게시글 작성 기능 제공
다크모드 및 UI 최적화를 통한 사용자 경험 향상
 추가 기능 (지금 구현된 내용 반영)
회원가입 / 로그인 시스템 (세션 기반 인증)
닉네임 기반 실시간 랭킹 시스템
커뮤니티 게시판 (익명/닉네임 선택 가능)
다크모드 UI 지원
거북목 감지 및 경고 알림 기능
집중 시간 자동 기록 및 분석
```
---
# OpensourceSW-Project
## 프로젝트 실행 방법 (macOS 기준)

이 프로젝트의 원활한 실행을 위해 아래 단계를 차례대로 따라해 주세요.

### 1. Python 환경 확인
본 프로젝트는 **Python 3.11** 환경에서 최적화되어 있습니다.
```bash
brew install python@3.11
git clone [https://github.com/Park-wonil/OpensourceSW-Project.git](https://github.com/Park-wonil/OpensourceSW-Project.git)
cd OpensourceSW-Project
```
### 2. 프로젝트 클론
```bash
git clone [https://github.com/Park-wonil/OpensourceSW-Project.git](https://github.com/Park-wonil/OpensourceSW-Project.git)
cd OpensourceSW-Project
```
### 3. 가상환경설정
```bash
conda deactivate
python3.11 -m venv venv
source venv/bin/activate
```
### 4.필수 라이브러리 설치
```bash
pip install --upgrade pip
pip install mediapipe==0.10.8 opencv-python numpy flask
pip install flask-socketio
```

### 5. 서버실행 Flask
```bash
python3 -m Backend.server
```


### 다시작업시작할 때 
```bash
cd OpensourceSW-Project(해당폴더로이동)
git checkout dev (dev 최신화)
git pull origin dev
git checkout feature/본인feature브랜치
git merge dev (최신코드가져옴)


작업후
git add .
git commit -m "작업내용"
git push origin feature/본인


5. PR(풀리퀘스트요청)
PR후 merge 끝나면
git checkout dev
git pull origin dev
```


PR시 조심할점 
compare: 본인 feature
base: dev

각 코드별 주석 필수

*****************변수 통일 ****************

함수.변수 설명
Docs 폴더의 naming_rules.md에 추가하고 계속 최신화하기
main브랜치에서 절대 작업 X
무조건 features파일에서 작업후 dev로 PR하고 최종본을 main브랜치에 올리는것임
git branch 를 터미널에 작성하면 현재 브랜치가나옴 계속확인하기
