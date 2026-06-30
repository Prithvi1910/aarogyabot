import React from 'react'
import { Heart, Plus, Activity, Pill, Stethoscope, Cross, Thermometer, Syringe } from 'lucide-react'

// Build a seamless ECG/heartbeat waveform path.
// width is split into `beats` cycles; pattern repeats every (width/beats) units,
// so translating the 2x-wide SVG by -50% loops seamlessly.
function ecgPath(width, beats) {
  const seg = width / beats
  const mid = 50
  let d = `M0,${mid}`
  for (let i = 0; i < beats; i++) {
    const x = i * seg
    d += ` L${x + seg * 0.30},${mid}`     // baseline
    d += ` L${x + seg * 0.34},${mid - 7}` // P wave
    d += ` L${x + seg * 0.38},${mid}`
    d += ` L${x + seg * 0.46},${mid}`
    d += ` L${x + seg * 0.49},${mid + 9}` // Q
    d += ` L${x + seg * 0.52},${mid - 36}`// R spike
    d += ` L${x + seg * 0.55},${mid + 20}`// S
    d += ` L${x + seg * 0.59},${mid}`
    d += ` L${x + seg * 0.72},${mid}`
    d += ` L${x + seg * 0.78},${mid - 12}`// T wave
    d += ` L${x + seg * 0.84},${mid}`
    d += ` L${x + seg},${mid}`
  }
  return d
}

const FLOATING_ICons = [
  { Icon: Heart,       top: '12%', left: '8%',  size: 30, dur: '12s', delay: '0s' },
  { Icon: Plus,        top: '22%', left: '82%', size: 26, dur: '10s', delay: '1.2s' },
  { Icon: Activity,    top: '64%', left: '14%', size: 30, dur: '13s', delay: '0.6s' },
  { Icon: Pill,        top: '74%', left: '78%', size: 26, dur: '11s', delay: '2s' },
  { Icon: Stethoscope, top: '40%', left: '88%', size: 28, dur: '14s', delay: '0.3s' },
  { Icon: Cross,       top: '50%', left: '5%',  size: 24, dur: '12s', delay: '1.8s' },
  { Icon: Thermometer, top: '85%', left: '40%', size: 24, dur: '15s', delay: '0.9s' },
  { Icon: Syringe,     top: '8%',  left: '52%', size: 24, dur: '13s', delay: '2.4s' },
]

function HealthBackground({ variant = 'landing', className = '' }) {
  const dark = variant === 'landing'
  const iconColor = dark ? 'text-white' : 'text-brand-500'
  const iconOpacity = dark ? 'opacity-[0.10]' : 'opacity-[0.06]'
  const ecgStroke = dark ? 'rgba(212,244,242,0.55)' : 'rgba(29,133,132,0.16)'
  const ecgGlow = dark ? 'rgba(132,214,210,0.6)' : 'rgba(76,188,185,0.25)'

  const d = ecgPath(1200, 12)

  return (
    <div className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`} aria-hidden="true">
      {/* Floating medical icons */}
      {FLOATING_ICons.map(({ Icon, top, left, size, dur, delay }, i) => (
        <div
          key={i}
          className={`drift absolute ${iconColor} ${iconOpacity}`}
          style={{ top, left, animationDuration: dur, animationDelay: delay }}
        >
          <Icon style={{ width: size, height: size }} strokeWidth={1.5} />
        </div>
      ))}

      {/* Heartbeat pulse rings */}
      <div className="absolute left-1/2 top-[30%] -translate-x-1/2">
        {[0, 1.5, 3].map((delay, i) => (
          <span
            key={i}
            className={`pulse-ring absolute left-1/2 top-1/2 h-40 w-40 -translate-x-1/2 -translate-y-1/2 rounded-full border ${
              dark ? 'border-white/40' : 'border-brand-400/40'
            }`}
            style={{ animationDelay: `${delay}s` }}
          />
        ))}
      </div>

      {/* Scrolling ECG monitor line */}
      <div className="absolute inset-x-0 bottom-[16%] h-24 overflow-hidden">
        <svg
          className="ecg-scroll h-full"
          width="200%"
          viewBox="0 0 1200 100"
          preserveAspectRatio="none"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d={d} stroke={ecgStroke} strokeWidth="2" strokeLinejoin="round"
            style={{ filter: `drop-shadow(0 0 6px ${ecgGlow})` }} />
        </svg>
      </div>
    </div>
  )
}

export default HealthBackground
