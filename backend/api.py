
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai, base64, os, requests, time, json, certifi
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from urllib.parse import urlencode

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

# Spotify Web API Class
class SpotifyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_url = "https://accounts.spotify.com/api/token"
        self.base_url = "https://api.spotify.com/v1/"
        
    def get_token(self):
        """アクセストークンを取得する"""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials"}
        result = requests.post(self.token_url, headers=headers, data=data)
        json_result = json.loads(result.content)
        self.token = json_result["access_token"]
        return self.token
    
    def get_auth_header(self):
        """認証ヘッダーを生成する"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def search(self, query, search_type="album,playlist", limit=10):
        """キーワードに基づいてアルバムやプレイリストを検索する"""
        if not self.token:
            self.get_token()
            
        headers = self.get_auth_header()
        query_params = urlencode({
            "q": query,
            "type": search_type,
            "limit": limit
        })
        
        query_url = f"{self.base_url}search?{query_params}"
        result = requests.get(query_url, headers=headers)
        json_result = json.loads(result.content)
        return json_result
    
    def get_embed_urls(self, query, search_type="album,playlist", limit=5):
        """検索結果から埋め込みURLを生成する"""
        search_results = self.search(query, search_type, limit)
        embed_urls = []
        
        # アルバムの埋め込みURL
        if "albums" in search_results:
            for album in search_results["albums"]["items"]:
                album_id = album["id"]
                embed_url = f"https://open.spotify.com/embed/album/{album_id}"
                embed_urls.append({
                    "type": "album",
                    "name": album["name"],
                    "artists": [artist["name"] for artist in album["artists"]],
                    "embed_url": embed_url
                })
        
        # プレイリストの埋め込みURL
        if "playlists" in search_results:
            for playlist in search_results["playlists"]["items"]:
                playlist_id = playlist["id"]
                embed_url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
                embed_urls.append({
                    "type": "playlist",
                    "name": playlist["name"],
                    "owner": playlist["owner"]["display_name"],
                    "embed_url": embed_url
                })
        
        return embed_urls
    
spotify_api = SpotifyAPI(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
)

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
            # トークンがない場合は取得
            if not spotify_api.token:
                spotify_api.get_token()
            
            # プレイリストのみを検索
            search_results = spotify_api.search(
                query=search_term, 
                search_type="playlist", 
                limit=1
            )
            
            # 検索結果からプレイリストを取得
            playlists = search_results.get("playlists", {}).get("items", [])
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


# ルートパスのテスト
@app.get("/")
def root():
    return {"message": "WineChatBot API is running!"}
