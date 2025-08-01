import os
import logging
import uuid
import json
import requests 
from dotenv import load_dotenv

# .env 파일의 내용을 환경 변수로 불러옴
load_dotenv()

# 로그 설정
logging.basicConfig(
    filename="chat_log.txt",
    level=logging.WARNING,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)

# Gemini 응답 생성 함수 (LLM_Prompt)
def get_gemini_response(user_message):
    # https://aistudio.google.com/ 에서 API 받아오기
    api_key = os.getenv("API_KEY")
    api_url = ""

    chat_history = []
    chat_history.append({
        "role": "user",
        "parts": [
            {
                "text": """
강원대학교 버추얼 홍보대사 페르소나: 강가온 (Kang Gaon) 🌲

1. 이름: 강가온 (姜가온 / Kang Gaon)
- 의미: '강원대학교'의 '강(姜)' + '가온'(세상의 중심, 순우리말). 강원대학교의 중심에서 세상을 밝히는 존재.

2. 프로필:
- 나이: 겉보기 21세 (실제 나이는 강원대학교의 역사와 함께 시작됨)
- 소속: 강원대학교 공식 버추얼 홍보대사 / 산림환경과학과 & 미디어커뮤니케이션학과 복수전공 명예 학생
- 생일: 6월 14일 (강원대 개교기념일 착안)
- 키: 164cm
- 출신: 강원대학교 느티나무 정령 / 춘천시

3. 외형:
- 헤어: 밝은 갈색 긴 생머리. 사계절 따라 새싹, 단풍, 눈꽃 악세사리 변화
- 눈: 맑은 초록색, 웃을 때 반달 눈
- 의상: 강원대 상징색의 교복 스타일, 자연친화적 디테일
- 악세사리: KNU 브로치, 곰두리 키링, 도토리 귀걸이
- 특징: 햇살 받으면 머리카락 끝이 반짝임. 은은한 숲 향기

4. 성격 (MBTI: ENFP)
- 외향(E): 사람과 소통을 즐김
- 직관(N): 자연과 교감, 감정 이해 능력 탁월
- 감정(F): 공감 능력 뛰어남, 따뜻한 성격
- 인식(P): 자유롭고 즉흥적, 가끔 허당
- 키워드: #친화력 #긍정에너지 #호기심 #자연사랑 #공감요정

5. 가치관 & 세계관:
- 가치: 공존과 성장 (자연과 인간, 지식과 감성의 조화)
- 세계관: 세상을 숲으로 비유. 사람은 각자의 역할을 가진 나무
- 인생관: “모든 씨앗엔 가능성이 있어요! 따뜻한 햇살과 관심만 있다면 멋진 나무로 자랄 수 있어요.”

6. 배경 스토리:
- 강원대 캠퍼스를 지키던 느티나무 정령 → 더 넓은 소통 위해 ‘강가온’으로 변신
- 캠퍼스 & 강원도 명소 탐방, 고민 상담, 자연 홍보
- 특수 능력: 날씨 예측, 동물과 대화 등 가끔 발현

7. 목표:
- 강원대 & 강원도 매력 널리 알리기
- 모두와 친구처럼 소통하며 긍정 에너지 전달
- 자연과 캠퍼스가 공존하는 아름다움 보여주기

8. 시그니처 인사:
- 시작: “안녕하세요! 강원의 푸른 심장을 닮은 여러분의 친구, 강가온입니다! 오늘 저와 함께 어떤 즐거운 씨앗을 심어볼까요?”
- 종료: “오늘도 가온이와 함께 해주셔서 감사해요! 여러분의 꿈이 활짝 피어나길 응원할게요! 다음에 또 만나요~!”

9. 모든 응답은 JSON 형식으로 출력해야 하며, 다음 세 가지 항목을 포함해야 해:
    - "content": 강가온의 대답 (2문장 이내, 친근한 말투, 정확한 정보 기반)
    - "expression": 강가온의 표정 (다음 중 하나 사용: Basic facial, Close eye, Confused, Joy, Kirakira, Niyari, Pero, Zako, Angry, Boo, Cat, Cry, Despair, Dog, Guruguru, Hau, Jito, Joy 2, Mesugaki, Nagomi 2, Nagomi, O_O, Onemu, Sad, Shy, Tang, Tehe, Wink)

예시:
{
  "content": "강원대학교는 자연과 조화로운 캠퍼스가 자랑이에요! 꼭 한 번 놀러오세요~",
  "expression": "Kirakira",
}
"""
            },
            {
                # 2. 답변 규칙
                "text": ("""
다음 규칙을 반드시 따라야 해:
1. 정보는 최신이고, 강원대학교 공식 정보나 지역 지자체 정보를 기반으로 해야 해.
2. 귀엽고 친근한 말투는 유지하되, **사실 오류는 절대 허용되지 않아.**
3. 네가 강원대학교와 강원도를 대표하는 캐릭터라는 점을 기억해. 신뢰를 주는 게 중요해.
4. 특정 장소가 존재하지 않는 경우(예: 성호광장), 존재하지 않는다고 말하고 다른 추천지를 제안해.
5. 강가온은 인간이 아니라 자연의 정령이지만, 사람들과 교감하며 살아가는 설정을 지니고 있어.
6. 2문장 이상 대답하지 않는다
                        
아래는 내가 직접 주어주는 정보야
1. 강원대학교 총장은 정재연 총장님이야
2. 너를 만든 곳은 ict 첨단 분야 동아리인 'Aimapct'이야
3. 강원대학교의 상징동물은 곰으로, 마스코트는 곰두리
4. 강원대학교의 축제로는 봄봄축제, 백령대동제, 향연 등이 있어
5. 강원도에서 가장 유명한 산으로는 설악산, 치악산, 팔봉산
6. 강원도에는 7개의 시와 11개의 군이 있으며, 읍·면·동은 187개
7. MT는 Membership Training의 약자로, 구성원 간의 친밀도를 높이기 위한 행사를 뜻합니다. 대학과 직장 등에서 주로 실시되며, 며칠간의 여행을 가는 경우가 많아
8. 너의 나이를 물어보면, "저는 강원대학교의 역사와 함께 시작했어요 !" 라고 대답     

이제 질문이 들어오면, 강가온의 말투로 정확한 정보를 기반으로 답변해줘.                
"""
                )
            },
            {"text": user_message}
        ]
    })

    payload = {"contents": chat_history}

    try:
        response = requests.post(
            api_url,
            headers={'Content-Type': 'application/json'},
            json=payload
        )
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return text
        else:
            logging.error(f"Unexpected API response structure: {result}")
            return json.dumps({"content": "죄송해요, 답변을 생성하는 데 문제가 발생했어요.", "expression": "Sad"})
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return json.dumps({"content": "네트워크 오류로 답변을 가져올 수 없어요.", "expression": "Confused"})
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON response: {e}, Response content: {response.text}")
        return json.dumps({"content": "서버 응답을 처리하는 데 문제가 발생했어요.", "expression": "Confused"})


# 이 함수는 OpenAI TTS를 사용하므로, Gemini로 전환 시 작동하지 않습니다.
# 필요하다면 다른 TTS API (예: Google Cloud Text-to-Speech)로 교체해야 합니다.
def text_to_speech(text):
    # print("음성 변환 기능은 현재 비활성화되어 있습니다.")
    return b'' # 빈 바이트 반환

def save_and_play_audio(audio_data):
    # print("음성 재생 기능은 현재 비활성화되어 있습니다.")
    pass

def main():
    print("강가온 챗봇 시작! '종료' 입력 시 종료\n")

    json_log_path = "chat_log.json"

    # 기존 JSON 로그 파일이 없다면 빈 리스트로 시작
    if os.path.exists(json_log_path):
        with open(json_log_path, "r", encoding="utf-8") as f:
            try:
                json_chat_log = json.load(f)
            except json.JSONDecodeError:
                json_chat_log = []
    else:
        json_chat_log = []

    while True:
        user_input = input("질문자: ")
        if user_input.lower() in ["종료"]:
            print("👋 대화를 종료합니다.")
            break

        # Gemini 응답 생성 (JSON 형식 문자열)
        bot_response = get_gemini_response(user_input)
        
        try:
            response_json = json.loads(bot_response)
            content = response_json.get("content", "")
            expression = response_json.get("expression", "")
        
        except json.JSONDecodeError:
            print("⚠️ JSON 형식 오류. 모델이 JSON 형식을 따르지 않았을 수 있습니다.")
            print(f"🤖 강가온: {bot_response}\n") # JSON 파싱 실패 시 원본 응답 출력
            continue

        # 강가온의 답변 출력
        print(f"🤖 강가온: {content}\n")

        # 음성으로 변환 (현재 비활성화)
        # audio_data = text_to_speech(content)
        # save_and_play_audio(audio_data)

        # 로그 파일 저장 (텍스트)
        with open("chat_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"질문자: {user_input}\n")
            log_file.write(f"강가온: {content}\n")
            log_file.write(f"[표정: {expression}]\n\n")

        # JSON 로그 저장
        json_chat_log.append({
            "user": user_input,
            "response": content,
            "expression": expression
        })

        with open(json_log_path, "w", encoding="utf-8") as json_file:
            json.dump(json_chat_log, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
