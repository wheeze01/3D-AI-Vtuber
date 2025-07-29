# ⭐ 코드 사용 방법 정리

### 1. OBS 설정하고 방송키기
- 유튜브 방송을 킨후 스트림키 가져오기
https://www.youtube.com/watch?v=WTzpQhCQGoQ

- OBS "제어" 항목의 "설정" 버튼을 누르고 "방송" 탭에서 스트림키 입력 <br><br>
  ![스크린샷 2025-04-04 190314](https://github.com/user-attachments/assets/da3c5d7d-f901-4ee4-9dd4-1c29a3c7543c)
 
- OBS의 YouTube Live Control Panel 에서 로그인후 "제어" 항목의 방송시작
<br><br>
### 2. 실시간 유튜브 스트리밍 방송의 ID를 환경변수에 넣기
 예시. url = https://youtube.com/live/examplecode1 일 경우 VIDED_ID = examplecode1
<br><br>
### 3. chat_bot_main.py 실행
- 유튜브 채팅에 대한 응답을 TTS로 출력 및 로그 분석 가능
- OBS에서 직접 TTS를 송출하고 싶으면 vb-audio virtual cable를 설치하고 오디오 추가하면 됨
