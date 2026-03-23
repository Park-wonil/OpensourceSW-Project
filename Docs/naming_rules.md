🔹 변수
cap : 카메라 객체 (영상 입력)
face_cascade : 얼굴 인식 모델

🔹 함수
get_frame()
카메라에서 프레임 가져옴 (실패 시 None)

detect_faces(frame)
프레임에서 얼굴 좌표 반환

is_face_detected(frame)
얼굴 존재 여부 반환 (True / False)

release_camera()
카메라 종료

run_face_detection()
실시간 얼굴 탐지 실행 (ESC 누르면 종료)