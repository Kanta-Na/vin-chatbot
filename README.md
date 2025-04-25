
# Wine ChatBot

---

## 【概要】

**WineChatBot** は、ワインに関する質問をすると、そのワインの背景や特徴について回答してくれると同時に、**そのワインを楽しむシーンにぴったりな音楽も自動でレコメンドしてくれる**AIチャットボットです。
本プロジェクトの目的は、**フロントエンド〜バックエンド〜デプロイまで、アプリ開発の一連の流れを実践的に学ぶこと**です。

---

## 📽 デモ動画


▶️ WineChatBot デモ動画

![WineChatBot デモ動画](source/demo.mp4)

---

## 【技術スタック】

| カテゴリ | 使用技術・サービス |
| --- | --- |
| **フロントエンド** | Next.js（React + TypeScript）、Tailwind CSS |
| **バックエンド** | FastAPI、OpenAI API（GPT-4o） |
| **音楽レコメンド** | Spotify Web API（埋め込み対応） |
| **デプロイ** | Vercel（フロント）、Render（バックエンド） |
| **その他** | `.env` 管理、CORS設定、REST通信、JSONパース、Markdownレンダリング、ローディング制御など |

---

## 【デプロイ先】
* フロントエンド：[Vercel](https://vercel.com/)
* バックエンド：[Render](https://dashboard.render.com/)

---

## 【主な機能】

- GPT-4oを用いた**自然な会話型ワインアドバイザー**
- 入力されたワイン名や趣向から、**最適なSpotify音楽プレイリストを提案**
- Markdown形式によるわかりやすい出力
- **ブラウザで利用可能なGUIチャットインターフェース**
