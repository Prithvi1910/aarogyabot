import React from 'react'
import { AlertTriangle, Info } from 'lucide-react'

function TriageCard({ triage }) {
  if (!triage || !triage.level || triage.level === 'SELF_CARE') {
    return null
  }

  const isEmergency = triage.level === 'EMERGENCY'

  if (isEmergency) {
    return (
      <div className="bg-red-50 border border-red-300 text-red-800 rounded-2xl p-[12px] mt-[8px] font-bold">
        <div className="flex items-start gap-2">
          {/* Pulsing dot */}
          <span className="flex-shrink-0 mt-1.5 relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
          </span>
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5 text-red-800" aria-hidden="true" />
          <div className="text-[14px] leading-relaxed">
            <span className="block font-black uppercase tracking-wider text-[11px] mb-0.5 text-red-900">
              EMERGENCY WARNING
            </span>
            {triage.action}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-yellow-50 border border-yellow-300 text-yellow-800 rounded-2xl p-[12px] mt-[8px]">
      <div className="flex items-start gap-2">
        {/* Yellow dot */}
        <span className="flex-shrink-0 mt-1.5 relative flex h-2 w-2">
          <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-500" />
        </span>
        <Info className="w-5 h-5 flex-shrink-0 mt-0.5 text-yellow-800" aria-hidden="true" />
        <div className="text-[14px] leading-relaxed">
          <span className="block font-bold uppercase tracking-wider text-[11px] mb-0.5 text-yellow-900">
            VISIT PHC RECOMMENDED
          </span>
          {triage.action}
        </div>
      </div>
    </div>
  )
}

export default TriageCard
