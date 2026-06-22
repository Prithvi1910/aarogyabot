import React from 'react'

function MessageBubble({ role, text }) {
  const isBot = role === 'bot'
  
  return (
    <div className={`flex w-full ${isBot ? 'justify-start' : 'justify-end'}`}>
      <div
        className={`rounded-2xl max-w-[80%] p-[12px] text-[15px] leading-[1.5] shadow-sm break-words ${
          isBot
            ? 'bg-white text-gray-800 border border-gray-200'
            : 'bg-[#16a34a] text-white'
        }`}
      >
        {text}
      </div>
    </div>
  )
}

export default MessageBubble
