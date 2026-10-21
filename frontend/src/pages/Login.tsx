import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { messageOf } from '../api'
import { useAuth } from '../auth'
import { BrandMark } from '../components/icons'
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
    <div className="login-page">
      <section className="login-art">
        <div className="brand">
          <BrandMark />
          <span className="brand-name">
            Siam Bean<small>ERP</small>
          </span>
        </div>
        <div>
          <p className="login-tagline">
            From roastery to invoice, <em>in one place.</em>
          </p>
          <ul className="login-points">
            <li>Orders that update stock the moment they are confirmed</li>
            <li>Numbered invoices with VAT worked out for you</li>
            <li>Always know who still owes you money</li>
          </ul>
        </div>
        <span className="muted" style={{ color: 'rgb(243 233 219 / 0.55)', fontSize: '0.85rem' }}>
          Bangkok · Importing and roasting since day one
        </span>
      </section>

      <section className="login-panel">
        <div className="login-box">
          <h1>Welcome back</h1>
          <p className="muted">Log in to take orders, track stock and send invoices.</p>
          <div style={{ marginTop: '1.25rem' }}>
            <Banner message={error} />
          </div>
          <form className="login-form" onSubmit={submit}>
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
            <button type="submit" disabled={busy}>
              {busy ? 'Logging in…' : 'Log in'}
            </button>
          </form>
          <p className="demo-title">Demo accounts · password demo1234</p>
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
      </section>
    </div>
  )
}
