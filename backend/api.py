from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai, base64, os, requests, time, json
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

# Spotify API
SPOTIFY_TOKEN_CACHE = {"token": None, "exp": 0}

def get_spotify_token():
    if SPOTIFY_TOKEN_CACHE["token"] and SPOTIFY_TOKEN_CACHE["exp"] > time.time():
        return SPOTIFY_TOKEN_CACHE["token"]
    
    auth = f"{os.getenv('SPOTIFY_CLIENT_ID')}:{os.getenv('SPOTIFY_CLIENT_SECRET')}"
    headers = {"Authorization": "Basic" + base64.b64encode(auth.encode()).decode()}
    data = {"grant_type": "client_credentials"}
    r = requests.post("https://accounts.apotify.com/api/token", headers=headers, data=data)
    token = r.json()["access_token"]
    SPOTIFY_TOKEN_CACHE["token"] = token
    SPOTIFY_TOKEN_CACHE["exp"] = time.time() + 3300    # 55分キャッシュ(有効期限)
    return token

# 画像をBase64でエンコードする関数
def encode_image(image_path: str) -> str:
    """画像をBase64でエンコードする"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# チャットAPI (20250424)
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    image_data_url = data.get("image")

    # GPTへ送るメッセージ校正
    messages = [
        {"role": "system", "content": "あなたはワインに詳しいソムリエAIです。"},
        {"role": "system", "content": "入力されたキーワードに関連する音楽(歌手もしくはプレイリスト)を調べてください。"},
        {"role": "system", "content": "Spotifyの検索用に、音楽のジャンル、キーワード、またはプレイリスト検索ワードを1つだけjson形式で提案してください。"},
        {"role": "system", "content": "形式例：{\"query\": \"French Cafe Jazz\"}"},
    ]

    # 画像入力付き or テキストのみ
    if image_data_url:
        messages.append({
            "role": "user",
            "content": [
                {"type": "input_text", "text": user_input},
                {"type": "input_image", "image_url": {"url": image_data_url}},
            ]
        })
    else:
        messages.append({"role": "user", "content": user_input})
    
    # Step1: gpt に検索用ワードを依頼
    try:
        print("---GPTに検索用キーワードを問い合わせます…---")
        search_resp = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages
        )
        gpt_search_json = search_resp.choices[0].message.content.strip()
        print(f"☆☆☆ gpt-4.1-nano の出力: {gpt_search_json}")
        search_obj = json.loads(gpt_search_json)
        search_term = search_obj["query"]
        print(f"✅ 取得された Spotify検索ワード: {search_term} ---")
    except Exception as e:
        print("☢☢☢ Spotify検索ワード生成に失敗: ", e)
        search_term = None

    # Step2: Spotify からプレイリスト検索
    spotify_url = None
    if search_term:
        try:
            token = get_spotify_token()
            headers = {"Authorization": f"Bearer {token}"}
            params = {"q": search_term, "type": "playlist", "limit": 1}
            r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
            playlists = r.json().get("playlists", {}).get("items", [])
            if playlists:
                playlist_id = playlists[0]["id"]
                spotify_url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
                print(f"✅ Spotify プレイリスト取得成功: {spotify_url}")
        except Exception as e:
            print("☢☢☢ Spotify API 取得失敗: ", e)
    
    # Step3: 通常のワインに関するGPT回答
    try:
        print(" Wine についてGPTへ質問を送信中………")
        wine_resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "あなたはワインに詳しいソムリエAIです。"},
                {"role": "system", "content": "Markdown形式で回答してください。"},
                {"role": "system", "content": user_input},
            ]
        )
        wine_reply = wine_resp.choices[0].message.content.strip()
        print("✅ GPTからワインの回答の取得に成功")
        print(f"----------\n{wine_reply}\n----------")
        
        return {
            "reply": wine_reply,
            "spotify_url": spotify_url,
        }
    except Exception as e:
        return {"error": str(e)}


# (旧)チャットAPI
"""
@app.post("/chat_old")
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
"""

# ルートパスのテスト
@app.get("/")
def root():
    return {"message": "WineChatBot API is running!"}
