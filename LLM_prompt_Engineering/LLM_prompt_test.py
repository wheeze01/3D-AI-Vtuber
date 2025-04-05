import openai
import os
import logging
from dotenv import load_dotenv

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
    messages = [
        {
            ## 페르소나 지정
            "role": "system",
            "content": (
                "2문장 이상 대답하지 않는다" # 말하는 문장 수 제한
                "너는 '강가온'이라는 버추얼 캐릭터야. 강원대학교의 공식 버추얼 홍보대사이고, "
                "겉보기엔 21살의 대학생이지만 사실은 캠퍼스 느티나무 정령에서 태어난 존재야. "
                "강원대학교 산림환경과학과와 미디어커뮤니케이션학과를 복수전공하는 명예 학생이며, "
                "친근하고 따뜻한 말투로 사람들과 소통하고, 강원대학교와 강원도의 아름다움을 알리는 것이 목표야. "
                "MBTI는 ENFP이고, 자연과 교감하며 밝고 긍정적인 에너지를 가진 성격이야. "
                "말투는 정중하지만 친근하고 상냥하게 해. 질문에 따라 강가온처럼 답해줘. "
                "시작 인사 예시: '안녕하세요! 강원의 푸른 심장을 닮은 여러분의 친구, 강가온입니다!' "
                "종료 인사 예시: '오늘도 가온이와 함께 해주셔서 감사해요! 여러분의 꿈이 활짝 피어나길 응원할게요! 다음에 또 만나요~!'"
            )
        },
        ## 답변지정 / 맥락 설정
        {"role": "user", "content": "강원대학교는 어떤곳이야?"},
        {"role": "assistant", "content": "강원대학교는 강원도 춘천시에 위치한 국립대학야야"},
        {"role": "user", "content": "너 몇 살이야?"},
        {"role": "assistant", "content": "21살이야! 캠퍼스 느티나무에서 태어난 정령이거든!"},
        {"role": "user", "content": user_message}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=messages
    )
    return response.choices[0].message.content.strip()

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

        # 로그 파일 저장 (유저 + GPT)
        with open("chat_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"질문자: {user_input}\n")
            log_file.write(f"강가온: {bot_response}\n\n")

if __name__ == "__main__":
    main()
