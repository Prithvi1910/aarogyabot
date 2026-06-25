import React from 'react'
import { HeartPulse } from 'lucide-react'

function LandingPage({ onStart }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-green-800 to-green-600 px-6 py-12">
      {/* Hero Icon */}
      <HeartPulse className="w-16 h-16 text-white drop-shadow-lg" aria-hidden="true" />

      {/* Title */}
      <h1 className="text-4xl font-bold text-white mt-4 tracking-tight">
        AarogyaBot
      </h1>

      {/* Subtitle */}
      <p className="text-green-100 text-lg text-center max-w-sm mt-2 leading-relaxed">
        AI-Powered Public Health Assistant for Rural India
      </p>

      {/* Feature Pills */}
      <div className="flex flex-wrap justify-center gap-2 mt-6">
        {["10+ Languages", "300+ Health Centers", "24/7 Available"].map((pill) => (
          <span
            key={pill}
            className="bg-white/20 text-white rounded-full px-3 py-1 text-sm font-medium backdrop-blur-sm"
          >
            {pill}
          </span>
        ))}
      </div>

      {/* Stats Row */}
      <div className="flex gap-10 mt-10">
        {[
          { number: "65%", label: "Rural Population Served" },
          { number: "10+", label: "Indian Languages" },
          { number: "300+", label: "PHCs Mapped" },
        ].map(({ number, label }) => (
          <div key={label} className="flex flex-col items-center">
            <span className="text-3xl font-bold text-white">{number}</span>
            <span className="text-green-200 text-xs mt-1 text-center max-w-[80px] leading-tight">{label}</span>
          </div>
        ))}
      </div>

      {/* CTA Button */}
      <button
        onClick={onStart}
        className="mt-8 bg-white text-green-700 font-bold rounded-full px-8 py-4 text-lg hover:bg-green-50 shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-105 active:scale-95"
        aria-label="Start chatting with AarogyaBot"
      >
        Start Chat →
      </button>

      {/* Disclaimer */}
      <p className="text-green-300 text-xs text-center mt-4 max-w-xs leading-relaxed">
        For informational purposes only. Not a substitute for medical advice.
      </p>
    </div>
  )
}

export default LandingPage
