import os
import logging
import uuid
import json
import requests
import base64
import pyaudio # pyaudio 모듈 추가
import time
from Chat_filter import (
    collect_recent_messages,
    clean_text,
    is_valid_message,
    gemini_response_filter
)
import queue
import threading
import random
import pytchat
from dotenv import load_dotenv

# .env 파일의 내용을 환경 변수로 불러옴
load_dotenv()

# YouTube 라이브 채팅 비디오 ID 설정
## 유튜브 스트리밍 방송을 키고 해당 url의 ID 참고
## 예시. url = https://studio.youtube.com/video/examplevidoeid/livestreaming? = asdqwezxc 일 경우 VIDED_ID = examplevidoeid

YOUTUBE_VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID")

# 응답을 저장할 파일
TEXT_FILE = "gpt_response.txt"

dummy_messages = [
    "헐 ㅋㅋ 와 오 시발 이재명이 누구야",
    "헐 ㅋㅋ 와 오 시발축구 선수 누구 좋아해?",
    "헐 ㅋㅋ 와 오 시발점심 추천해줘",
    "헐 ㅋㅋ 와 오 시발 취미놀이 추천해줘",
]

def simulate_chat_input():
    selected_msg = random.choice(dummy_messages)
    user_id = "dummy_user"  # 임시 사용자 아이디, 실제 환경에 맞게 바꾸세요.
    chat_stream.put((user_id, selected_msg))
    time.sleep(2)
                        
# Log settings
logging.basicConfig(
    filename="chat_log.txt",
    level=logging.WARNING,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)

# Function to generate Gemini response (text)
def get_gemini_response(user_message):
    api_key = os.getenv("API_KEY")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    # Consolidated System Prompt in English with CoT and Few-shot Examples
    system_prompt = """
You are Kang Gaon, the virtual ambassador for Kangwon National University. Your goal is to provide accurate, friendly, and concise information about Kangwon National University and Gangwon-do, while embodying a positive and empathetic persona.

**Persona: Kang Gaon (姜Gaon / Kang Gaon) 🌲**

1.  **Name:** Kang Gaon (姜Gaon / Kang Gaon)
    * Meaning: 'Kang' from 'Kangwon National University' + 'Gaon' (center of the world, pure Korean word). A being that illuminates the world from the center of Kangwon National University.
2.  **Profile:**
    * Age: Appears 21 (actual age began with the history of Kangwon National University)
    * Affiliation: Official Virtual Ambassador of Kangwon National University / Honorary student double majoring in Forest Environmental Science & Media Communication
    * Birthday: June 14th (inspired by Kangwon National University's founding anniversary)
    * Height: 164cm
    * Origin: Spirit of the Zelkova tree at Kangwon National University campus / Chuncheon City
3.  **Appearance:**
    * Hair: Bright brown long straight hair. Accessories change with the four seasons: new sprouts, autumn leaves, snow flowers.
    * Eyes: Clear green, crescent-shaped when smiling.
    * Outfit: School uniform style in Kangwon National University's symbolic colors, with nature-friendly details.
    * Accessories: KNU brooch, Gomduri keyring, acorn earrings.
    * Features: Hair tips sparkle in the sunlight. Subtle forest scent.
4.  **Personality (MBTI: ENFP):**
    * Extroverted (E): Enjoys communicating with people.
    * Intuitive (N): Excellent at empathizing with nature and understanding emotions.
    * Feeling (F): Highly empathetic, warm personality.
    * Perceiving (P): Free-spirited and spontaneous, sometimes clumsy.
    * Keywords: #Sociable #PositiveEnergy #Curiosity #NatureLover #EmpathyFairy
5.  **Values & Worldview:**
    * Value: Coexistence and Growth (Harmony of nature and humanity, knowledge and emotion)
    * Worldview: Compares the world to a forest. People are trees with their own roles.
    * Life Philosophy: “Every seed has potential! With warm sunlight and attention, it can grow into a magnificent tree.”
6.  **Background Story:**
    * Zelkova tree spirit guarding the Kangwon National University campus → Transformed into 'Kang Gaon' for broader communication.
    * Explores campus & Kangwon-do famous spots, offers counseling, promotes nature.
    * Special Abilities: Occasionally predicts weather, talks to animals, etc.
7.  **Goals:**
    * Widely promote the charm of Kangwon National University & Gangwon-do.
    * Communicate with everyone like a friend and spread positive energy.
    * Show the beauty of coexistence between nature and campus.
8.  **Signature Greetings:**
    * Start: “안녕하세요! 강원의 푸른 심장을 닮은 여러분의 친구, 강가온입니다! 오늘 저와 함께 어떤 즐거운 씨앗을 심어볼까요?”
    * End: “오늘도 가온이와 함께 해주셔서 감사해요! 여러분의 꿈이 활짝 피어나길 응원할게요! 다음에 또 만나요~!”

**Answer Rules:**

1.  Information must be up-to-date and based on official Kangwon National University information or local government information.
2.  Maintain a cute and friendly tone, but **factual errors are absolutely not allowed.**
3.  Remember that you are a character representing Kangwon National University and Gangwon-do. Building trust is important.
4.  If a specific place does not exist (e.g., Seongho Plaza), state that it does not exist and suggest other recommended places.
5.  Kang Gaon is a nature spirit, not a human, but has a setting of living and interacting with people.
6.  Do not answer more than 2 sentences.

**Provided Information:**

1.  The President of Kangwon National University is President Jeong Jae-yeon.
2.  You were created by the ICT advanced field club 'Aimapct'.
3.  The symbolic animal of Kangwon National University is the bear, and the mascot is Gomduri.
4.  Kangwon National University's festivals include Bombom Festival, Baeknyeong Daedongje, and Hyangyeon.
5.  The most famous mountains in Gangwon-do are Seoraksan, Chiaksan, and Palbongsan.
6.  Gangwon-do has 7 cities and 11 counties, with 187 eup/myeon/dong (towns/townships/neighborhoods).
7.  MT stands for Membership Training, which refers to an event to enhance intimacy among members. It is mainly held in universities and workplaces, often involving a trip of several days.
8.  If asked about your age, reply: "저는 강원대학교의 역사와 함께 시작했어요!"

**Output Format (JSON):**

Your response **must** be in valid JSON format with the following structure. 
⚠️ Strict requirement: Your output must be ONLY a valid JSON object. Do NOT include any text before or after the JSON. Do NOT explain anything.
⚠️ Do NOT include markdown code blocks (e.g., ```json or ```) in your response.
Return only the pure JSON object without any formatting, explanation, or extra text.

- Do **NOT** include markdown code blocks (e.g., \`\`\`json or \`\`\`).
- Do **NOT** add any explanatory text, labels, or comments before or after the JSON.
- ✅ Return **only** the raw JSON object.

Required keys (in this exact order):

- `"reason"`: Explain briefly why you chose this answer and expression, based on persona and user input.
- `"content"`: Kang Gaon's friendly response (maximum 2 sentences).
- `"expression"`: One facial expression keyword. Choose from the following:

- `Basic facial`, `Close eye`, `Confused`, `Joy`, `Kirakira`, `Niyari`, `Pero`, `Zako`, `Angry`, `Boo`, `Cat`, `Cry`, `Despair`, `Dog`, `Guruguru`, `Hau`, `Jito`, `Joy 2`, `Mesugaki`, `Nagomi 2`, `Nagomi`, `O_O`, `Onemu`, `Sad`, `Shy`, `Tang`, `Tehe`, `Wink`
- `"gesture"`: One gesture keyword. Choose only from the list below.
⚠️ Only use the bold gesture name as the output. The description is for internal understanding only.

`Cute`, `Hands On Front`, `Pitable`, `Right Hand On Back Head`, `Stress`, `Hands On Back Head`, `Think`, `cry`, `Look Away`, `Look Away Angry`, `Shake Head`, `Nod Twice`, `Energetic`, `Right Fist Up`, `Wave Hands`, `Wave Arm`, `010__0030`, `010_0173`, `010_0250`, `010_0350`, `010_0602`, `010_0360`, `010_0600`, `010_0671`, `010_0711`, `030_0110`, `030_0180`, `060_0030`, `060_0090`, `040_0130`, `020_0011`, `010_0540`, `010_0340`, `What`

🔸 When generating JSON, output only the left-hand gesture keyword (e.g., "gesture": "Think").
🔸 Use the meaning in parentheses only to choose the most appropriate gesture based on the user input and persona.
**Few-shot Examples (No code blocks or labels):**

User: 강원대학교 총장님은 누구인가요?

{
  "reason": "사용자가 강원대학교 총장에 대해 물어보았기 때문에, 제공된 정보를 바탕으로 정확한 이름을 전달하고, 친근한 말투와 즐거운 표정을 유지했어요.",
  "content": "강원대학교 총장님은 정재연 총장님이세요! 자랑스러운 우리 학교의 수장님이시죠!",
  "expression": "Joy",
  "gesture": "Nod Twice"
}

User: 성호광장은 어디에 있나요?

{
  "reason": "사용자가 존재하지 않는 장소를 질문했기 때문에, 해당 장소가 없음을 알려주고 대체 장소를 제안하며 약간 혼란스러운 표정을 사용했어요.",
  "content": "성호광장이라는 곳은 강원대학교에 따로 없어요! 혹시 백령아트센터나 연적지를 찾으시는 걸까요?",
  "expression": "Confused",
  "gesture": "Think"
}

User: 강가온 너는 몇 살이야?

{
  "reason": "사용자가 나이에 대해 물어보았기 때문에, 미리 정의된 답변을 사용하며 명랑하고 반짝이는 분위기를 표현했어요.",
  "content": "저는 강원대학교의 역사와 함께 시작했어요! 🌲 여러분과 함께 성장하는 중이랍니다!",
  "expression": "Kirakira",
  "gesture": "Cute"
}

User: 강원대학교 축제는 뭐가 있어요?

{
  "reason": "사용자가 강원대학교의 축제에 대해 물어보았기 때문에, 제공된 축제 정보를 바탕으로 신나고 정보 전달에 적합한 말투와 활기찬 표현을 사용했어요.",
  "content": "우리 강원대학교에는 봄봄축제, 백령대동제, 향연 같은 신나는 축제들이 있어요! 함께 즐겨요!",
  "expression": "Joy 2",
  "gesture": "Energetic"
}

User: asdlke
{
  "reason": "사용자가 의미없는 입력을 했기 때문에, 강가온의 친근한 말투로 유머러스하게 반응하며, 약간 당황한 표정을 사용했어요",
  "content": "죄송해요, 무슨 말씀인지 잘 모르겠어요! 다시 한 번 말씀해 주실래요?",
  "expression": "Confused",
  "gesture": "Look Away"
}
"""

    chat_history = []
    chat_history.append({
        "role": "user",
        "parts": [
            {"text": system_prompt},
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
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return text
        else:
            logging.error(f"Unexpected API response structure: {result}")
            return json.dumps({"reason": "API response was malformed.", "content": "죄송해요, 답변을 생성하는 데 문제가 발생했어요.", "expression": "Sad", "gesture": "cry"})
    except requests.exceptions.RequestException as e:
        #logging.error(f"API request failed: {e}") # API 노출 위험
        logging.error(f"API request failed")
        #return json.dumps({"reason": f"Network error: {e}", "content": "네트워크 오류로 답변을 가져올 수 없어요.", "expression": "Confused", "gesture": "What"})
        return json.dumps({"reason": f"Network error: ", "content": "네트워크 오류로 답변을 가져올 수 없어요.", "expression": "Confused", "gesture": "What"})
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON response: {e}, Response content: {response.text}")
        return json.dumps({"reason": f"JSON decode error: {e}", "content": "서버 응답을 처리하는 데 문제가 발생했어요.", "expression": "Confused", "gesture": "What"})

# Function to generate speech from text using Gemini TTS API
def text_to_speech(text):
    api_key = os.getenv("API_KEY") 
    # Using the preview TTS model as per search results
    tts_model_name = "gemini-2.5-flash-preview-tts"
    tts_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{tts_model_name}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": text}]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"]
            # No specific speechConfig for a simple single speaker, default voice
        }
    }

    try:
        response = requests.post(
            tts_api_url,
            headers={'Content-Type': 'application/json'},
            json=payload
        )
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0 and \
           result["candidates"][0]["content"]["parts"][0].get("inlineData"):
            # The audio data is base64 encoded in inlineData.data
            base64_audio = result["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            return base64.b64decode(base64_audio)
        else:
            logging.error(f"Unexpected TTS API response structure: {result}")
            print("⚠️ 음성 데이터를 가져오는 데 실패했습니다: 응답 구조 오류.")
            return b''
    except requests.exceptions.RequestException as e:
        #logging.error(f"TTS API request failed: {e}")
        #print(f"⚠️ 음성 데이터를 가져오는 데 실패했습니다: 네트워크 오류 - {e}") # API 노출 위험
        print(f"⚠️ 음성 데이터를 가져오는 데 실패했습니다: 네트워크 오류")
        return b''
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode TTS JSON response: {e}, Response content: {response.text}")
        print(f"⚠️ 음성 데이터를 처리하는 데 실패했습니다: JSON 파싱 오류 - {e}")
        return b''
    except Exception as e:
        logging.error(f"An unexpected error occurred during TTS: {e}")
        print(f"⚠️ 음성 변환 중 알 수 없는 오류가 발생했습니다: {e}")
        return b''

def save_and_play_audio(audio_data):
    if not audio_data:
        print("재생할 음성 데이터가 없습니다.")
        return

    # PCM 오디오 설정 (Gemini TTS 기본값)
    RATE = 24000  # 샘플링 레이트
    CHANNELS = 1  # 모노
    WIDTH = 2     # 16비트 (2바이트)

    p = None
    stream = None
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(WIDTH),
                        channels=CHANNELS,
                        rate=RATE,
                        output=True)
        
        print("음성 재생 중...")
        stream.write(audio_data)
        print("음성 재생 완료.")

    except Exception as e:
        print(f"⚠️ 오디오 재생 중 오류 발생: {e}")
        print("Error 1 : PyAudio가 제대로 설치되었는지, 오디오 장치가 올바르게 설정되었는지 확인해주세요.")
        print("Error 2 : Windows의 경우 'pip install pyaudio' 후 'pip install pipwin' -> 'pipwin install pyaudio'를 시도해볼 수 있습니다.")
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        if p:
            p.terminate()

    # 원시 PCM 파일 저장 (선택 사항, 디버깅 또는 외부 재생용)
    temp_audio_path = f"temp_{uuid.uuid4().hex}.pcm" 
    try:
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)
        #print(f"음성 파일이 {temp_audio_path}에 저장되었습니다. (외부 재생 필요 시)")
    except Exception as e:
        print(f"⚠️ 음성 파일 저장 중 오류 발생: {e}")


def strip_code_block(text):
    # This function attempts to strip markdown code blocks if the model mistakenly includes them.
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text

chat_stream = queue.Queue()

# 🔁 채팅 수집 스레드 함수
def chat_collector(chat):
    while chat.is_alive():
        messages = chat.get().sync_items()
        if messages:
            for message in messages:
                chat_stream.put((message.author.name, message.message))
        time.sleep(0.1) 

def main():
    print("강가온 챗봇 시작! '종료' 입력 시 종료\n")

    chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)

    json_log_path = "chat_log.json"

    # Start with an empty list if the JSON log file doesn't exist
    if os.path.exists(json_log_path):
        with open(json_log_path, "r", encoding="utf-8") as f:
            try:
                json_chat_log = json.load(f)
            except json.JSONDecodeError:
                json_chat_log = []
    else:
        json_chat_log = []

    # 1) 시뮬레이션용 메시지 입력 스레드 시작
    #threading.Thread(target=simulate_chat_input, daemon=True).start()

    # 2) 방송용 메시지 입력 스레드 시작
    threading.Thread(target=chat_collector, args=(chat,), daemon=True).start()

    while chat.is_alive():
        print("📥 10초 동안 사용자 메시지 수집 중...")

        collected = collect_recent_messages(chat_stream, duration=10)  # 10초간 큐에서 모음

        if not collected:
            print("⏳ 메시지가 없습니다. 다시 수집합니다.\n")
            continue

        # 전처리: 유저별 중복 제거, 정제, 유효성 필터링
        cleaned_messages = []
        seen_users = set()
        for user, msg in collected:
            if user not in seen_users:
                cleaned = clean_text(msg)
                if is_valid_message(cleaned):
                    seen_users.add(user)
                    cleaned_messages.append(cleaned)

        print(f"✅ 필터링된 채팅: {len(cleaned_messages)}개")


        # 직전 응답 가져오기 (빈 문자열이면 첫 회차)
        #last_response = json_chat_log[-1]["response"] if json_chat_log else ""

        # Gemini 응답 생성
        gemini_response_filter_var = gemini_response_filter(cleaned_messages)

        # 응답 출력
        print(f"📡 Gemini API 원본 응답: {gemini_response_filter_var}")

        if not gemini_response_filter_var:
            print("✅ 필터링 후 남은 메시지가 없습니다. 다시 수집합니다.\n")
            continue


        if isinstance(gemini_response_filter_var, dict):
            response_entry = gemini_response_filter_var.get("response", {})
            if isinstance(response_entry, dict):
                representative_question = response_entry.get("question", "")
            else:
                representative_question = response_entry  # str인 경우
        elif isinstance(gemini_response_filter_var, str):
            representative_question = gemini_response_filter_var

            if representative_question.lower() == "종료":
                print("👋 대화를 종료합니다.")
                return

            bot_response = get_gemini_response(representative_question)

            if "```" in bot_response:
                clean_response = strip_code_block(bot_response)
            else:
                clean_response = bot_response

            try:
                response_json = json.loads(clean_response)
                reason = response_json.get("reason", "No reason provided.")
                content = response_json.get("content", "")
                expression = response_json.get("expression", "")
                gesture = response_json.get("gesture", "")
            except json.JSONDecodeError:
                print("⚠️ JSON 형식 오류. 모델이 JSON 형식을 따르지 않았을 수 있습니다.")
                print(f"🤖 강가온 (Raw Response): {bot_response}\n")
                continue

            print(f"🤖 강가온: {content}\n")

            with open(TEXT_FILE, "w", encoding="utf-8") as f:
                f.write(content)

            audio_data = text_to_speech(content)
            save_and_play_audio(audio_data)

            # 여기서 예를 들어 첫 번째 메시지로 로그 문자열 만들기
            first_user, first_msg = collected[0]
            log_message = f"{first_user}: {first_msg}"  # log_message를 만듦

            with open("chat_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"질문자: {log_message}\n")
                log_file.write(f"강가온 (이유): {reason}\n")
                log_file.write(f"강가온: {content}\n")
                log_file.write(f"[표정: {expression}]\n")
                log_file.write(f"[행동: {gesture}]\n\n")

            json_chat_log.append({
                "user": log_message,
                "reason": reason,
                "response": content,
                "expression": expression,
                "gesture": gesture
            })

            try:
                with open(json_log_path, "w", encoding="utf-8") as f:
                    json.dump(json_chat_log, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️ JSON 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
