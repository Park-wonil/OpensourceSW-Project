🔹 변수
cap : 카메라 객체 (영상 입력)
face_cascade : 얼굴 인식 모델

🔹 함수
# 웹으로 실시간 영상 프레임을 생성하여 스트리밍하는 함수
def generate_frames():

# 현재 프레임에서 얼굴 존재 여부와 개수를 반환하는 함수
def get_focus_data():

Front 

1. UI 및 섹션 제어

showSection(): 상단 탭 클릭 시 해당 섹션으로 부드러운 스크롤 이동 및 버튼 활성화 상태 표시.

2. 카메라 및 모니터링

startCamera(): 백엔드(/start) 호출 → 카메라 켜기 → 1초마다 데이터를 요청하는 루프(checkAll) 가동.

stopCamera(): 백엔드(/stop) 호출 → 카메라 끄기 → 데이터 요청 루프 중단.

3. 데이터 분석 및 점수 (핵심 로직)

checkAll(): 백엔드(/detect)에서 실시간 상태(얼굴 인식, EAR 등)를 가져와 다음을 수행:

점수 계산: 자리비움 시 -2.0, 졸음 감지 시 -1.0, 집중 시 +0.3.

UI 업데이트: 분석 데이터 출력 및 상태 뱃지(집중/졸음/이탈) 전환.

updateScoreUI(): 점수에 따라 게이지 바의 길이를 조절하고 색상(초록/주황/빨강) 변경.

4. 타이머 (뽀모도로)

toggleTimer(): 타이머 시작/일시정지 전환 및 아이콘 변경.

resetTimer(): 타이머 25분 초기화.

updateTimerDisplay(): 초 단위 숫자를 분:초 형식으로 변환해 화면에 표시.


CV
-absence_detection
is_absent :	이탈 중 여부 (bool)
absence_duration_s : 현재 이탈 경과 시간 (float)
absence_count : 세션 총 이탈 횟수
total_absence_s : 세션 총 이탈 시간 (초)
get_stats() : 세션 종료 후 호출. 이탈 통계 dict 반환
def _detect_face(frame) : 프레임에서 얼굴 존재 여부를 반환하는 함수 (bool)