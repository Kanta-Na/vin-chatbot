
# ChatBot - Backend (FastAPI)

このディレクトリは、WineChatBotのバックエンド機能を提供しています。主に以下の機能を担っています。

- OpenAI GPT-4.1-nano によるワイン関連の質問応答
- ユーザーからのPOSTリクエストを受け取り、OpenAIに転送
- SpotifyのプレイリストURL抽出に対応
- CORS設定により、信頼できるURLからのアクセスのみ許可

## デプロイ先

このFastAPIバックエンドは [Render](https://dashboard.render.com/) を使用してクラウド上にホストされています。

## 起動方法（ローカル）

```bash
cd backend
.venv\Scripts\activate
uvicorn api:app --reload
```
