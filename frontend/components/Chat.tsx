
// 「入力欄にメッセージを打ってボタンを押すと、FastAPIに送信されて、返答が画面に表示される chat UI」

"use client";

import {useState} from "react";

export default function Chat() {
    const [input, setInput] = useState("");    // 入力欄の値を管理
    const [messages, setMessages] = useState<{ sender: string; text: string}[]>([]);    // メッセージの履歴を管理
    const [loading, setLoading] = useState(false);    // ローディング状態を管理

    const sendMessage = async () => {
        if (!input.trim()) return;    // 入力欄が空の場合は何もしない

        const userMessage = { sender: "You", text: input};    // ユーザーのメッセージを追加
        setMessages((prev) => [...prev, userMessage]);    // メッセージ履歴に追加
        setLoading(true);    // ローディング状態をtrueにする

        console.log("送信ボタンが押されたよ！");
        console.log("input:", input);

        try {
            // fetch(...)：ネットワークリクエストを送信する関数(APIへリクエストを送信する。JavaScriptの標準関数。)   
            const res = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: input}),
            });

            const data = await res.json();
            const botMessage = { sender: "WineBot", text: data.reply || data.error || "エラーが発生しました。"};
            setMessages((prev) => [...prev, botMessage]);
        } catch (error) {
            setMessages((prev) => [...prev, {sender: "WineBot", text: "通信エラーが発生しました。"}]);
        }

        setInput("");
        setLoading(false);
    };

    // 表示する画面の中身を定義（HTMLっぽいけど、JSXという記法）
    return (
        <div className="max-w-xl mx-auto p-4">
          <h1 className="text-2xl font-bold mb-4">🍷 WineChatBot</h1>
    
          <div className="space-y-2 mb-4 h-64 overflow-y-auto border p-2 rounded">
            {messages.map((msg, index) => (
              <div key={index} className={msg.sender === "You" ? "text-right" : "text-left"}>
                <span className="font-semibold">{msg.sender}:</span> {msg.text}
              </div>
            ))}
            {loading && <div className="text-gray-500">WineBot: 考え中...</div>}
          </div>
    
          <div className="flex gap-2">
            {/* 入力欄 */}
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="ワインについて聞いてみよう！"
              className="flex-grow border p-2 rounded"
            />
            {/* 送信ボタン */}
            <button
              onClick={sendMessage}
              className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
            >
              送信
            </button>
          </div>
        </div>
      );
}
