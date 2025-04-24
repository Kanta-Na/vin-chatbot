
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

load_dotenv()
client = OpenAI()

app = FastAPI()

# CORS対応（ローカルのフロントエンドと連携するため）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vin-chatbot.vercel.app/",
        "https://vin-chatbot.vercel.app",
        "http://localhost:3000",
    ],    # フロントエンド（Vercel）のURLだけ許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 画像をBase64でエンコードする関数
def encode_image(image_path: str) -> str:
    """画像をBase64でエンコードする"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    
# チャットAPI
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    image_data_url = data.get("image") 

    messages = [
        {"role": "system", "content":"あなたはワインに詳しいソムリエAIです。"},
        {"role": "system", "content":"Markdown形式で回答してください。"},
        {"role": "system", "content":"ユーザーのワイン情報をもとに最適な音楽プレイリストをSpotifyから選び、必ず https://open.spotify.com/... 形式のURLを返してください。"},
    ]

    # 画像が送られてきた場合は、image_url として追加
    # 後に、ドラックアンドドロップで画像を張り付けることができるようにする。
    if image_data_url:
        messages.append({
            "role": "user",
            "content": [
                {"type": "input_text", "text": user_input},
                {
                    "type": "input_image",
                    "image_url": {
                        "url": image_data_url,
                    }
                }
            ]
        })
    else:
        messages.append({"role": "user", "content": user_input})

    print("🔄 これからユーザー入力に応じたリクエストを送信します...")
    print(f"ユーザーの入力: {user_input}")
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        bot_reply = completion.choices[0].message.content.strip()
        print("✅ GPT からレスポンスをもらいました。")
        print(f"GPT からのレスポンス: {completion}")
        print("🔄 Chat.tsx にレスポンスを返します...")
        print(bot_reply)
        return {"reply": bot_reply}

    except Exception as e:
        return {"error": str(e)}


# ルートパスのテスト
@app.get("/")
def root():
    return {"message": "WineChatBot API is running!"}
