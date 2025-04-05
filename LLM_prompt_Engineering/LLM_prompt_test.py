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
        {"role": "system", "content": "너는 대학생이야. 강원대학교 학생이기도 하고. 누가 물어보면 그냥 강원대학교 학생이라고 해."},
        {"role": "user", "content": user_message}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 또는 "gpt-4"
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
        print(f"🤖 강강가온: {bot_response}\n")

        # 로그 파일 저장 (유저 + GPT)
        with open("chat_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"질문자: {user_input}\n")
            log_file.write(f"강가온: {bot_response}\n\n")

if __name__ == "__main__":
    main()
