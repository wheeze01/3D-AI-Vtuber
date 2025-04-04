import os
import openai
import pytchat
import logging
from time import sleep
from gtts import gTTS
import pygame
from dotenv import load_dotenv

load_dotenv()

# 1. OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 2. YouTube API 키 설정
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# 3. YouTube 라이브 채팅 비디오 ID 설정
## 유튜브 스트리밍 방송을 키고 해당 url의 ID 참고
## 예시. url = https://studio.youtube.com/video/examplevidoeid/livestreaming? = asdqwezxc 일 경우 VIDED_ID = examplevidoeid

YOUTUBE_VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID")

# 4. 응답을 저장할 파일
TEXT_FILE = "gpt_response.txt"

# 5. 로깅 설정
logging.basicConfig(
    filename="chat_log.txt",
    level=logging.WARNING,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)

# TTS로 음성 파일 생성
def generate_tts(text, mp3_file="output.mp3"):
    tts = gTTS(text=text, lang="ko")
    tts.save(mp3_file)
    #print(f"[INFO] TTS 음성 파일 생성 완료: {mp3_file}")

def play_audio(mp3_file="output.mp3"):
    pygame.mixer.init()  
    pygame.mixer.music.load(mp3_file)  # MP3 파일 로드
    pygame.mixer.music.play()  

    while pygame.mixer.music.get_busy():  
        continue

    pygame.mixer.quit()  

# OpenAI GPT 응답 생성 함수
def get_gpt_response(user_message):
    messages = [
        {"role": "system", "content": "너는 대학생이야. 강원대학교 학생이기도 하고. 누가 물어보면 그냥 강원대학교 학생이라고 해."},
        {"role": "user", "content": user_message},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response["choices"][0]["message"]["content"]

# YouTube 채팅 메시지 읽기
def youtube_chat_bot():
    chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)

    while chat.is_alive():
        for message in chat.get().sync_items():
            user_name = message.author.name
            user_message = message.message
            log_message = f"{user_name}: {user_message}"
            print(log_message)

            # GPT 응답 생성
            bot_response = get_gpt_response(user_message)
            print(f"Bot: {bot_response}")

            # 유저 메시지 + GPT 응답을 로그 파일에 저장
            with open("chat_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"{log_message}\n")  # 유저 메시지
                log_file.write(f"Bot: {bot_response}\n\n")  # GPT 응답

            with open(TEXT_FILE, "w", encoding="utf-8") as f:
                f.write(bot_response)

            # TTS 변환 및 출력
            generate_tts(bot_response)
            play_audio()

        sleep(1)

if __name__ == "__main__":
    youtube_chat_bot()
