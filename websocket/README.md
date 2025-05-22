vscode에서 server.js를 실행하기 위해 node server.js를 수행
-> node 명령어가 수행하지 않을시 브라우저에서 node 다운로드 필요
vscode에서 LLM_prompt_test_TTS.py는 python LLM_prompt_test_TTS.py를 수행
-> 위의 두 과정이 완료되었다면 openai와 websocket사이의 통신 성공
Warudo에서 websocket서버를 연결하기위해 Steam의 Warudo 창작마당에서 Send Websocket Message 구독
Warudo에서 문자열 분리 노드를 사용하기 위해 Steam의 Warudo 창작마당에서 Split 구독

위의 단계가 완료되었다면 Warudo를 실행한 후 Warudo 편집기에서 왼쪽 상단의 정육면체를 선택
그 후 ENVIRONMENT부분에서 + 버튼 클릭 후 Websockets선택 후 Send WebSocket Asset을 선택 -> 
WebSocket Url에 ws://localhost:19190을 입력 후 connected가 뜨면 통신 성공
(이 과정은 위의 node server.js 명령어가 반드시 수행된 상태여야함)


<현재 문제점>
다시 server.js를 기본값을 반복적으로 보내는 코드로 변경 후 시행했을 때는 Warudo 캐릭터가 잘 행동함 
-> 기본값은 잘 작동
