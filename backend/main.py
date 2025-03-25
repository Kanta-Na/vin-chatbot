# ワインチャットボットのメインプログラム
# 2025/03/24 「最小構成の ChatBot」を作成
# 2025/03/25 「GUIで動く chatbot」を作成

# 必要なライブラリのインポート
import os
import openai
import base64
from dotenv import load_dotenv
from PIL import Image
from openai import OpenAI

# .envファイルから環境変数、APIキーを読み込む
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# OpenAIクライアントを初期化
client = OpenAI()

# 画像をBase64でエンコードする関数を定義
def encode_image(image_path):
    """画像をBase64でエンコードする"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    
# チャット関数を定義
def chat():
    print("🍷 WineChatBot 起動！画像にも対応しています！")
    print("終了したい場合は 'exit' と入力してください。\n")

    while True:
        user_input = input("あなた: ")
        if user_input.lower() in ["exit", "quit"]:
            print("WineChatBot: A plus tard!👋（ばいばい👋）")
            break

        send_image = input("画像も一緒に送りますか？（y/n）: ").strip().lower()
        messages = [
            {"role": "system", "content": "あなたはワインに詳しいソムリエAIです。"}
        ]

        if send_image == "y":
            image_path = input("画像ファイルのパスを入力してください（例: ./image.jpg）: ").strip()
            if not os.path.isfile(image_path):
                print("画像ファイルが見つかりませんでした。テキストのみで進めます。")
            else:
                base64_image = encode_image(image_path)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_input},
                        {
                            "type": "input_image",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                })
        else:
            messages.append({"role": "user", "content": user_input})

        try:
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
            bot_reply = completion.choices[0].message.content.strip()
            print(f"\nWineChatBot: {bot_reply}\n")

        except Exception as e:
            print(f"[エラー] {e}")
    
if __name__ == "__main__":
    chat()
