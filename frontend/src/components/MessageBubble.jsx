import React from 'react'

function MessageBubble({ role, text }) {
  const isBot = role === 'bot'

  return (
    <div className={`flex w-full items-end gap-2 message-fade ${isBot ? 'justify-start' : 'justify-end'}`}>
      {/* Bot avatar */}
      {isBot && (
        <div
          className="flex-shrink-0 w-7 h-7 rounded-full bg-green-600 flex items-center justify-center text-white text-xs font-bold shadow-sm"
          aria-hidden="true"
        >
          A
        </div>
      )}

      <div
        className={`rounded-2xl max-w-[80%] p-[12px] text-[15px] leading-[1.5] shadow-sm break-words whitespace-pre-wrap ${
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
