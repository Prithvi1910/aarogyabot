import React from 'react'
import { MapPin, Phone } from 'lucide-react'

function FacilityCard({ facility }) {
  if (!facility) return null

  const dist = typeof facility.distance_km === 'number' ? facility.distance_km.toFixed(1) : '0.0'
  const mapsUrl = `https://maps.google.com/?q=${encodeURIComponent(facility.name + ' ' + facility.district)}`

  return (
    <div className="flex items-start justify-between gap-3 rounded-2xl bg-white p-3.5 shadow-soft ring-1 ring-brand-100/70">
      <div className="min-w-0 flex-1">
        {/* Facility name with MapPin icon */}
        <h4 className="flex items-center gap-2 break-words text-[15px] font-semibold leading-tight text-ink-900">
          <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
            <MapPin className="h-4 w-4" aria-hidden="true" />
          </span>
          {facility.name}
        </h4>
        <p className="ml-9 mt-1 text-[13px] text-ink-500">
          {facility.type} • {facility.district}
        </p>

        <div className="ml-9 mt-2 flex flex-wrap items-center gap-x-4 gap-y-1">
          {/* Phone number */}
          {facility.phone && (
            <a
              href={`tel:${facility.phone}`}
              className="inline-flex items-center gap-1.5 rounded text-[14px] font-medium text-brand-700 hover:underline focus:outline-none focus:ring-2 focus:ring-brand-300"
              aria-label={`Call ${facility.name} at ${facility.phone}`}
            >
              <Phone className="h-3.5 w-3.5" aria-hidden="true" />
              {facility.phone}
            </a>
          )}

          {/* Get Directions link */}
          <a
            href={mapsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs font-medium text-brand-600 hover:text-brand-700 hover:underline"
          >
            Get Directions →
          </a>
        </div>
      </div>

      {/* Distance badge */}
      <span className="flex-shrink-0 rounded-full bg-brand-600 px-2.5 py-1 text-[12px] font-bold text-white">
        {dist} km
      </span>
    </div>
  )
}

export default FacilityCard
