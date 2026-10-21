import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { messageOf } from '../api'
import { useAuth } from '../auth'
import { Banner, Field } from '../components/ui'

const DEMO = [
  { email: 'somchai@siambean.test', label: 'Somchai · Admin' },
  { email: 'nok@siambean.test', label: 'Nok · Sales' },
  { email: 'lek@siambean.test', label: 'Lek · Warehouse' },
  { email: 'fon@siambean.test', label: 'Fon · Accountant' },
]

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/" replace />

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await login(email, password)
      navigate('/', { replace: true })
    } catch (e) {
      setError(messageOf(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login">
      <h1>Siam Bean ERP</h1>
      <p className="muted">Log in to take orders, track stock and send invoices.</p>
      <Banner message={error} />
      <form className="card" onSubmit={submit}>
        <div className="form">
          <Field label="Email">
            <input type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </Field>
          <Field label="Password">
            <input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </Field>
        </div>
        <div className="actions">
          <button type="submit" disabled={busy}>
            {busy ? 'Logging in…' : 'Log in'}
          </button>
        </div>
      </form>
      <p className="muted">Demo accounts (password demo1234):</p>
      <div className="demo-accounts">
        {DEMO.map((account) => (
          <button
            key={account.email}
            type="button"
            className="secondary small"
            onClick={() => {
              setEmail(account.email)
              setPassword('demo1234')
            }}
          >
            {account.label}
          </button>
        ))}
      </div>
    </div>
  )
}
