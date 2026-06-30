import React, { useState, useEffect } from 'react'
import { X, Activity, AlertTriangle, MapPin, RefreshCw, ShieldCheck } from 'lucide-react'

function AlertsDashboard({ onClose }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(false)
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const res = await fetch(`${apiUrl}/surveillance/alerts`)
      if (!res.ok) throw new Error('failed')
      setData(await res.json())
    } catch {
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const maxSymptom = data?.top_symptoms?.[0]?.count || 1

  return (
    <div className="absolute inset-0 z-40 flex flex-col bg-[#f6faf9] animate-fade-in">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-brand-100/70 glass px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-soft">
            <Activity className="h-5 w-5" />
          </div>
          <div className="leading-tight">
            <div className="text-[15px] font-bold text-ink-900">Community Health Alerts</div>
            <div className="text-[11px] font-medium text-ink-500">
              Outbreak surveillance · last {data?.window_days ?? 7} days
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={load}
            className="flex h-9 w-9 items-center justify-center rounded-full text-ink-500 transition-colors hover:bg-brand-50 hover:text-brand-600"
            aria-label="Refresh alerts"
          >
            <RefreshCw className={`h-[18px] w-[18px] ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-full text-ink-500 transition-colors hover:bg-brand-50 hover:text-ink-900"
            aria-label="Close alerts"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </header>

      {/* Body */}
      <div className="flex-1 overflow-y-auto px-4 py-4 chat-scroll">
        {loading && (
          <div className="flex h-40 items-center justify-center text-sm text-ink-500">Loading alerts…</div>
        )}

        {error && !loading && (
          <div className="rounded-2xl bg-rose-50 p-4 text-sm text-rose-700 ring-1 ring-rose-200">
            Could not load surveillance data. Make sure the server is running.
          </div>
        )}

        {data && !loading && !error && (
          <div className="flex flex-col gap-5">
            {/* Summary */}
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-2xl bg-white p-4 shadow-soft ring-1 ring-brand-100/70">
                <div className="text-2xl font-bold text-ink-900">{data.total_reports}</div>
                <div className="mt-0.5 text-[12px] text-ink-500">Reports tracked</div>
              </div>
              <div className="rounded-2xl bg-white p-4 shadow-soft ring-1 ring-brand-100/70">
                <div className="text-2xl font-bold text-brand-600">{data.active_alerts.length}</div>
                <div className="mt-0.5 text-[12px] text-ink-500">Active clusters</div>
              </div>
            </div>

            {/* Active alerts */}
            <section>
              <h3 className="mb-2 px-1 text-[11px] font-semibold uppercase tracking-wider text-ink-500">
                Active outbreak clusters
              </h3>
              {data.active_alerts.length === 0 ? (
                <div className="flex items-center gap-2 rounded-2xl bg-brand-50 p-4 text-sm text-brand-700 ring-1 ring-brand-100">
                  <ShieldCheck className="h-5 w-5 flex-shrink-0" />
                  No unusual symptom clusters detected right now.
                </div>
              ) : (
                <div className="flex flex-col gap-2.5">
                  {data.active_alerts.map((a, i) => {
                    const high = a.severity === 'high'
                    return (
                      <div
                        key={i}
                        className={`rounded-2xl p-3.5 shadow-soft ring-1 ${
                          high ? 'bg-rose-50 ring-rose-200' : 'bg-amber-50 ring-amber-200'
                        }`}
                      >
                        <div className="flex items-start gap-2.5">
                          <span className={`mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg text-white ${high ? 'bg-rose-500' : 'bg-amber-400'}`}>
                            <AlertTriangle className="h-4 w-4" />
                          </span>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between gap-2">
                              <span className={`text-[15px] font-bold ${high ? 'text-rose-800' : 'text-amber-900'}`}>
                                {a.likely_condition || 'Symptom cluster'}
                              </span>
                              <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-white ${high ? 'bg-rose-500' : 'bg-amber-400'}`}>
                                {a.severity}
                              </span>
                            </div>
                            <div className={`mt-1 flex items-center gap-1.5 text-[13px] ${high ? 'text-rose-700' : 'text-amber-800'}`}>
                              <MapPin className="h-3.5 w-3.5" />
                              PIN {a.pincode} · {a.count} reports
                            </div>
                            <div className="mt-1.5 flex flex-wrap gap-1.5">
                              {a.symptoms.map((s) => (
                                <span key={s} className="rounded-full bg-white/70 px-2 py-0.5 text-[11px] font-medium capitalize text-ink-700 ring-1 ring-black/5">
                                  {s}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </section>

            {/* Top symptoms */}
            <section>
              <h3 className="mb-2 px-1 text-[11px] font-semibold uppercase tracking-wider text-ink-500">
                Most reported symptoms
              </h3>
              <div className="flex flex-col gap-2 rounded-2xl bg-white p-3.5 shadow-soft ring-1 ring-brand-100/70">
                {data.top_symptoms.map((s) => (
                  <div key={s.symptom} className="flex items-center gap-3">
                    <span className="w-24 flex-shrink-0 truncate text-[13px] font-medium capitalize text-ink-700">
                      {s.symptom}
                    </span>
                    <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-brand-50">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-brand-400 to-brand-600"
                        style={{ width: `${Math.max(8, (s.count / maxSymptom) * 100)}%` }}
                      />
                    </div>
                    <span className="w-6 flex-shrink-0 text-right text-[12px] font-semibold text-ink-500">{s.count}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* Regions */}
            {data.regions.length > 0 && (
              <section>
                <h3 className="mb-2 px-1 text-[11px] font-semibold uppercase tracking-wider text-ink-500">
                  Reports by area
                </h3>
                <div className="flex flex-wrap gap-2">
                  {data.regions.map((r) => (
                    <span key={r.pincode} className="flex items-center gap-1.5 rounded-full bg-white px-3 py-1.5 text-[13px] font-medium text-ink-700 shadow-soft ring-1 ring-brand-100/70">
                      <MapPin className="h-3.5 w-3.5 text-brand-500" />
                      {r.pincode}
                      <span className="text-ink-400">·</span>
                      <span className="font-bold text-brand-600">{r.count}</span>
                    </span>
                  ))}
                </div>
              </section>
            )}

            <p className="px-1 pb-2 text-[11px] leading-relaxed text-ink-500">
              Built from anonymized symptom signals (no personal data). For early awareness only —
              official outbreak confirmation comes from public-health authorities.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AlertsDashboard
