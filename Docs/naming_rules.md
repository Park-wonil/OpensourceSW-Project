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

