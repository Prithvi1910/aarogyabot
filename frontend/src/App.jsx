import React from 'react'
import ChatInterface from './components/ChatInterface'
import TriageCard from './components/TriageCard'
import FacilityCard from './components/FacilityCard'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      {/* Top Banner Navigation */}
      <header className="bg-green-700 text-white py-4 px-6 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">🩺</span>
            <div>
              <h1 className="text-xl font-bold tracking-tight">Aarogyabot (आरोग्यबॉट)</h1>
              <p className="text-xs text-green-100">Multilingual Healthcare Assistant</p>
            </div>
          </div>
          <div className="text-sm font-medium bg-green-800 px-3 py-1 rounded-full border border-green-600">
            System Online
          </div>
        </div>
      </header>

      {/* Main Layout Grid */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Chat Component Area (Left Side) */}
        <section className="md:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
          <ChatInterface />
        </section>

        {/* Side Panel: Triage and Nearest Facilities Info (Right Side) */}
        <aside className="space-y-6 flex flex-col">
          <TriageCard />
          <FacilityCard />
        </aside>
      </main>
    </div>
  )
}

export default App
