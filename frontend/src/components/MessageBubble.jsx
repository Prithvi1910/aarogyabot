import React from 'react'
import { Volume2, Square, BookOpen } from 'lucide-react'

function MessageBubble({ role, text, image, sources, showSpeak, isSpeaking, onSpeak }) {
  const isBot = role === 'bot'

  return (
    <div className={`flex w-full items-end gap-2 message-fade ${isBot ? 'justify-start' : 'justify-end'}`}>
      {/* Bot avatar */}
      {isBot && (
        <div
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-brand-700 text-xs font-bold text-white shadow-sm"
          aria-hidden="true"
        >
          A
        </div>
      )}

      <div
        className={`max-w-[82%] whitespace-pre-wrap break-words p-3.5 text-[15px] leading-[1.55] ${
          isBot
            ? 'rounded-2xl rounded-bl-md bg-white text-ink-900 shadow-soft ring-1 ring-brand-100/70'
            : 'rounded-2xl rounded-br-md bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-glow'
        }`}
      >
        {/* Attached photo (visual symptom checker) */}
        {image && (
          <img
            src={image}
            alt="Shared health photo"
            className={`max-h-52 w-auto rounded-xl object-cover ${text ? 'mb-2' : ''}`}
          />
        )}
        {text}

        {/* Source citations — grounds the answer in the health docs */}
        {isBot && sources && sources.length > 0 && (
          <div className="mt-2.5 flex flex-wrap items-center gap-1.5 border-t border-brand-100/80 pt-2">
            <span className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide text-ink-500">
              <BookOpen className="h-3 w-3" aria-hidden="true" />
              Sources
            </span>
            {sources.map((s) => (
              <span
                key={s}
                className="rounded-full bg-brand-50 px-2 py-0.5 text-[11px] font-medium text-brand-700"
              >
                {s}
              </span>
            ))}
          </div>
        )}

        {/* Read aloud (text-to-speech) control for bot replies */}
        {isBot && showSpeak && text && (
          <button
            type="button"
            onClick={onSpeak}
            className={`mt-2.5 flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-brand-300 ${
              isSpeaking
                ? 'bg-brand-600 text-white'
                : 'bg-brand-50 text-brand-700 hover:bg-brand-100'
            }`}
            aria-label={isSpeaking ? 'Stop reading aloud' : 'Read this answer aloud'}
          >
            {isSpeaking ? (
              <>
                <Square className="h-3 w-3 fill-current" aria-hidden="true" />
                Stop
              </>
            ) : (
              <>
                <Volume2 className="h-3.5 w-3.5" aria-hidden="true" />
                Listen
              </>
            )}
          </button>
        )}
      </div>
    </div>
  )
}

export default MessageBubble
