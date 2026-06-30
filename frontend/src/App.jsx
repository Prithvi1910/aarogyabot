import React, { useState } from 'react'
import LandingPage from './components/LandingPage'
import ChatInterface from './components/ChatInterface'

function App() {
  const [started, setStarted] = useState(false)

  if (!started) {
    return <LandingPage onStart={() => setStarted(true)} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#eef5f4] via-[#e6f1f0] to-[#dbeceb] flex items-center justify-center p-0 sm:p-6">
      <div className="w-full sm:max-w-[420px] h-[100dvh] sm:h-[760px] bg-white sm:rounded-[2rem] sm:shadow-frame overflow-hidden flex flex-col sm:ring-1 sm:ring-black/5">
        <ChatInterface />
      </div>
    </div>
  )
}

export default App
