import React, { useState, useEffect, useRef } from 'react'
import { Heart, Send, Mic, MicOff } from 'lucide-react'
import MessageBubble from './MessageBubble'
import TriageCard from './TriageCard'
import FacilityCard from './FacilityCard'
import QuickReplies from './QuickReplies'

const LANGUAGES = [
  { name: 'Hindi', code: 'hi-IN' },
  { name: 'English', code: 'en-US' },
  { name: 'Gujarati', code: 'gu-IN' },
  { name: 'Tamil', code: 'ta-IN' },
  { name: 'Telugu', code: 'te-IN' },
  { name: 'Marathi', code: 'mr-IN' }
]

function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'bot',
      text: "Hello! I am AarogyaBot. Ask me about any health concern or send your PIN code to find the nearest health facility. I understand Hindi, Tamil, Telugu, Gujarati and more.",
      triage: null,
      facilities: []
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [showQuickReplies, setShowQuickReplies] = useState(true)
  const messagesEndRef = useRef(null)

  // Speech Recognition State
  const [isSupported, setIsSupported] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [recognitionLanguage, setRecognitionLanguage] = useState('hi-IN')
  const recognitionRef = useRef(null)

  const scrollToBottom = (behavior = 'smooth') => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    messagesEndRef.current?.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : behavior })
  }

  useEffect(() => {
    scrollToBottom('smooth')
  }, [messages, isLoading])

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      setIsSupported(true)
      const rec = new SpeechRecognition()
      rec.continuous = false
      rec.interimResults = false
      rec.lang = recognitionLanguage

      rec.onstart = () => {
        setIsRecording(true)
        setErrorMessage('')
      }

      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        setInputText(prev => (prev ? prev + ' ' + transcript : transcript))
      }

      rec.onerror = (event) => {
        console.error('Speech recognition error:', event)
        if (event.error === 'not-allowed') {
          setErrorMessage('Microphone access denied. Please enable microphone permissions in your browser.')
        } else if (event.error === 'no-speech') {
          setErrorMessage('No speech was detected. Please try again.')
        } else if (event.error === 'audio-capture') {
          setErrorMessage('No microphone was found on your device.')
        } else {
          setErrorMessage(`Speech recognition error: ${event.error}`)
        }
        setIsRecording(false)
      }

      rec.onend = () => {
        setIsRecording(false)
      }

      recognitionRef.current = rec
    }
  }, [])

  // Sync language selection with the SpeechRecognition instance
  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = recognitionLanguage
    }
  }, [recognitionLanguage])

  const toggleRecording = () => {
    if (!isSupported || !recognitionRef.current) return

    if (isRecording) {
      recognitionRef.current.stop()
    } else {
      try {
        setErrorMessage('')
        recognitionRef.current.start()
      } catch (err) {
        console.error('Failed to start speech recognition:', err)
      }
    }
  }

  const sendMessage = async (overrideText = null) => {
    const text = (overrideText && typeof overrideText === 'string') ? overrideText.trim() : inputText.trim()
    if (!text || isLoading) return

    setShowQuickReplies(false)

    // Stop recording if active when sending message
    if (isRecording && recognitionRef.current) {
      recognitionRef.current.stop()
    }

    // Add user message
    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      text
    }
    setMessages(prev => [...prev, userMsg])
    setInputText('')
    setIsLoading(true)

    let useFallback = false
    const botMsgId = `bot-${Date.now()}`

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: text, session_id: sessionId })
      })

      if (!response.ok || !response.body) {
        throw new Error('Streaming failed, using fallback')
      }

      // Add empty bot message that will be updated in real time
      const initialBotMsg = {
        id: botMsgId,
        role: 'bot',
        text: '',
        triage: null,
        facilities: [],
        isStreaming: true
      }
      setMessages(prev => [...prev, initialBotMsg])

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedText = ''
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const cleanedLine = line.trim()
          if (!cleanedLine.startsWith('data: ')) continue
          const dataContent = cleanedLine.slice(6).trim()
          if (!dataContent) continue

          if (dataContent.startsWith('[DONE]')) {
            const jsonStr = dataContent.slice(6)
            try {
              const parsed = JSON.parse(jsonStr)
              if (parsed.session_id && sessionId === null) {
                setSessionId(parsed.session_id)
              }
              setMessages(prev => prev.map(msg => {
                if (msg.id === botMsgId) {
                  return {
                    ...msg,
                    triage: parsed.triage && Object.keys(parsed.triage).length > 0 ? parsed.triage : null,
                    facilities: parsed.facilities || [],
                    isStreaming: false
                  }
                }
                return msg
              }))
            } catch (e) {
              console.error('Error parsing [DONE] metadata:', e)
              setMessages(prev => prev.map(msg => msg.id === botMsgId ? { ...msg, isStreaming: false } : msg))
            }
          } else {
            accumulatedText += dataContent
            setMessages(prev => prev.map(msg => {
              if (msg.id === botMsgId) {
                return { ...msg, text: accumulatedText }
              }
              return msg
            }))
          }
        }
      }
    } catch (error) {
      console.warn('Streaming error, falling back to /chat:', error)
      useFallback = true
    }

    if (useFallback) {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/chat/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: text, session_id: sessionId })
        })

        if (!response.ok) {
          throw new Error('API Request Failed')
        }

        const data = await response.json()
        
        if (data.session_id && sessionId === null) {
          setSessionId(data.session_id)
        }
        
        const botMsg = {
          id: botMsgId,
          role: 'bot',
          text: data.reply,
          triage: data.triage && Object.keys(data.triage).length > 0 ? data.triage : null,
          facilities: data.facilities || [],
          isStreaming: false
        }

        setMessages(prev => [...prev, botMsg])
      } catch (fallbackError) {
        console.error('Fallback error:', fallbackError)
        const errorMsg = {
          id: `error-${Date.now()}`,
          role: 'bot',
          text: "I am sorry, I am having trouble answering right now. Please visit your nearest PHC.",
          triage: null,
          facilities: [],
          isStreaming: false
        }
        setMessages(prev => [...prev, errorMsg])
      } finally {
        setIsLoading(false)
      }
    } else {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 relative min-h-[500px]">
      {/* Sticky Header */}
      <header className="sticky top-0 h-[56px] bg-green-700 text-white flex items-center px-4 shadow-sm z-10 justify-between">
        <div className="flex items-center gap-2">
          <Heart className="w-5 h-5 text-green-100 fill-green-100" aria-hidden="true" />
          <span className="font-semibold text-lg tracking-tight">AarogyaBot</span>
        </div>
      </header>

      {/* Main Message List */}
      <main className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 custom-scrollbar">
        {messages.map((msg) => (
          <div key={msg.id} className="flex flex-col gap-2">
            <MessageBubble
              role={msg.role}
              text={
                msg.isStreaming ? (
                  <>
                    {msg.text}
                    <span className="animate-pulse w-1 h-4 bg-gray-400 inline-block ml-1" />
                  </>
                ) : (
                  msg.text
                )
              }
            />
            {msg.role === 'bot' && msg.triage && (
              <div className="w-full max-w-[80%] animate-fade-in">
                <TriageCard triage={msg.triage} />
              </div>
            )}
            {msg.role === 'bot' && msg.facilities && msg.facilities.length > 0 && (
              <div className="w-full max-w-[80%] flex flex-col gap-2 mt-1 animate-fade-in">
                {msg.facilities.map((fac, idx) => (
                  <FacilityCard key={idx} facility={fac} />
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex w-full justify-start animate-fade-in">
            <div className="flex space-x-1.5 p-3.5 bg-white border border-gray-200 rounded-2xl max-w-[80px] justify-center items-center shadow-sm">
              <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce motion-reduce:animate-none" />
              <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce motion-reduce:animate-none" style={{ animationDelay: '0.15s' }} />
              <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce motion-reduce:animate-none" style={{ animationDelay: '0.3s' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      <QuickReplies
        visible={showQuickReplies}
        onSelect={(text) => {
          setShowQuickReplies(false)
          sendMessage(text)
        }}
      />

      {/* Sticky Input Bar */}
      <footer className="sticky bottom-0 bg-white border-t border-gray-200 p-3 flex flex-col gap-2">
        {isSupported && (
          <div className="flex items-center justify-between text-xs text-gray-500 px-1">
            <div className="flex items-center gap-1.5">
              <label htmlFor="voice-lang-select" className="font-medium text-gray-600">Voice Language:</label>
              <select
                id="voice-lang-select"
                value={recognitionLanguage}
                onChange={(e) => setRecognitionLanguage(e.target.value)}
                className="bg-gray-50 border border-gray-300 rounded px-2 py-0.5 text-gray-700 focus:ring-1 focus:ring-green-500 focus:outline-none"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
            {isRecording && (
              <span className="text-red-500 font-semibold animate-pulse motion-reduce:animate-none flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-red-500 inline-block animate-ping absolute opacity-75 motion-reduce:hidden"></span>
                <span className="w-2 h-2 rounded-full bg-red-500 inline-block relative"></span>
                Listening...
              </span>
            )}
          </div>
        )}
        
        {errorMessage && (
          <div className="text-red-500 text-xs px-1 animate-fade-in">
            {errorMessage}
          </div>
        )}

        <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex items-center gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type health concern or 6-digit PIN code..."
            disabled={isLoading}
            className="flex-1 rounded-full border border-gray-300 px-4 py-2 text-[16px] min-h-[44px] focus:ring-2 focus:ring-green-500 focus:outline-none focus:border-green-500 focus:ring-offset-1 disabled:bg-gray-100 disabled:text-gray-400"
          />
          {isSupported && (
            <button
              type="button"
              onClick={toggleRecording}
              disabled={isLoading}
              className={`w-11 h-11 rounded-full flex items-center justify-center transition-colors focus:ring-2 focus:ring-green-500 focus:outline-none focus:ring-offset-1 relative ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse motion-reduce:animate-none'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }`}
              style={{ minWidth: '44px', minHeight: '44px' }}
              aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
            >
              {isRecording ? (
                <div className="relative flex items-center justify-center">
                  <MicOff className="w-5 h-5 text-white" />
                  <span className="absolute -top-1 -right-1 flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75 motion-reduce:hidden"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-red-600"></span>
                  </span>
                </div>
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </button>
          )}
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="w-11 h-11 bg-green-600 hover:bg-green-700 disabled:opacity-40 disabled:cursor-not-allowed rounded-full flex items-center justify-center text-white transition-colors focus:ring-2 focus:ring-green-500 focus:outline-none focus:ring-offset-1"
            style={{ minWidth: '44px', minHeight: '44px' }}
            aria-label="Send message"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </footer>
    </div>
  )
}

export default ChatInterface
