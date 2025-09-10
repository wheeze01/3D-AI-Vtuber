# AI-vtuber 유튜브 방송 채팅 크롤링 시스템 🎥🤖

이 프로젝트는 **AI 기반 버튜버(가상 유튜버) 방송 시스템**에 대한 설명입니다.  
그 중 유튜브 방송 채팅 크롤링 시스템은 실시간 음성 합성, 유튜브 채팅 가져오기, 가상 케이블을 통한 마이크 설정(VB-CABLE 사용), OBS 연동 부분입니다.

---

## 🚀 주요 내용
- 실시간 음성 합성 (TTS) + 립싱크
- 가상 케이블을 통한 마이크 설정
- OBS 연동을 통한 방송 송출 (유튜브)
- 디버깅 및 프롬프트 엔지니어링: 채팅 기반 캐릭터 반응 (log 분석)<br><br>
<code>각 코드는 VS code 사용을 권장합니다. </code>

---

## 🐤 앞으로 해야하는 것
- [ ] 와루도를 통한 방송 진행 및 로그 분석
- [ ] 필터링 기능 체크
- [ ] API 사용 비용 예측
- [ ] 추가 계획 : https://docs.google.com/document/d/1vHcjmMWHKweeZkmWyMNVDupdp6ilRgba2bhFnI2zd8o/edit?usp=sharing

---

## 📂 프로젝트 구조
```bash
3D-AI-Vtuber/
├─ Chat_Bot_unused/       # 사용하지 않음. 이전에 했던 작업물 모음 (참고만 할 것)
├─ Chat_Bot_used/         # 현재 사용하는 코드 모음입니다.
│  ├─ .env.example/       # 각 API 설정부분. 방송 설정전에 꼭 확인하세요.
│  ├─ Chat_bot_main.py/   # 메인 코드입니다. (방송시 이 코드만 사용합니다.)
│  └─ Chat_filter.py      # 채팅 필터링과 관련된 별도만든 라이브러리입니다. (실행하는거 아님)
├─ logs/                  # 방송중 실시간으로 해당 폴더로 채팅 및 챗붓의 반응 전부 기록됩니다.
├─ .gitignore             # GIT을 사용할떄 꼮 기입 (API 같이 올라가기 방지용입니다.)
├─ docs/                  # 문서 및 인수인계 가이드
└─ README.md

