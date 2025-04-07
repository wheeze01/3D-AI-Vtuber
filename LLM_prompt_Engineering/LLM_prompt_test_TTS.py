import openai
import os
import logging
from dotenv import load_dotenv
import tempfile
import playsound

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 로그 설정
logging.basicConfig(
    filename="chat_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)

# GPT 응답 생성 함수 (LLM_Prompt)
def get_gpt_response(user_message):
    response = openai.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [
                {
            "role": "system",
            "content": """
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
"""
        },
        {
            # 2. 답변 규칙
            "role": "system",
            "content": (
                "2문장 이상 대답하지 않는다" # 말하는 문장 수 제한
            )
        },
        # 3. 답변지정 / 맥락 설정
        {"role": "user", "content": "강원대학교는 어떤곳이야?"},
        {"role": "assistant", "content": "강원대학교는 강원도 춘천시에 위치한 국립대학야야"},
        {"role": "user", "content": user_message},

        # 4. 디버깅
        #{"role": "user", "content": "너 몇 살이야?"},
        #{"role": "assistant", "content": "21살이야! 캠퍼스 느티나무에서 태어난 정령이거든!"}
        
    ]
    )
    return response.choices[0].message.content.strip()
 
def text_to_speech(text):  # 선택: 'nova', 'shimmer', 'fable' 등
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    return response.content  # 🔥 bytes 형태로 반환됨

def save_and_play_audio(audio_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(audio_data)  # 🔥 여기에 bytes만 들어가야 함
        temp_audio_path = temp_audio.name

    playsound.playsound(temp_audio_path)
    os.remove(temp_audio_path)  # 재생 후 파일 삭제


def main():
    print("GPT 채팅 시작! '종료' 입력 시 종료\n")

    while True:
        user_input = input("질문자: ")
        if user_input.lower() in ["종료"]:
            print("👋 대화를 종료합니다.")
            break

        # GPT 응답 생성
        bot_response = get_gpt_response(user_input)
        print(f"🤖 강가온: {bot_response}\n")

        audio_data = text_to_speech(bot_response)
        save_and_play_audio(audio_data)
        
        
        # 로그 파일 저장 (유저 + GPT)
        with open("chat_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"질문자: {user_input}\n")
            log_file.write(f"강가온: {bot_response}\n\n")

if __name__ == "__main__":
    main()
