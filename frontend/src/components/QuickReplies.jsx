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
    <div className="flex flex-wrap gap-2 px-4 pb-3">
      {CHIPS.map(({ label, Icon }) => (
        <button
          key={label}
          type="button"
          onClick={() => onSelect(label)}
          className="rounded-full border border-green-600 text-green-700 bg-white hover:bg-green-50 hover:shadow-md transition-shadow px-4 py-2.5 text-sm cursor-pointer min-h-[44px] flex items-center gap-1.5"
        >
          <Icon className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
          {label}
        </button>
      ))}
    </div>
  )
}

export default QuickReplies
