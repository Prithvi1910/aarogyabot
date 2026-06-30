import React from 'react'
import { AlertTriangle, Info, Phone } from 'lucide-react'

function TriageCard({ triage }) {
  if (!triage || !triage.level || triage.level === 'SELF_CARE') {
    return null
  }

  const isEmergency = triage.level === 'EMERGENCY'

  if (isEmergency) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-3.5 shadow-soft">
        <div className="flex items-start gap-2.5">
          <span className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-rose-500 text-white">
            <AlertTriangle className="h-4 w-4" aria-hidden="true" />
          </span>
          <div className="text-[14px] leading-relaxed text-rose-800">
            <span className="mb-0.5 flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider text-rose-700">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-500 opacity-75" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-rose-500" />
              </span>
              Emergency Warning
            </span>
            {triage.action}
            {/* One-tap ambulance SOS */}
            <a
              href="tel:108"
              className="mt-2.5 flex items-center justify-center gap-2 rounded-xl bg-rose-600 px-4 py-2.5 text-[14px] font-bold text-white shadow-soft transition-all hover:-translate-y-0.5 hover:bg-rose-700"
              aria-label="Call 108 ambulance"
            >
              <Phone className="h-4 w-4" />
              Call 108 Ambulance
            </a>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 p-3.5 shadow-soft">
      <div className="flex items-start gap-2.5">
        <span className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-amber-400 text-white">
          <Info className="h-4 w-4" aria-hidden="true" />
        </span>
        <div className="text-[14px] leading-relaxed text-amber-900">
          <span className="mb-0.5 block text-[11px] font-bold uppercase tracking-wider text-amber-700">
            Visit PHC Recommended
          </span>
          {triage.action}
        </div>
      </div>
    </div>
  )
}

export default TriageCard
