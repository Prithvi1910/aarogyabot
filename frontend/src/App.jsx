import React, { useState } from 'react'
import LandingPage from './components/LandingPage'
import ChatInterface from './components/ChatInterface'

function App() {
  const [started, setStarted] = useState(false)

  if (!started) {
    return <LandingPage onStart={() => setStarted(true)} />
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-0 sm:p-4">
      <div className="w-full sm:max-w-md h-screen sm:h-[700px] bg-white sm:rounded-2xl sm:shadow-2xl overflow-hidden flex flex-col">
        <ChatInterface />
      </div>
    </div>
  )
}

export default App
