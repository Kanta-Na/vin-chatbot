
// frontend/app/layout.tsx
// 「ページ全体のレイアウトを定義するファイル」

import './globals.css'
import { ReactNode } from 'react'

export const metadata = {
  title: 'WineChatBot',
  description: 'ワイン好きのためのGPTチャットボット',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  )
}
