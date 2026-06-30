import React, { useState, useEffect, useRef } from 'react'
import { HeartPulse, Send, Mic, MicOff, FileText, X, Download, Camera, Volume2, VolumeX, Activity, Navigation } from 'lucide-react'
import MessageBubble from './MessageBubble'
import TriageCard from './TriageCard'
import FacilityCard from './FacilityCard'
import QuickReplies from './QuickReplies'
import HealthBackground from './HealthBackground'
import AlertsDashboard from './AlertsDashboard'
import { getOfflineReply } from '../offlineFirstAid'

const VOICE_LANGUAGES = [
  { code: "hi-IN", label: "Hindi" },
  { code: "gu-IN", label: "Gujarati" },
  { code: "mr-IN", label: "Marathi" },
  { code: "ta-IN", label: "Tamil" },
  { code: "te-IN", label: "Telugu" },
  { code: "en-IN", label: "English" },
  { code: "pa-IN", label: "Punjabi" },
  { code: "ur-IN", label: "Urdu" },
  { code: "or-IN", label: "Odia" },
  { code: "as-IN", label: "Assamese" }
]

// Map the backend's short language codes to BCP-47 tags for speech synthesis
const TTS_LANG_MAP = {
  hi: "hi-IN", ta: "ta-IN", te: "te-IN", gu: "gu-IN", mr: "mr-IN",
  en: "en-IN", pa: "pa-IN", ur: "ur-IN", or: "or-IN", as: "as-IN",
  bn: "bn-IN", kn: "kn-IN", ml: "ml-IN"
}

function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'bot',
      text: "Hello! I am AarogyaBot. Ask me about any health concern, tap the camera to send a photo of a rash, wound or eye problem, or send your PIN code to find the nearest health facility. I understand Hindi, Tamil, Telugu, Gujarati and more.",
      triage: null,
      facilities: []
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [showQuickReplies, setShowQuickReplies] = useState(true)
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  // Health Report state
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const [reportData, setReportData] = useState(null)
  const [reportToast, setReportToast] = useState('')

  // Outbreak surveillance dashboard
  const [showAlerts, setShowAlerts] = useState(false)

  // Online/offline status (PWA)
  const [isOffline, setIsOffline] = useState(typeof navigator !== 'undefined' && !navigator.onLine)

  // Text-to-Speech (voice output) state
  const [ttsSupported, setTtsSupported] = useState(false)
  const [autoSpeak, setAutoSpeak] = useState(false)
  const [speakingId, setSpeakingId] = useState(null)

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

  // Track online/offline status for the PWA
  useEffect(() => {
    const goOnline = () => setIsOffline(false)
    const goOffline = () => setIsOffline(true)
    window.addEventListener('online', goOnline)
    window.addEventListener('offline', goOffline)
    return () => {
      window.removeEventListener('online', goOnline)
      window.removeEventListener('offline', goOffline)
    }
  }, [])

  // Detect Speech Synthesis (voice output) support and pre-load voices
  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      setTtsSupported(true)
      // Some browsers populate the voice list asynchronously
      window.speechSynthesis.getVoices()
      window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices()
    }
    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  // Speak a bot reply aloud in the given language. Clicking again stops it.
  const speakText = (id, text, lang = 'en') => {
    if (!ttsSupported || !text) return
    const synth = window.speechSynthesis

    // Toggle off if this same message is already speaking
    if (speakingId === id) {
      synth.cancel()
      setSpeakingId(null)
      return
    }

    synth.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    const bcp = TTS_LANG_MAP[lang] || 'en-IN'
    utterance.lang = bcp
    utterance.rate = 0.95

    // Try to pick a voice that matches the language
    const voices = synth.getVoices()
    const match =
      voices.find(v => v.lang === bcp) ||
      voices.find(v => v.lang && v.lang.toLowerCase().startsWith((lang || 'en').toLowerCase()))
    if (match) utterance.voice = match

    utterance.onend = () => setSpeakingId(null)
    utterance.onerror = () => setSpeakingId(null)

    setSpeakingId(id)
    synth.speak(utterance)
  }

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

    // Offline: answer from the bundled first-aid pack instead of the server
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      const off = getOfflineReply(text)
      setMessages(prev => [...prev, {
        id: `bot-${Date.now()}`, role: 'bot', text: off.reply,
        triage: off.triage, facilities: [], sources: []
      }])
      setIsLoading(false)
      return
    }

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
        id: `bot-${Date.now()}`,
        role: 'bot',
        text: data.reply,
        lang: data.lang || 'en',
        sources: data.sources || [],
        triage: data.triage && Object.keys(data.triage).length > 0 ? data.triage : null,
        facilities: data.facilities || []
      }

      setMessages(prev => [...prev, botMsg])
      if (autoSpeak) speakText(botMsg.id, botMsg.text, botMsg.lang)
    } catch (error) {
      console.error('Chat error:', error)
      // Network failed — fall back to the offline first-aid pack
      const off = getOfflineReply(text)
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        role: 'bot',
        text: off.reply,
        triage: off.triage,
        facilities: [],
        sources: []
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleImagePick = (e) => {
    const fileObj = e.target.files && e.target.files[0]
    // Reset so picking the same file again re-triggers onChange
    e.target.value = ''
    if (fileObj) sendImage(fileObj)
  }

  const sendImage = async (fileObj) => {
    if (!fileObj || isLoading) return
    if (!fileObj.type.startsWith('image/')) {
      setErrorMessage('Please select an image file.')
      return
    }

    setShowQuickReplies(false)
    setErrorMessage('')

    // Stop recording if active
    if (isRecording && recognitionRef.current) {
      recognitionRef.current.stop()
    }

    const note = inputText.trim()
    const previewUrl = URL.createObjectURL(fileObj)

    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: note,
      image: previewUrl
    }
    setMessages(prev => [...prev, userMsg])
    setInputText('')
    setIsLoading(true)

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const form = new FormData()
      form.append('file', fileObj)
      form.append('note', note)
      if (sessionId) form.append('session_id', sessionId)
      // Detect reply language from the note when present, else English
      form.append('lang', 'auto')

      const response = await fetch(`${apiUrl}/chat/image`, {
        method: 'POST',
        body: form
      })

      if (!response.ok) {
        throw new Error('Image API Request Failed')
      }

      const data = await response.json()

      if (data.session_id && sessionId === null) {
        setSessionId(data.session_id)
      }

      const botMsg = {
        id: `bot-${Date.now()}`,
        role: 'bot',
        text: data.reply,
        lang: data.lang || 'en',
        triage: data.triage && Object.keys(data.triage).length > 0 ? data.triage : null,
        facilities: data.facilities || []
      }
      setMessages(prev => [...prev, botMsg])
      if (autoSpeak) speakText(botMsg.id, botMsg.text, botMsg.lang)
    } catch (error) {
      console.error('Image chat error:', error)
      const errorMsg = {
        id: `error-${Date.now()}`,
        role: 'bot',
        text: "I could not analyse this photo right now. Please show it to a health worker at your nearest PHC.",
        triage: null,
        facilities: []
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  // Find nearest PHCs using the device GPS (falls back to asking for a PIN code)
  const findNearbyByGPS = () => {
    setShowQuickReplies(false)
    if (!('geolocation' in navigator)) {
      setMessages(prev => [...prev, {
        id: `bot-${Date.now()}`, role: 'bot',
        text: 'Location is not available on this device. Please type your 6-digit PIN code and I will find nearby facilities.',
        triage: null, facilities: []
      }])
      return
    }

    setMessages(prev => [...prev, { id: `user-${Date.now()}`, role: 'user', text: '📍 Find nearest health centre' }])
    setIsLoading(true)

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const { latitude, longitude } = pos.coords
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
          const res = await fetch(`${apiUrl}/facilities/nearby?lat=${latitude}&lon=${longitude}&limit=3`)
          if (!res.ok) throw new Error('nearby failed')
          const facilities = await res.json()
          setMessages(prev => [...prev, {
            id: `bot-${Date.now()}`, role: 'bot',
            text: facilities.length
              ? 'Here are the closest health facilities to your location:'
              : 'No facilities found near your location. Please type your PIN code to search.',
            triage: null, facilities
          }])
        } catch (e) {
          console.error('GPS facility error:', e)
          setMessages(prev => [...prev, {
            id: `bot-${Date.now()}`, role: 'bot',
            text: 'I could not fetch nearby facilities. Please type your 6-digit PIN code instead.',
            triage: null, facilities: []
          }])
        } finally {
          setIsLoading(false)
        }
      },
      (err) => {
        console.error('Geolocation denied:', err)
        setIsLoading(false)
        setMessages(prev => [...prev, {
          id: `bot-${Date.now()}`, role: 'bot',
          text: 'Location access was denied. Please type your 6-digit PIN code and I will find nearby facilities.',
          triage: null, facilities: []
        }])
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }

  const generateHealthReport = async () => {
    if (!sessionId || isGeneratingReport) return
    setIsGeneratingReport(true)
    setReportToast('')
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/chat/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      })
      if (!response.ok) throw new Error('Report generation failed')
      const data = await response.json()
      setReportData(data)
    } catch (err) {
      console.error('Report error:', err)
      setReportToast('Could not generate report')
      setTimeout(() => setReportToast(''), 3000)
    } finally {
      setIsGeneratingReport(false)
    }
  }

  const downloadReport = () => {
    if (!reportData) return
    const blob = new Blob([reportData.report], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'AarogyaBot_Health_Report.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  // Count user messages to decide when to show the report button
  const userMessageCount = messages.filter(m => m.role === 'user').length

  return (
    <div className="flex flex-col h-full bg-[#f6faf9] relative isolate min-h-[500px]">
      {/* Faint health-themed background */}
      <HealthBackground variant="chat" className="z-0" />

      {/* Sticky Header */}
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-brand-100/70 glass px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-soft">
            <HeartPulse className="h-5 w-5" aria-hidden="true" />
          </div>
          <div className="leading-tight">
            <div className="text-[15px] font-bold text-ink-900">AarogyaBot</div>
            {isOffline ? (
              <div className="flex items-center gap-1.5 text-[11px] font-medium text-amber-600">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                Offline · First-aid mode
              </div>
            ) : (
              <div className="flex items-center gap-1.5 text-[11px] font-medium text-brand-600">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-400 opacity-75" />
                  <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-brand-500" />
                </span>
                Online · Health Assistant
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1">
          {/* Outbreak alerts dashboard */}
          <button
            type="button"
            onClick={() => setShowAlerts(true)}
            className="relative flex h-9 w-9 items-center justify-center rounded-full text-ink-500 transition-colors hover:bg-brand-50 hover:text-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-300"
            aria-label="Open community health alerts"
            title="Community health alerts"
          >
            <Activity className="w-[18px] h-[18px]" />
            <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-rose-500 ring-2 ring-white" />
          </button>

          {/* Auto-read replies aloud toggle */}
          {ttsSupported && (
            <button
              type="button"
              onClick={() => {
                const next = !autoSpeak
                setAutoSpeak(next)
                if (!next) {
                  window.speechSynthesis.cancel()
                  setSpeakingId(null)
                }
              }}
              className={`flex h-9 w-9 items-center justify-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-brand-300 ${
                autoSpeak ? 'bg-brand-100 text-brand-700' : 'text-ink-500 hover:bg-brand-50 hover:text-brand-600'
              }`}
              aria-pressed={autoSpeak}
              aria-label={autoSpeak ? 'Turn off auto read-aloud' : 'Turn on auto read-aloud'}
              title={autoSpeak ? 'Auto read-aloud is ON' : 'Auto read-aloud is OFF'}
            >
              {autoSpeak ? <Volume2 className="w-[18px] h-[18px]" /> : <VolumeX className="w-[18px] h-[18px]" />}
            </button>
          )}
        </div>
      </header>

      {/* Outbreak surveillance dashboard overlay */}
      {showAlerts && <AlertsDashboard onClose={() => setShowAlerts(false)} />}

      {/* Main Message List */}
      <main className="relative z-10 flex-1 overflow-y-auto px-4 py-5 flex flex-col gap-3.5 chat-scroll">
        {messages.map((msg) => (
          <div key={msg.id} className="flex flex-col gap-2">
            <MessageBubble
              role={msg.role}
              text={msg.text}
              image={msg.image}
              sources={msg.sources}
              showSpeak={msg.role === 'bot' && ttsSupported}
              isSpeaking={speakingId === msg.id}
              onSpeak={() => speakText(msg.id, msg.text, msg.lang)}
            />
            {msg.role === 'bot' && msg.triage && (
              <div className="ml-10 max-w-[88%] animate-fade-in">
                <TriageCard triage={msg.triage} />
              </div>
            )}
            {msg.role === 'bot' && msg.facilities && msg.facilities.length > 0 && (
              <div className="ml-10 flex max-w-[88%] flex-col gap-2 animate-fade-in">
                {msg.facilities.map((fac, idx) => (
                  <FacilityCard key={idx} facility={fac} />
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex w-full items-end gap-2 animate-fade-in">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-brand-700 text-xs font-bold text-white shadow-sm">
              A
            </div>
            <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md bg-white px-4 py-3.5 shadow-soft ring-1 ring-brand-100/70">
              <div className="h-2 w-2 rounded-full bg-brand-400 animate-bounce motion-reduce:animate-none" />
              <div className="h-2 w-2 rounded-full bg-brand-400 animate-bounce motion-reduce:animate-none" style={{ animationDelay: '0.15s' }} />
              <div className="h-2 w-2 rounded-full bg-brand-400 animate-bounce motion-reduce:animate-none" style={{ animationDelay: '0.3s' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      <div className="relative z-10">
        <QuickReplies
          visible={showQuickReplies}
          onSelect={(text) => {
            setShowQuickReplies(false)
            if (text === 'Find Nearest PHC') {
              findNearbyByGPS()
            } else {
              sendMessage(text)
            }
          }}
        />
      </div>

      {/* Floating Health Report Button — appears after 3+ user messages */}
      {userMessageCount >= 3 && sessionId && (
        <button
          id="generate-report-btn"
          onClick={generateHealthReport}
          disabled={isGeneratingReport}
          className="absolute bottom-28 right-4 z-20 flex items-center gap-2 rounded-full bg-gradient-to-r from-brand-600 to-brand-700 px-4 py-2.5 text-sm font-medium text-white shadow-glow transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60 animate-pop-in"
          aria-label="Generate health report"
        >
          <FileText className="w-4 h-4" />
          {isGeneratingReport ? 'Generating…' : 'Health Report'}
        </button>
      )}

      {/* Error Toast */}
      {reportToast && (
        <div className="absolute bottom-40 right-4 z-30 rounded-full bg-rose-500 px-4 py-2 text-sm text-white shadow-lg animate-fade-in">
          {reportToast}
        </div>
      )}

      {/* Health Report Modal */}
      {reportData && (
        <div
          className="absolute inset-0 z-40 flex items-center justify-center bg-ink-900/40 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-label="Health Summary Report"
        >
          <div className="flex max-h-[82%] w-full flex-col gap-4 rounded-3xl bg-white p-6 shadow-card animate-pop-in">
            {/* Modal Header */}
            <div className="flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-lg font-bold text-ink-900">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-100 text-brand-700">
                  <FileText className="h-[18px] w-[18px]" />
                </span>
                Health Summary
              </h2>
              <button
                onClick={() => setReportData(null)}
                className="flex h-8 w-8 items-center justify-center rounded-full text-ink-500 transition-colors hover:bg-brand-50 hover:text-ink-900"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Generated timestamp */}
            <p className="text-xs text-ink-500">Generated: {reportData.generated_at}</p>

            {/* Report Body */}
            <div className="flex-1 overflow-y-auto rounded-2xl bg-brand-50/60 p-4 ring-1 ring-brand-100/70 chat-scroll">
              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-ink-700">
                {reportData.report}
              </pre>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-3 pt-1">
              <button
                onClick={() => setReportData(null)}
                className="rounded-full bg-brand-50 px-4 py-2.5 text-sm font-medium text-ink-700 transition-colors hover:bg-brand-100"
              >
                Close
              </button>
              <button
                onClick={downloadReport}
                className="flex items-center gap-2 rounded-full bg-gradient-to-r from-brand-600 to-brand-700 px-4 py-2.5 text-sm font-medium text-white shadow-soft transition-all hover:-translate-y-0.5"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sticky Input Bar */}
      <footer className="sticky bottom-0 z-10 border-t border-brand-100/70 glass px-3 pb-3 pt-2.5 flex flex-col gap-2">
        {isSupported && (
          <div className="flex items-center justify-between px-1 text-xs text-ink-500">
            <div className="flex items-center gap-1.5">
              <label htmlFor="voice-lang-select" className="font-medium">Voice</label>
              <select
                id="voice-lang-select"
                value={recognitionLanguage}
                onChange={(e) => setRecognitionLanguage(e.target.value)}
                className="rounded-lg border border-brand-100 bg-white px-2 py-1 font-medium text-ink-700 focus:outline-none focus:ring-2 focus:ring-brand-200"
              >
                {VOICE_LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>
            {isRecording && (
              <span className="flex items-center gap-1.5 font-semibold text-rose-500">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-400 opacity-75 motion-reduce:hidden" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-rose-500" />
                </span>
                Listening…
              </span>
            )}
          </div>
        )}

        {errorMessage && (
          <div className="px-1 text-xs text-rose-500 animate-fade-in">
            {errorMessage}
          </div>
        )}

        <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex items-center gap-2">
          {/* Hidden file input for the visual symptom checker */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleImagePick}
            className="hidden"
            aria-hidden="true"
            tabIndex={-1}
          />

          {/* Input pill with camera + mic inside */}
          <div className="flex flex-1 items-center gap-1 rounded-full border border-brand-100 bg-white py-1 pl-4 pr-1 shadow-soft transition-all focus-within:border-brand-300 focus-within:ring-2 focus-within:ring-brand-200/60">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type a health concern or PIN code…"
              disabled={isLoading}
              className="min-h-[40px] min-w-0 flex-1 bg-transparent text-[15px] text-ink-900 placeholder:text-ink-500/60 focus:outline-none disabled:text-ink-500/50"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-ink-500 transition-colors hover:bg-brand-50 hover:text-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-200 disabled:opacity-40"
              aria-label="Send a photo of your health concern"
              title="Send a photo (rash, wound, eye, snake-bite)"
            >
              <Camera className="h-[19px] w-[19px]" />
            </button>
            {isSupported && (
              <button
                type="button"
                onClick={toggleRecording}
                disabled={isLoading}
                className={`relative flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-brand-200 ${
                  isRecording
                    ? 'bg-rose-500 text-white'
                    : 'text-ink-500 hover:bg-brand-50 hover:text-brand-600'
                }`}
                aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
              >
                {isRecording ? (
                  <>
                    <MicOff className="h-[19px] w-[19px]" />
                    <span className="absolute -right-0.5 -top-0.5 flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-300 opacity-75 motion-reduce:hidden" />
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-rose-400" />
                    </span>
                  </>
                ) : (
                  <Mic className="h-[19px] w-[19px]" />
                )}
              </button>
            )}
          </div>

          {/* Send */}
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-glow transition-all hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-brand-300 disabled:translate-y-0 disabled:opacity-40 disabled:shadow-none"
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
      </footer>
    </div>
  )
}

export default ChatInterface
