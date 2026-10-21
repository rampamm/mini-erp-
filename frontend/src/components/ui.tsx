import type { ReactNode } from 'react'

export function Banner({ message, kind = 'error' }: { message: string | null; kind?: 'error' | 'success' }) {
  if (!message) return null
  return (
    <p className={`banner banner-${kind}`} role={kind === 'error' ? 'alert' : 'status'}>
      {message}
    </p>
  )
}

export function Loading({ label = 'Loading…' }: { label?: string }) {
  return <p className="muted">{label}</p>
}

export function Empty({ children }: { children: ReactNode }) {
  return <p className="empty">{children}</p>
}

export function Badge({ tone, children }: { tone: 'good' | 'warn' | 'bad' | 'neutral' | 'info'; children: ReactNode }) {
  return <span className={`badge badge-${tone}`}>{children}</span>
}

export function PageHeader({ title, subtitle, children }: { title: string; subtitle?: string; children?: ReactNode }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      <div className="page-actions">{children}</div>
    </div>
  )
}

export function Field({ label, children, hint }: { label: string; children: ReactNode; hint?: string }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small className="muted">{hint}</small>}
    </label>
  )
}

export function Table({ children }: { children: ReactNode }) {
  return (
    <div className="table-wrap">
      <table>{children}</table>
    </div>
  )
}

export function Card({ title, children }: { title?: string; children: ReactNode }) {
  return (
    <section className="card">
      {title && <h2>{title}</h2>}
      {children}
    </section>
  )
}
