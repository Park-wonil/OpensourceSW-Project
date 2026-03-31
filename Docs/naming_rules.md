🔹 변수
cap : 카메라 객체 (영상 입력)
face_cascade : 얼굴 인식 모델

🔹 함수
# 카메라를 실행하고 사용 가능한 상태로 만드는 함수
def start_camera():

# 카메라를 종료하고 자원을 해제하는 함수
def stop_camera():

# 웹으로 실시간 영상 프레임을 생성하여 스트리밍하는 함수
def generate_frames():

# 현재 프레임에서 얼굴 존재 여부와 개수를 반환하는 함수
def get_focus_data():