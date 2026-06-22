import React from 'react'

function FacilityCard({ facility }) {
  if (!facility) return null

  // Ensure distance_km is formatted nicely as X.X
  const dist = typeof facility.distance_km === 'number' ? facility.distance_km.toFixed(1) : '0.0'

  return (
    <div className="relative bg-white border-l-4 border-green-600 shadow-sm rounded-lg p-[12px] flex justify-between items-start gap-4">
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-gray-900 text-[15px] leading-tight break-words">
          {facility.name}
        </h4>
        <p className="text-gray-500 text-[13px] mt-1">
          {facility.type} • {facility.district}
        </p>
        {facility.phone && (
          <div className="mt-2">
            <a
              href={`tel:${facility.phone}`}
              className="inline-flex items-center text-green-700 hover:underline text-[14px] font-medium min-h-[44px] px-1 focus:outline-none focus:ring-2 focus:ring-green-500 rounded"
              aria-label={`Call ${facility.name} at ${facility.phone}`}
            >
              📞 {facility.phone}
            </a>
          </div>
        )}
      </div>
      <div className="flex-shrink-0">
        <span className="inline-block bg-green-100 text-green-800 text-[12px] font-bold px-2 py-0.5 rounded-full">
          {dist} km
        </span>
      </div>
    </div>
  )
}

export default FacilityCard
