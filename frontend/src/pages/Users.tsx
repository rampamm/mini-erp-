import { useState, type FormEvent } from 'react'
import { api, messageOf } from '../api'
import { useAuth } from '../auth'
import { Badge, Banner, Card, Field, Loading, PageHeader, Table } from '../components/ui'
import { roleLabel } from '../format'
import type { Role, User } from '../types'
import { useLoad } from '../useLoad'

const ROLES: Role[] = ['admin', 'sales', 'warehouse', 'accountant']

export default function Users() {
  const { user: me } = useAuth()
  const { data, error, loading, reload } = useLoad(() => api<User[]>('/api/users'), [])
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState<Role>('sales')
  const [password, setPassword] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  async function create(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setNotice(null)
    try {
      await api('/api/users', { method: 'POST', body: { email, full_name: fullName, role, password } })
      setNotice(`Created ${fullName.trim()}. They can log in now.`)
      setEmail('')
      setFullName('')
      setPassword('')
      reload()
    } catch (e) {
      setFormError(messageOf(e))
    }
  }

  async function update(target: User, body: Partial<Pick<User, 'role' | 'active'>>) {
    setFormError(null)
    setNotice(null)
    try {
      await api(`/api/users/${target.id}`, { method: 'PATCH', body })
      reload()
    } catch (e) {
      setFormError(messageOf(e))
    }
  }

  return (
    <>
      <PageHeader title="Users" />
      <Banner message={formError ?? error} />
      <Banner message={notice} kind="success" />
      <Card title="Add a user">
        <form onSubmit={create}>
          <div className="form">
            <Field label="Name">
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </Field>
            <Field label="Email">
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </Field>
            <Field label="Role">
              <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {roleLabel(r)}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Temporary password" hint="At least 8 characters">
              <input type="text" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="off" />
            </Field>
          </div>
          <div className="actions">
            <button type="submit">Create user</button>
          </div>
        </form>
      </Card>
      {loading && !data && <Loading />}
      {data && (
        <Table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((u) => (
              <tr key={u.id} className={u.active ? '' : 'inactive'}>
                <td>{u.full_name}</td>
                <td>{u.email}</td>
                <td>
                  <select
                    aria-label={`Role for ${u.full_name}`}
                    value={u.role}
                    disabled={u.id === me?.id}
                    onChange={(e) => update(u, { role: e.target.value as Role })}
                  >
                    {ROLES.map((r) => (
                      <option key={r} value={r}>
                        {roleLabel(r)}
                      </option>
                    ))}
                  </select>
                </td>
                <td>{u.active ? <Badge tone="good">Active</Badge> : <Badge tone="neutral">Deactivated</Badge>}</td>
                <td>
                  {u.id !== me?.id &&
                    (u.active ? (
                      <button className="danger small" onClick={() => update(u, { active: false })}>
                        Deactivate
                      </button>
                    ) : (
                      <button className="secondary small" onClick={() => update(u, { active: true })}>
                        Reactivate
                      </button>
                    ))}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </>
  )
}
