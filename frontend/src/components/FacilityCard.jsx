import React from 'react'
import { MapPin, Phone } from 'lucide-react'

function FacilityCard({ facility }) {
  if (!facility) return null

  const dist = typeof facility.distance_km === 'number' ? facility.distance_km.toFixed(1) : '0.0'
  const mapsUrl = `https://maps.google.com/?q=${encodeURIComponent(facility.name + ' ' + facility.district)}`

  return (
    <div className="relative bg-white border-l-4 border-green-600 shadow-sm rounded-lg p-[12px] flex justify-between items-start gap-4">
      <div className="flex-1 min-w-0">
        {/* Facility name with MapPin icon */}
        <h4 className="font-semibold text-gray-900 text-[15px] leading-tight break-words flex items-center gap-1.5">
          <MapPin className="w-4 h-4 text-green-600 flex-shrink-0" aria-hidden="true" />
          {facility.name}
        </h4>
        <p className="text-gray-500 text-[13px] mt-1 ml-5">
          {facility.type} • {facility.district}
        </p>

        {/* Phone number */}
        {facility.phone && (
          <div className="mt-2 ml-5">
            <a
              href={`tel:${facility.phone}`}
              className="inline-flex items-center gap-1.5 text-green-700 hover:underline text-[14px] font-medium min-h-[44px] px-1 focus:outline-none focus:ring-2 focus:ring-green-500 rounded"
              aria-label={`Call ${facility.name} at ${facility.phone}`}
            >
              <Phone className="w-3.5 h-3.5" aria-hidden="true" />
              {facility.phone}
            </a>
          </div>
        )}

        {/* Get Directions link */}
        <a
          href={mapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block ml-5 mt-1 text-blue-600 text-xs underline hover:text-blue-800"
        >
          Get Directions
        </a>
      </div>

      {/* Distance badge */}
      <div className="flex-shrink-0">
        <span className="inline-block bg-green-600 text-white text-[12px] font-bold px-2 py-0.5 rounded-full">
          {dist} km
        </span>
      </div>
    </div>
  )
}

export default FacilityCard
