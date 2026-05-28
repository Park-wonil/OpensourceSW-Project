🔹 변수
cap : 카메라 객체 (영상 입력)
face_cascade : 얼굴 인식 모델

🔹 함수
# 웹으로 실시간 영상 프레임을 생성하여 스트리밍하는 함수
def generate_frames():

# 현재 프레임에서 얼굴 존재 여부와 개수를 반환하는 함수
def get_focus_data():


Backend (server.py / database.py)

1. 인증 및 사용자 (HTTP)

@app.route('/register') register(): 회원가입 요청 → DB에 사용자 생성.

@app.route('/login') login(): 자격증명 검증 후 세션 발급.

@app.route('/logout') logout(): 세션 종료.

@app.route('/me') me(): 현재 로그인 사용자 정보 반환.

@app.route('/me/total') me_total(): 현재 사용자 누적 학습 시간 반환.

get_current_username(): 세션에서 로그인 사용자명을 꺼내는 헬퍼.

create_user(username, password, nickname): DB에 신규 사용자 레코드 INSERT.

verify_user(username, password): 비밀번호 검증 → 성공 시 사용자 정보 반환.

2. 카메라 스트리밍 (HTTP)

@app.route('/start') start(): 카메라 캡처 시작.

@app.route('/stop') stop(): 카메라 캡처 중단.

@app.route('/video') video(): MJPEG 스트림 응답 (generate_frames 호출).

@app.route('/detect') detect(): 현재 프레임의 얼굴/EAR 등 실시간 분석값 반환.

@app.route('/stretching') stretching(): 스트레칭 가이드용 상태값 반환.

3. 점수 및 통계 (HTTP)

@app.route('/score') score(): 현재 세션 점수 반환 (get_score 호출).

@app.route('/stats') stats(): 세션/누적 통계 반환 (get_stats 호출).

@app.route('/stats/weekly') weekly_stats(): 주간 통계 (get_weekly_stats 호출).

@app.route('/stats/monthly') monthly_stats(): 월간 통계 (get_monthly_stats 호출).

@app.route('/reset') reset(): 사용자 데이터 초기화 (reset_data 호출).

4. 과목 및 목표 (HTTP)

@app.route('/subject', POST) set_subject(): 학습 과목 설정 (save_subject 호출).

@app.route('/subjects') get_subjects(): 사용자 과목 목록 조회 (get_all_subjects 호출).

@app.route('/goals', GET) goals(): 목표 시간 목록 반환 (get_goals 호출).

@app.route('/goals', POST) add_goal(): 목표 추가/수정 (set_goal 호출).

@app.route('/goals/<subject>', DELETE) remove_goal(subject): 목표 삭제.

5. 랭킹 및 친구 (HTTP)

@app.route('/ranking') ranking(): 전체 랭킹 조회 (get_ranking).

@app.route('/ranking/update', POST) update_ranking(): 본인 랭킹 점수 갱신 (update_my_ranking).

@app.route('/friends/add', POST) add_new_friend(): 친구 추가 (add_friend).

6. 커뮤니티 (HTTP)

@app.route('/community/posts', GET) community_posts(): 카테고리별 게시글 목록.

@app.route('/community/posts', POST) community_create_post(): 새 게시글 등록 (create_post).

@app.route('/community/posts/<id>') community_get_post(post_id): 단일 게시글 + 댓글 조회.

@app.route('/community/posts/<id>/comments', POST) community_add_comment(post_id): 댓글 등록.

@app.route('/community/posts/<id>', DELETE) community_delete_post(post_id): 게시글 삭제.

init_community(): 커뮤니티 테이블 초기화 (서버 시작 시 1회).

7. AI 챗봇 (HTTP)

@app.route('/ai/status') ai_status(): API 키 보유 여부/상태 반환.

@app.route('/ai/chat', POST) ai_chat(): 사용자 메시지를 외부 LLM에 전달 후 응답 반환.

8. Socket.IO — 연결/친구/초대

on_connect(): 클라이언트 연결 수립.

on_disconnect(): 연결 해제 + 온라인 상태 정리 + 룸 정리.

on_register(data) ("register_user"): 닉네임/sid 등록 및 온라인 목록 브로드캐스트.

on_send_invite(data) ("send_invite"): 친구 초대 신호 전송.

on_accept(data) / on_reject(data): 초대 수락/거절.

on_end_cam(data) ("end_cam"): 캠 종료 신호.

9. Socket.IO — WebRTC 시그널링

on_offer(data) ("webrtc_offer") / on_answer(data) ("webrtc_answer") / on_ice(data) ("webrtc_ice"):
대시보드 1:1 캠 SDP/ICE 중계.

on_room_offer / on_room_answer / on_room_ice ("room_offer/answer/ice"):
스터디룸 다인 캠 SDP/ICE 중계.

10. Socket.IO — 스터디룸

on_create_room(data) ("create_room"): 새 방 생성.

on_join_room(data) ("join_room_req"): 방 입장 (비밀방은 비밀번호 검증).

on_leave_room(data) ("leave_room_req"): 방 퇴장 + 피어 정리.

on_get_rooms() ("get_rooms"): 방 목록 요청 응답.

on_room_chat(data) ("room_chat") / on_room_emoji(data) ("room_emoji"): 룸 채팅·이모지 브로드캐스트.

handle_delete_room(data) ("delete_room"): 방 삭제.

_broadcast_room_list(): 방 목록 전체 브로드캐스트 (내부 헬퍼).

11. DB 함수 (database.py)

get_conn(): SQLite 연결 객체 반환.

init_db(): 기본 테이블 스키마 생성 (앱 시작 시 1회).

save_data(data): 세션 결과/측정값을 DB에 INSERT.

reset_data(username): 특정 사용자의 학습 데이터 초기화.

get_score(start_time, username): 시점 이후 점수 집계.

get_stats(username): 누적 통계 dict 반환.

get_weekly_stats(username) / get_monthly_stats(username): 주간/월간 집계.

save_subject(subject, username) / get_all_subjects(username): 과목 저장/조회.

set_goal(subject, target_minutes, username) / get_goals(username) / delete_goal(subject, username):
목표 시간 CRUD.

update_my_ranking(username, minutes, nickname) / get_ranking(): 랭킹 갱신/조회.

create_post / get_posts / get_post / add_comment / delete_post: 커뮤니티 CRUD.

add_friend(username): 친구 관계 추가.

_fmt_seconds(s): 초 → "HH:MM:SS" 포맷 변환 (내부 헬퍼).

12. 명명 규칙 (Backend Prefix 컨벤션)

get_*: 데이터 조회 (get_conn, get_score, get_ranking, get_posts).

save_* / insert_*: 데이터 영속 저장 (save_data, save_subject).

set_*: 단일 설정/속성 갱신 (set_subject, set_goal).

update_*: 기존 레코드 갱신 (update_my_ranking, update_ranking).

add_* / create_*: 새 엔티티 추가 (add_goal, add_friend, create_user, create_post).

delete_* / remove_*: 엔티티 삭제 (delete_goal, delete_post, remove_goal).

init_*: 초기화 1회성 작업 (init_db, init_community).

verify_*: 검증·인증 (verify_user).

on_*: Socket.IO 이벤트 핸들러 (on_connect, on_create_room, on_offer).

handle_*: 단발성 이벤트 처리 (handle_delete_room).

_xxx (언더스코어 prefix): 모듈 내부 헬퍼 (_broadcast_room_list, _fmt_seconds, _detect_face).


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

5. 상태 표시 및 분석 데이터 출력

state-badge: 현재 상태를 표시하는 요소. 초기에는 대기 중으로 표시되며, checkAll() 실행 시 집중 중, 졸음 감지, 자리 비움 상태로 변경.

face-detected: 얼굴 인식 여부를 O 또는 X로 표시하는 요소.

cam-ear: 실시간 EAR 값을 표시하는 요소.

absence-stats: 누적 자리비움 횟수와 누적 시간을 표시하는 요소.

current-absence-row: 현재 자리비움 상태일 때만 표시되는 영역.

current-absence-time: 현재 자리비움 경과 시간을 초 단위로 표시하는 요소.

6. 인증 및 사용자

login(): 로그인 폼 제출 → 백엔드(/login) 인증 요청 → 성공 시 대시보드 진입.

register(): 회원가입 폼 제출 → 백엔드(/register) 호출 → 사용자 계정 생성.

logout(): 백엔드(/logout) 호출 → 세션 종료 후 로그인 화면 복귀.

checkLogin(): 페이지 로드 시 로그인 상태 확인 → 미로그인 시 로그인 폼, 로그인 시 대시보드 표시.

7. 과목 및 목표 관리

loadSubjects(): 백엔드(/subjects)에서 사용자 과목 목록을 조회하여 드롭다운/칩 렌더링.

startWithSelected(): 선택된 과목으로 학습 세션 시작 (타이머·통계 기록 컨텍스트 설정).

loadGoals(): 사용자별 목표 시간(분) 목록을 불러와 목표 카드 UI 갱신.

updateGoalTarget(subject, encodedSubject): 특정 과목의 목표 시간을 수정 후 서버에 저장.

deleteGoal(subject): 해당 과목의 목표를 삭제.

8. 통계 및 랭킹

loadWeeklyStats(): 주간 학습 통계 데이터를 백엔드에서 조회.

renderWeeklyChart(weekData): 주간 데이터를 막대/라인 차트로 렌더링.

loadRanking(): 전체 사용자 랭킹 데이터 조회.

updateMyRanking(): 본인 순위/점수 UI 갱신.

renderSubjectChart(subjectStats): 과목별 학습 시간을 도넛/막대 차트로 시각화.

9. 커뮤니티 (게시판)

switchCategory(category, event): 카테고리 탭 전환 → 해당 카테고리 게시글만 필터링.

loadPosts(): 게시글 목록을 백엔드에서 조회 후 캐싱.

handleCommunitySearch(): 검색 입력값으로 게시글 필터링 실행.

setCommunitySort(sortType, button): 정렬 기준(최신/인기/댓글순) 전환.

getFilteredAndSortedPosts(): 현재 검색어·정렬·카테고리 조건에 맞는 게시글 배열 반환.

renderCommunityPosts(): 게시글 목록 영역을 다시 그림.

renderPopularPosts(): 상단 인기글 영역 렌더링.

submitPost(): 작성 폼의 내용을 백엔드로 전송하여 새 게시글 등록.

viewPost(postId): 게시글 상세 화면으로 전환 후 본문/댓글 로드.

submitComment(): 댓글 입력값을 서버로 전송하여 등록.

10. 스터디룸 (WebRTC 다인 캠)

createRoom(): 스터디룸 생성 요청 → 새 방 입장.

joinRoom(roomId, locked): 방 입장. 비밀방이면 비밀번호 입력 모달 호출.

leaveRoom(): 현재 방 퇴장 + WebRTC 피어 정리.

toggleRoomCam(): 룸 카메라 ON/OFF 토글 (getUserMedia 획득/해제 및 트랙 재협상).

sendRoomChat(): 룸 채팅 메시지 전송.

createRoomPeer(sid, nickname, isInitiator): 특정 멤버와의 RTCPeerConnection 생성.

updateCamGrid(): 참여자 수에 맞게 캠 그리드 레이아웃 재계산.

11. AI 챗봇 (스터디 버디)

saveApiKey(): 사용자 API 키를 로컬에 저장 후 챗봇 활성화.

clearApiKey(): 저장된 API 키 제거.

sendAiMessage(): 입력 메시지를 백엔드(/ai/chat)로 전송하여 응답 수신.

appendAiMsg(role, text): 채팅 영역에 사용자/AI 메시지 버블 추가.

clearAiChat(): AI 채팅 기록 초기화.

12. 캐릭터 꾸미기 (고양이/비숑)

loadCatConfig(): localStorage에서 캐릭터 외형 설정(JSON) 로드.

saveCatConfig(): 현재 캐릭터 외형 설정을 localStorage에 저장.

applyCatConfig(cfg): 설정 객체를 실제 SVG 캐릭터에 반영.

openCatCustomizer() / closeCatCustomizer(): 꾸미기 모달 열기/닫기.

updateCatOption(key, val): 모자/악세사리/옷 등 개별 옵션 변경.

renderPreview(state): 꾸미기 모달 내 미리보기 SVG 렌더링.

renderStudyBuddy(state): 대시보드 메인 캐릭터 영역 SVG 갱신.

13. 테마 및 일정

toggleTheme(): 라이트/다크 테마 전환.

loadTheme() / setTheme(theme): 저장된 테마 불러오기 / 적용.

renderTodayDate(): 오늘 날짜를 헤더 영역에 표시.

addDday() / deleteDday(idx) / renderDdays(): D-day 추가/삭제/렌더링.

14. 명명 규칙 (Prefix 컨벤션)

load*: 외부(서버/localStorage)에서 데이터 조회 (loadSubjects, loadGoals, loadTheme).

save*: 데이터를 영속 저장 (saveCatConfig, saveApiKey, saveDdays).

get*: 메모리상 데이터/상태 반환 (getDdays, getCommentCount).

set*: 단일 설정값 적용 (setTheme, setBgEffect, setCommunitySort).

render*: DOM/SVG를 다시 그림 (renderPreview, renderWeeklyChart, renderCommunityPosts).

update*: 상태 변경 + UI 동기화 (updateScoreUI, updateGoalTarget, updateCamGrid).

apply*: 설정 객체를 실제 화면에 반영 (applyCatConfig, applyTimerSetting).

toggle*: ON/OFF 전환 (toggleTimer, toggleRoomCam, toggleTheme).

submit*: 폼 제출 (submitPost, submitComment, submitJoinPw).

show* / close*: 모달/팝업 열기/닫기 (showWriteForm, closeCatCustomizer).

start* / stop*: 동작 시작/중지 (startCamera, stopRoomCam, startWithSelected).

_xxx (언더스코어 prefix): 내부 헬퍼 함수 (외부에서 직접 호출 금지) — _gardenSVG, _buildPreviewSVG, _bgInit.


CV
-absence detection
is_absent : 이탈 중 여부 (bool)
absence_duration_s : 현재 이탈 경과 시간 (float)
absence_count : 세션 총 이탈 횟수
total_absence_s : 세션 총 이탈 시간 (초)
get_stats() : 세션 종료 후 호출. 이탈 통계 dict 반환
def _detect_face(frame) : 프레임에서 얼굴 존재 여부를 반환하는 함수 bool  
current_absence_s : 현재 이탈 경과 시간(이탈 중 아니면 0)
def _detect_face(frame) : 프레임에서 얼굴 존재 여부를 반환하는 함수 (bool)

1. 카메라 캡처 / 스트리밍 (Vision/vision.py)

cap : OpenCV VideoCapture 객체 (전역).

is_running : 캡처 루프 동작 여부 플래그.

capture_thread : _capture_loop를 실행하는 데몬 스레드.

latest_frame : 가장 최근 인코딩된 JPEG 바이트 (스트리밍용).

latest_data : 가장 최근 분석 결과 dict (얼굴/EAR/자리비움/거북목 등).

lock : latest_frame / latest_data 동시 접근 보호용 threading.Lock.

current_subject / current_username : 현재 학습 세션 컨텍스트.

_camera_start_time : 카메라 시작 시각 (스트레칭 인터벌 계산).

_stretch_shown_at : 스트레칭 오버레이 마지막 표시 시각.

start_camera() : 캡처 시작 (VideoCapture 열고 스레드 기동).

stop_camera() : 캡처 중단 및 cap.release().

_capture_loop() : 프레임 루프 — 얼굴/EAR/자리비움/거북목 분석 + 오버레이 + DB 저장.

generate_frames() : MJPEG 스트림용 yield 제너레이터.

get_focus_data() : 현재 분석 결과(latest_data) 스냅샷 반환.

set_current_subject(subject) / set_current_username(username) : 세션 컨텍스트 갱신.

2. 얼굴 / EAR 분석 (vision.py)

LEFT_EYE / RIGHT_EYE : MediaPipe FaceMesh 눈 landmark 인덱스 리스트.

BUFFER_SIZE : 얼굴 검출 디바운싱용 buffer 길이 (=5).

ABSENCE_THRESHOLD_S : 이탈 판정 임계 시간(초) (=2.0).

RETURN_CONFIRM_S : 복귀 확정 대기 시간(초) (=1.0).

_get_face_mesh() : MediaPipe FaceMesh 모델 lazy 로더.

calculate_ear(landmarks, eye_indices, w, h) : EAR(Eye Aspect Ratio) 계산. 0.2 미만이면 졸음 판정.

3. 자리비움 감지 — AbsenceDetector (vision.py)

class AbsenceDetector : 얼굴 존재 여부 시계열을 이용한 자리비움 상태머신.

self.is_absent : 현재 이탈 중 여부 (bool).

self.absence_start : 이탈 시작 시각 (timestamp).

self.return_since : 복귀 후 확정 대기 시작 시각.

self.last_seen_ts : 마지막으로 얼굴이 보였던 시각.

self.buffer : 최근 N프레임 얼굴 검출 결과 deque (디바운싱).

self.absence_count : 누적 이탈 횟수.

self.total_absence_s : 누적 이탈 시간(초).

update(face_present) : 매 프레임 호출, 상태 전이.

get_current_absence_duration() : 현재 이탈 경과 시간 반환 (아니면 0.0).

4. 거북목 / 어깨 감지 (Vision/neck.py)

NECK_WARN_ANGLE : 경고(warn) 임계 각도 (=15°).

NECK_BAD_ANGLE  : 불량(bad) 임계 각도 (=25°).

SHOULDER_TILT_THRESH : 어깨 좌우 y 차이 임계 (=0.04, 정규화 좌표).

ALERT_HOLD_S : 나쁜 자세 지속 시 알림 발생까지 대기(초) (=10.0).

ALERT_COOLDOWN_S : 알림 재발생 최소 간격(초) (=300.0).

class NeckPostureDetector : MediaPipe Pose 기반 거북목 판정기.

self.neck_angle : 최신 목 각도(°).

self.status : "good" | "warn" | "bad" | "unknown".

self._bad_start : "bad" 상태 시작 시각 (내부).

self.bad_seconds : 현재 "bad" 지속 시간(초).

self._last_alert : 마지막 알림 발생 시각.

self.alert_count : 누적 알림 발생 수.

update(frame_rgb) : 프레임을 받아 거북목 dict 반환 (current_data에 ** 스프레드).

_make(...) : update 반환 dict 빌더 (내부 헬퍼).

_get_pose() : MediaPipe Pose 모델 lazy 로더.

_calc_neck_angle(lm) : 귀-어깨 landmark로 목 기울기 각도 계산.

draw_neck_overlay(frame, neck_data) : 프레임에 거북목 상태 텍스트 오버레이.

5. 거북목 응답 필드 (current_data 병합)

pose_detected : 포즈 추정 성공 여부 (bool).

neck_angle : 목 각도(°).

shoulder_tilt : 좌우 어깨 정규화 y 차이.

neck_status : "good"/"warn"/"bad"/"unknown".

neck_bad_seconds : 현재 "bad" 지속 시간(초).

neck_should_alert : 이번 프레임에 알림을 띄울지 여부.

neck_alert_count : 누적 알림 수.

6. 스트레칭 가이드 / 알림 (neck.py + vision.py)

STRETCHING_GUIDE : 스트레칭 동작 dict 리스트 (title, desc) — 프론트에서 조회.

STRETCH_INTERVAL_S : 스트레칭 알림 발생 간격(초) (=3600).

STRETCH_SHOW_S : 알림 오버레이 표시 지속 시간(초) (=8.0).

stretch_reminder : current_data에 병합되는 boolean 필드 (현재 알림 표시 중 여부).

_STATUS_COLOR / _STATUS_LABEL : 거북목 상태별 OpenCV 색상/텍스트 매핑 (내부 상수).

7. 한글 오버레이 (vision.py)

_KOREAN_FONT_PATHS : 한글 폰트 후보 경로 리스트.

_get_korean_fonts() : 시스템에서 한글 폰트 로드 (Pillow ImageFont).

_draw_korean_overlay(frame, line1, line2) : 한글 텍스트를 PIL로 그려 OpenCV 프레임에 합성.

8. 명명 규칙 (CV Prefix 컨벤션)

대문자 + 언더스코어 (UPPER_SNAKE) : 모듈 전역 상수 — 임계값/인덱스/시간 등 (NECK_WARN_ANGLE, ABSENCE_THRESHOLD_S, LEFT_EYE).

class XxxDetector : 시계열 상태머신 형태의 감지기 클래스 (AbsenceDetector, NeckPostureDetector).

_get_xxx() : 외부 모델/리소스의 lazy 로더 (_get_face_mesh, _get_pose, _get_korean_fonts).

_calc_xxx() : 단발 수치 계산 헬퍼 (_calc_neck_angle).

calculate_xxx() : 공용 수치 계산 (calculate_ear).

draw_xxx_overlay() : OpenCV 프레임 위에 시각화 텍스트/도형 그리기 (draw_neck_overlay).

_capture_loop / _make / _draw_xxx (언더스코어 prefix) : 모듈 내부 헬퍼 — 외부에서 직접 호출 금지.

is_xxx / xxx_count / total_xxx_s / current_xxx_s : 상태 플래그 / 누적 카운트 / 누적·현재 경과 시간(초) 명명 패턴.

xxx_should_alert : 이번 프레임에 클라이언트에 알림을 띄울지 결정하는 1회성 boolean.


database function
# 데이터베이스 관련 함수

- DB 연결: get_
   get_conn()

- DB 초기화: init_
   init_db()

- 데이터 저장: save_ / insert_
   save_data()

# 데이터 처리 및 계산 함수

- 데이터 조회 및 반환: get_
  - get_score()

