from dotenv import load_dotenv
import os

# .env 파일의 내용을 환경 변수로 불러옴
load_dotenv()

# 환경 변수 사용
api_key = os.getenv("API_KEY")
print(api_key)