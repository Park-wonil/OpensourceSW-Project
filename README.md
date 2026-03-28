# OpensourceSW-Project
프로젝트 실행 방법 (Mac 기준)
1. Python 버전

본 프로젝트는 Python 3.11 환경에서 실행됩니다.

python3 --version

👉 3.11이 아니면 설치:

brew install python@3.11
2. 프로젝트 클론
git clone https://github.com/Park-wonil/OpensourceSW-Project.git
cd OpensourceSW-Project
3. 가상환경 생성 및 활성화
python3.11 -m venv venv
source venv/bin/activate

활성화 확인:

(venv)
(중요) conda 사용 중이면 비활성화
conda deactivate

(base)가 없어야 정상

4. 필수 라이브러리 설치
pip install --upgrade pip
pip install mediapipe==0.10.8
pip install opencv-python
pip install numpy
pip install flask
