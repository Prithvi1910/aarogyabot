import React from 'react'
import { Stethoscope, MapPin, Shield, AlertTriangle } from 'lucide-react'

const CHIPS = [
  { label: "Common Symptoms",   Icon: Stethoscope },
  { label: "Find Nearest PHC",  Icon: MapPin },
  { label: "Disease Prevention", Icon: Shield },
  { label: "Emergency Signs",   Icon: AlertTriangle },
]

function QuickReplies({ onSelect, visible }) {
  if (!visible) return null

  return (
    <div className="px-4 pb-3">
      <p className="mb-2 px-1 text-[11px] font-semibold uppercase tracking-wider text-ink-500">
        Try asking
      </p>
      <div className="grid grid-cols-2 gap-2">
        {CHIPS.map(({ label, Icon }) => (
          <button
            key={label}
            type="button"
            onClick={() => onSelect(label)}
            className="group flex items-center gap-2.5 rounded-2xl border border-brand-100 bg-white px-3.5 py-3 text-left text-sm font-medium text-ink-900 shadow-soft transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-card"
          >
            <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600 transition-colors group-hover:bg-brand-100">
              <Icon className="h-4 w-4" aria-hidden="true" />
            </span>
            {label}
          </button>
        ))}
      </div>
    </div>
  )
}

export default QuickReplies
