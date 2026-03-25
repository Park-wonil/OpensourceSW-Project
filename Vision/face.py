import cv2  #영상처리임

# 카메라 
cap = cv2.VideoCapture(0)

# 얼굴 인식 모델
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def get_frame():
    # 카메라 객체(cap)로부터 현재 프레임을 읽어옵니다.
    # ret은 프레임을 성공적으로 읽었는지 여부(True/False)를 나타내는 불리언 값입니다.
    # frame은 읽어온 실제 이미지 데이터(numpy 배열)입니다.
    ret, frame = cap.read()
    
    # 프레임을 성공적으로 읽지 못했다면(예: 카메라 연결 끊김 등) None을 반환합니다.
    if not ret:
        return None
        
    # 성공적으로 읽어왔다면 해당 프레임을 반환합니다.
    return frame

def detect_faces(frame):
    # 얼굴 인식은 흑백 이미지에서 더 빠르고 정확하게 동작하므로 
    # 입력받은 컬러 프레임(BGR 형식)을 흑백(Grayscale) 이미지로 변환합니다.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 변환된 흑백 이미지에서 얼굴을 검출합니다.

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # 검출된 얼굴들의 위치 정보 리스트를 반환합니다. 
    # (얼굴이 없으면 빈 튜플이나 배열 반환)
    return faces

def is_face_detected(frame):
    # 위에서 정의한 detect_faces 함수를 호출하여 얼굴을 검출합니다.
    faces = detect_faces(frame)
    
    # 검출된 얼굴 리스트의 길이가 0보다 크면(즉, 1개 이상의 얼굴이 인식되면) True를 반환하고,
    # 그렇지 않으면 False를 반환합니다.
    return len(faces) > 0

def release_camera():
    # 사용이 끝난 카메라 장치를 해제(release)합니다.
    # 이를 통해 다른 프로그램이 카메라를 사용할 수 있게 되며, 시스템 자원을 반환합니다.
    cap.release()

#main.py에 이용될것 어떤 버튼을 누르면
def run_face_detection():  # 얼굴 탐지를 실행하는 함수 정의
    while True:  # 무한 반복으로 실시간 프레임 처리
        frame = get_frame()  # 카메라로부터 한 프레임을 가져옴
        if frame is None:  # 프레임을 가져오지 못했으면
            break  # 반복 종료

        faces = detect_faces(frame)  # 현재 프레임에서 얼굴 위치 탐지

        # 얼굴 네모 표시
        for (x, y, w, h) in faces:  # 탐지된 각 얼굴의 좌표와 크기 순회
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)  # 얼굴 위치에 사각형 표시

        cv2.imshow('Face Detection', frame)  # 결과 프레임을 화면에 출력

        if cv2.waitKey(1) == 27:  # 키 입력 대기 후 ESC(27) 키가 눌리면
            break  # 반복 종료

    release_camera()  # 카메라 자원 해제
    cv2.destroyAllWindows()  # 모든 OpenCV 창 닫기
run_face_detection()