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

///
다시작업시작할 때 
1. cd OpensourceSW-Project(해당폴더로이동)
2.
git checkout dev (dev 최신화)
git pull origin dev
3.git checkout feature/본인feature브랜치
4.git merge dev (최신코드가져옴)


작업후
git add .
git commit -m "작업내용"
git push origin feature/본인


5. PR(풀리퀘스트요청)
PR후 merge 끝나면
git checkout dev
git pull origin dev


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
