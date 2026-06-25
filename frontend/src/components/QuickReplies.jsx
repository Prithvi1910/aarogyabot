import React from 'react'

function QuickReplies({ onSelect, visible }) {
  if (!visible) return null

  const chips = [
    "Common Symptoms",
    "Find Nearest PHC",
    "Disease Prevention",
    "Emergency Signs"
  ]

  return (
    <div className="flex flex-wrap gap-2 px-4 pb-3">
      {chips.map((chipText) => (
        <button
          key={chipText}
          type="button"
          onClick={() => onSelect(chipText)}
          className="rounded-full border border-green-600 text-green-700 bg-white hover:bg-green-50 px-4 py-2 text-sm cursor-pointer min-h-[44px] flex items-center"
        >
          {chipText}
        </button>
      ))}
    </div>
  )
}

export default QuickReplies
