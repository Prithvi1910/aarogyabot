import React from 'react'
import { HeartPulse, ArrowRight, Languages, Stethoscope, MapPin, Camera } from 'lucide-react'
import HealthBackground from './HealthBackground'

const FEATURES = [
  { label: '10+ Languages', Icon: Languages },
  { label: 'AI Triage', Icon: Stethoscope },
  { label: 'Find PHCs', Icon: MapPin },
  { label: 'Photo Check', Icon: Camera },
]

const STATS = [
  { number: '65%', label: 'Rural population served' },
  { number: '500+', label: 'Health centres mapped' },
  { number: '24/7', label: 'Always available' },
]

function LandingPage({ onStart }) {
  return (
    <div className="relative min-h-[100dvh] overflow-hidden bg-gradient-to-b from-brand-800 via-brand-700 to-brand-500">
      {/* Soft decorative glows */}
      <div className="pointer-events-none absolute -top-24 -right-20 h-72 w-72 rounded-full bg-brand-400/30 blur-3xl" />
      <div className="pointer-events-none absolute top-1/3 -left-24 h-80 w-80 rounded-full bg-brand-300/20 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 right-1/4 h-72 w-72 rounded-full bg-white/10 blur-3xl" />

      {/* Health-themed animated background */}
      <HealthBackground variant="landing" />

      <div className="relative z-10 mx-auto flex min-h-[100dvh] max-w-md flex-col items-center justify-center px-7 py-12 text-center">
        {/* App icon */}
        <div className="mb-7 flex h-20 w-20 items-center justify-center rounded-3xl glass shadow-glow animate-floaty">
          <HeartPulse className="h-10 w-10 text-white" aria-hidden="true" />
        </div>

        {/* Wordmark */}
        <span className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-brand-100/90">
          AarogyaBot
        </span>

        {/* Hero heading */}
        <h1 className="text-[2.6rem] font-extrabold leading-[1.08] tracking-tight text-white">
          Your health,
          <br />
          just a tap away.
        </h1>

        {/* Subtitle */}
        <p className="mt-4 max-w-xs text-[15px] leading-relaxed text-brand-50/80">
          An AI public-health assistant for rural India — ask in your language by voice, text, or photo.
        </p>

        {/* Feature chips */}
        <div className="mt-8 flex flex-wrap justify-center gap-2.5">
          {FEATURES.map(({ label, Icon }) => (
            <span
              key={label}
              className="flex items-center gap-1.5 rounded-full bg-white/12 px-3.5 py-1.5 text-[13px] font-medium text-white ring-1 ring-white/15 backdrop-blur-sm"
            >
              <Icon className="h-3.5 w-3.5 text-brand-100" aria-hidden="true" />
              {label}
            </span>
          ))}
        </div>

        {/* Stats */}
        <div className="mt-10 grid w-full max-w-sm grid-cols-3 gap-3">
          {STATS.map(({ number, label }) => (
            <div
              key={label}
              className="rounded-2xl bg-white/10 px-2 py-4 ring-1 ring-white/10 backdrop-blur-sm"
            >
              <div className="text-2xl font-bold text-white">{number}</div>
              <div className="mt-1 text-[11px] leading-tight text-brand-50/75">{label}</div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <button
          onClick={onStart}
          className="group mt-10 flex w-full max-w-sm items-center justify-between gap-3 rounded-full bg-white py-2.5 pl-7 pr-2.5 text-lg font-semibold text-brand-700 shadow-glow transition-all duration-200 hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0"
          aria-label="Start chatting with AarogyaBot"
        >
          Start Chat
          <span className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-600 text-white transition-transform duration-200 group-hover:translate-x-0.5">
            <ArrowRight className="h-5 w-5" aria-hidden="true" />
          </span>
        </button>

        {/* Disclaimer */}
        <p className="mt-6 max-w-xs text-[11px] leading-relaxed text-brand-100/60">
          For informational purposes only. Not a substitute for professional medical advice.
        </p>
      </div>
    </div>
  )
}

export default LandingPage
