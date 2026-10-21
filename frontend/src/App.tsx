import { useEffect, useState } from 'react'

type Health = { status: string; db: string }

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setHealth)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main>
      <h1>Siam Bean ERP</h1>
      {error && <p role="alert">Cannot reach the server: {error}</p>}
      {!error && !health && <p>Checking the server…</p>}
      {health && (
        <p>
          Server: {health.status}, database: {health.db}
        </p>
      )}
    </main>
  )
}
