import time
from queue import Queue
from typing import List
import re
import requests
import json
from typing import List
from dotenv import load_dotenv
import os

# .env 파일의 내용을 환경 변수로 불러옴
load_dotenv()


def collect_recent_messages(chat_stream: Queue, duration: int = 10) -> List[tuple]:
    print("📥 채팅 수집 중... (10초)")
    collected = []
    start = time.time()
    while time.time() - start < duration:
        try:
            message = chat_stream.get(timeout=1)
            if isinstance(message, tuple) and len(message) == 2:
                collected.append(message)  # (user, msg)
        except:
            continue
    return collected


#다국어 입력 대응
# def translate_to_korean(text: str) -> str:
#     url = f"https://translation.googleapis.com/language/translate/v2"
#     params = {
#         "q": text,
#         "target": "ko",
#         "format": "text",
#         "key": "YOUR_GOOGLE_TRANSLATE_API_KEY"
#     }
#     resp = requests.post(url, data=params)
#     return resp.json()['data']['translations'][0]['translatedText']


#길이 제한 감탄사도 짜름
def is_valid_message(message: str) -> bool:
    message = message.strip()
    if not message:
        return False
    if len(message) > 100:
        return False
    if message.lower() in ["ㅋㅋ", "ㅎ", "헐", "와", "오", "음", "응", "하", "에이", "헉"]:
        return False
    return True

#이모티콘/특수문자 제거 + 텍스트 정제
def clean_text(message: str) -> str:
    message = re.sub(r'[^\w\s가-힣]', '', message)  # 이모티콘/특수문자 제거
    return message.strip()

#동일 질문자 중복 제거 (현재 안쓰고있음)
def filter_by_unique_users(messages: List[tuple]) -> List[str]:
    seen_users = set()
    results = []
    for user, msg in messages:
        if user not in seen_users and is_valid_message(msg):
            seen_users.add(user)
            results.append((user, msg))
    return results


#이전 응답과 관련성 높은 질문 우선 (현재 안쓰고있음)
def relevance_score(message: str, last_bot_response: str) -> float:
    msg_words = set(message.lower().split())
    bot_words = set(last_bot_response.lower().split())
    if not bot_words: return 0.0
    return len(msg_words & bot_words) / len(bot_words)

# ▶ Gemini API 요청 함수 (응답 JSON 형식 유지)
def gemini_response_filter(final_messages: List[str]) -> dict:
    """
    Gemini API에 사용자 질문 리스트를 보내서 JSON 형식 응답을 받는 함수.
    """

    # 1) 질문들을 문자열로 연결 (API 프롬프트용)
    prompt = "다음은 사용자들의 질문 리스트야. 대표적인 1개의 질문을 뽑아줘(반드시 한국어로 대답할 것):\n"
    for i, msg in enumerate(final_messages):
        prompt += f"{i+1}. {msg}\n"

    # 2) Gemini API endpoint와 API 키 (본인 API 키로 교체)
    api_key = os.getenv("API_KEY")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    # 3) 요청 페이로드 구성 (system prompt + user message)
    system_prompt = """
You can analyze different messages sent by users,
It plays the role of picking only one representative question.

Be sure to follow the styles and criteria below:

1. Please pick me a smiley tone or expression of empathy only occasionally. Examples: "LOL," "That's right, that's right."
2. If you have many similar questions, please summarize them into one and choose a representative question.
3. If the questions are different on different topics, please choose the most interesting or conversational ones.
- If more than one flow is important, you can add one representative question + the rest in parentheses.
4. If you have a lot of abusive messages, please choose a sentence with 'intention or question' in it as well.
- If abusive/expletive accounts for a certain percentage of all messages (e.g., 30% or more),
→ Include abusive messages in the list of candidates for representative questions.

- It can be ruled out if you repeat simple swear words,
→ If certain topics (complaints, protests, taunts, etc.) are included with swear words, this is considered to be the intent of the question.

- Example:
"Why are you acting so stupid?" → "Why did AI make a mistake?" can be paraphrased
"Who wants that answer?" → "What is the accuracy or standard of the answer?"

- If you only have a simple anger-resolving message ("ㅅㅂ", "Why not"):
→ Consider no direct questions and can be ignored
5. Please remove emoticons and special characters.

Below is an example of input and output. Please refer to it and answer in a similar way.

[Example 1]
Enter:
- What should I eat for lunch
- How's the weather today
- Please recommend me a lunch menu

Output:
"What should I have for lunch?"

[Example 2]
Enter:
- Are you an AI?
- When did it come out?
- How do you make your voice sound?

Output:
"How do you make your voice sound?"

[Example 3]
Enter:
- I'm so mad
- What is this
- It's annoying, so let me ask you a question, how does the YouTube algorithm work?

Output:
"How does the YouTube algorithm work?"

[Example 4]
Enter:
- Can I have a cat?
- What should I eat for lunch today?
- How much water should I drink a day?

Output:
"Can I have a cat?" (For your information, there was also a question about lunch or water intake today.)

---
When the list of questions comes in, please refer to the above criteria and examples and print out a representative question
"""

    chat_history = [
        {
            "role": "user",
            "parts": [
                {"text": system_prompt},
                {"text": prompt}
            ]
        }
    ]

    payload = {
        "contents": chat_history
    }

    # 4) API 요청 보내기
    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=15  # 타임아웃 지정
        )
        response.raise_for_status()
        result = response.json()

        # 5) 응답에서 텍스트 추출
        candidates = result.get("candidates", [])
        if candidates and "content" in candidates[0]:
            content_parts = candidates[0]["content"].get("parts", [])
            if content_parts:
                text = content_parts[0].get("text", "")
                # text가 JSON 문자열 형태면 파싱 시도
                try:
                    parsed = json.loads(text)
                    return parsed
                except json.JSONDecodeError:
                    # JSON이 아니면 그냥 텍스트를 response 필드에 넣어서 반환
                    return {
                        "type": "chat",
                        "summary": "사용자 질문들을 요약한 응답입니다.",
                        "response": text,
                        "messages": final_messages
                    }
        # 이상할 경우 예외 처리
        return {
            "type": "error",
            "summary": "API 응답 형식이 예상과 다름",
            "response": "",
            "messages": final_messages
        }

    except requests.exceptions.RequestException as e:
        # 네트워크 오류 등 예외 처리
        return {
            "type": "error",
            "summary": f"API 요청 실패: {e}",
            "response": "",
            "messages": final_messages
        }


