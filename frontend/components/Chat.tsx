
// 「入力欄にメッセージを打ってボタンを押すと、FastAPIに送信されて、返答が画面に表示される chat UI」

"use client";

import {useState} from "react";
import ReactMarkdown from "react-markdown";    // Markdown描画のため追加

export default function Chat() {
    /*
    フロントエンドのロジックとデータ部分。
    const によって、useState で管理される変数（input, messages, loading）を定義し、
    sendMessage 関数で、ユーザーのメッセージを送信して、返答を受け取ることを定義。
    */
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

    // Enterキーを押したときの処理
    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();    // 改行せずに送信
        sendMessage();
      }
    }

    // 表示する画面の中身を定義（HTMLっぽいけど、JSXという記法）（UIの部分）
    return (
        <div className="h-screen flex flex-col max-w-3xl mx-auto p-4">

          {/* "className" は Tailwind CSS のユーティリティクラスである。*/}
          {/* ユーティリティクラスは、クラス名を指定するだけで、スタイルを適用できる。*/}
          {/*例えば、max-w-xlは、最大幅をxlに設定するという意味。*/}
          {/*mx-autoは、左右のマージンを自動で設定するという意味。*/}
          {/*p-4は、パディングを4pxに設定するという意味。*/}

          <h1 className="text-3xl font-bold mb-4">🍷 WineChatBot</h1>
    
          <div className="flex-1 overflow-y-auto border p-4 rounded mb-4 bg-gray-50">
            {messages.map((msg, index) => (
              <div key={index} className={`mb-3 p-3 rounded ${msg.sender === "You" ? "text-right bg-white" : "text-left bg-blue-100"}`}>
                <div className="font-semibold mb-1">{msg.sender}:</div>
                <div className="prose prose-sm whitespace-pre-wrap">
                  {/* GPT-4o 出力の Markdown に対応 */}
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </div>
              </div>
            ))}
            {loading && <div className="text-gray-500">WineBot: 考え中...</div>}
          </div>
    
          <div className="flex gap-2">
            {/* 入力欄 （自動リサイズするテキストエリア）*/}
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="ワインについて聞いてみよう！（Shift+Enterで改行）"
              className="flex-grow border p-2 rounded resize-none"
              rows={2}
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
