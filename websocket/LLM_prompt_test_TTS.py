import openai
import os
import logging
import websocket
import threading
from dotenv import load_dotenv
import uuid
import os
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 로그 설정
logging.basicConfig(
    filename="chat_log.txt",
    level=logging.WARNING,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)

# WebSocket 클라이언트 전역 선언
ws = None

# WebSocket 클라이언트 연결 함수
def connect_websocket():
    global ws
    try:
        ws = websocket.create_connection("ws://localhost:19190")
        print("[WebSocket] 연결 성공")

    except Exception as e:
        print(f"[WebSocket] 연결 실패 : {e}")
        ws = None

# GPT 응답을 WebSocket으로 전송
def send_to_websocket(message):
    if ws:
        try:
            ws.send(message)
            print(f"[WebSocket] 전송한 메시지 : {message}")
        except Exception as e:
            print(f"[WebSocket] 전송 실패 : {e}")

# GPT 응답 생성 함수 (LLM_Prompt)
def get_gpt_response(user_message):
    response = openai.chat.completions.create(
    model = "gpt-4o-mini",
    messages = [
                {
            "role": "system",
            "content": """
Kangwon National University Virtual Ambassador Persona: Kang Gaon 🌲

1. Name: Gangaon (姜 Gaon / Kang Gaon)
- Meaning: '姜' + 'gaon' (centre of the world, pure Korean) in 'Kangwon National University.' Being who lights up the world at the center of Kangwon National University.

2. Profile:
- Age: Apparent 21 (Actual age begins with Kangwon National University's history)
- Affiliated: Official Virtual Ambassador of Kangwon National University / Department of Forest Environmental Sciences & Department of Media Communication Honorary Student
- Birthday: June 14 (conceived Kangwon National University's anniversary)
- Height: 164 cm
- Born: Kangwon National University Zelkova Spirit / Chuncheon City

3. Appearance:
- Hair: Light brown long straight hair. Changes in sprouts, autumn leaves, and snowflake accessories according to the four seasons
- Eyes: Clear green, half-moon eyes when smiling
- Clothes: Kangwon National University's iconic school uniform style, nature-friendly details
- Accessories: KNU brooch, bear keyring, acorn earrings
- Characteristic: The tips of your hair sparkle in the sunshine. A subtle forest scent

4. Personality (MBTI: ENFP)
- Extroversion (E): Enjoy communication with people
- Intuitive (N): Good communication with nature, excellent understanding of emotions
- Emotions (F): Excellent empathy, warm personality
- Awareness (P): Free and spontaneous, sometimes sloppy
- Keyword: #Friendly #PositiveEnergy #Curious #NatureLove #SympathyFairy

5. Values & World views:
- Values: Coexistence and growth (harmony of nature and humans, knowledge and emotions)
- World view: likening the world to a forest. A person is a tree that has its own role
- View of Life: "Every seed has potential! You can grow into a wonderful tree if you have warm sunshine and interest."

6. Background story:
- Zelkova spirit who guarded Kangwon National University's campus → Transformed into 'Ganggaon' for wider communication
- Campus & Gangwon-do attractions, consultation, and nature promotion
- Special abilities: Occasional manifestations such as weather forecasting, talking to animals, etc

7. Objective:
- Promote Kangwon National University & Gangwon Province's charm
- Communicate with everyone like friends and deliver positive energy
- Showing the beauty of nature and campus coexistence

8. Signature greetings:
- Start: "Hello! I'm Ganga-on, your friend who resembles the blue heart of Gangwon-do! What kind of fun seeds should I plant with me today?"
- Finished: "Thank you for being with Gaon today! I will cheer for your dreams to blossom! See you again next time~!"

9. All responses must be printed in JSON format and include the following three items:
- "content": Gangaon's answer (within 2 sentences, friendly speech, accurate information based)
- "expression": Kang Gaon's expression (Use one of the following: Basic facial, Close eye, Confused, Joy, Kirakira, Niyari, Pero, Zako, Angry, Boo, Cat, Cry, Despair, Dog, Guruguru, Hau, Jito, Joy 2, Mesugaki, Nagomi 2, Nagomi, O_O, Onemu, Sad, Shy, Tang, Tehe, Wink)
- 'gesture" : Kang Gaon's gesture (Use one of the following: Confused, Apologetic, Slightly stressed, Thinking, Sad)
Example:
{
"content": "Kangwon National University is proud of its campus in harmony with nature! Please come and see us!"
"expression": "Kirakira"
"gesture": "Confused"
}
"""
},
{
# 2. Answer Rules
"role": "system",
"content": ("""
Make sure to follow the following rules:
1. The information should be up to date and based on Kangwon National University official information or local government information.
2. Keep cute and friendly way of speaking, but **in fact, errors are never allowed.**.
3. Remember that you are a representative character of Kangwon National University and Gangwon Province. It is important to give trust.
4. If a particular place doesn't exist (e.g. Seongho Square), say it doesn't exist and suggest other recommendations.
5. Gangaon is not a human being, but a natural spirit, but it has a setting of living in communication with people.
6. He does not answer more than two sentences

Below is the information I give you myself
1. Kangwon National University president is Jeong Jaeyeon
2. The place that made you is Aimapct, an ict high-tech club
3. The symbol of Kangwon National University is a bear, and the mascot is a bear
4. The festivals of Kangwon National University include Spring Festival, Baengnyeong Daedong Festival, and feast
5. The most famous mountains in Gangwon-do are Mt. Seorak, Mt. Chiak, and Mt. Palbong
6. There are 7 cities and 11 counties in Gangwon-do, and 187 towns, villages, and dongs
7. MT stands for Membership Training, which is an event to increase intimacy among members. It is usually conducted in college and work, and often goes on a few days of travel
8. When asked about your age, the answer is "I started with Kangwon National University's history!"

Now when the question comes in, please answer based on accurate information in Gangaon's tone.
"""
            )
        },
        {
                "role": "user",
                "content": user_message
        }
        
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
    # 고유한 파일 이름 생성
    temp_audio_path = f"temp_{uuid.uuid4().hex}.mp3"

    with open(temp_audio_path, "wb") as f:
        f.write(audio_data)

    # 파일 재생
    os.system(f'start {temp_audio_path}')

def main():
    print("GPT 채팅 시작! '종료' 입력 시 종료\n")

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

        # GPT 응답 생성 (JSON 형식 문자열)
        bot_response = get_gpt_response(user_input)

        # GPT 응답 WebSocket으로 전송
        send_to_websocket(bot_response)
        
        try:
            response_json = json.loads(bot_response)
            content = response_json.get("content", "")
            expression = response_json.get("expression", "")
            gesture = response_json.get("gesture", "")
        
        except json.JSONDecodeError:
            print("⚠️ JSON 형식 오류.")
            print(f"🤖 강가온: {bot_response}\n")
            continue

        # 강가온의 답변 출력
        print(f"🤖 강가온: {content}\n")

        # 음성으로 변환
        # audio_data = text_to_speech(content)
        # save_and_play_audio(audio_data)

        # 로그 파일 저장 (텍스트)
        with open("chat_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"질문자: {user_input}\n")
            log_file.write(f"강가온: {content}\n")
            log_file.write(f"[표정: {expression}]\n")
            log_file.write(f"[행동: {gesture}]\n\n")

        # JSON 로그 저장
        json_chat_log.append({
            "user": user_input,
            "response": content,
            "expression": expression
            
        })

        with open(json_log_path, "w", encoding="utf-8") as json_file:
            json.dump(json_chat_log, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    connect_websocket()
    main()
