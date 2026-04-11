# 오픈소스SW 프로젝트
프로젝트 명 : 집중도 분석 스터디 타이머
## 🧠 프로젝트 소개
AI 기반 얼굴 인식 기술을 활용한 **집중도 분석 스터디 타이머**입니다.  
사용자의 얼굴 및 눈 상태를 인식하여 공부 집중도를 측정하고,  
자리 이탈 또는 졸음 상태를 감지하면 타이머를 자동으로 제어합니다.

---

##  프로젝트 목표
- 얼굴 인식을 통해 사용자 존재 여부 판단
- 눈 감김 여부를 통해 졸음 상태 감지
- 자동으로 타이머 시작/정지
- 공부 시간 및 집중도 데이터 기록

---

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
```

### 5. 서버실행 Flask
```bash
python3 -m Backend.server
```

---
## 🛠 기술 스택
- OpenCV
- FE(html,css)
- Flask (Backend)
- Git & GitHub (협업)

---
