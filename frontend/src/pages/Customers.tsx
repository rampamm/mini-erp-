import { useEffect, useState, type FormEvent } from 'react'
import { api, messageOf } from '../api'
import { useAuth } from '../auth'
import { Badge, Banner, Card, Empty, Field, Loading, PageHeader, Table } from '../components/ui'
import type { Customer, CustomerPage, PaymentTerms } from '../types'
import { useLoad } from '../useLoad'

const TERMS: PaymentTerms[] = ['Cash', '15 days', '30 days']

function CustomerForm({
  customer,
  onSaved,
  onCancel,
}: {
  customer: Customer | null
  onSaved: (message: string) => void
  onCancel: () => void
}) {
  const [name, setName] = useState(customer?.name ?? '')
  const [taxId, setTaxId] = useState(customer?.tax_id ?? '')
  const [terms, setTerms] = useState<PaymentTerms>(customer?.payment_terms ?? '30 days')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    const body = { name, tax_id: taxId, payment_terms: terms }
    try {
      if (customer) await api(`/api/customers/${customer.id}`, { method: 'PATCH', body })
      else await api('/api/customers', { method: 'POST', body })
      onSaved(`Saved ${name.trim()}.`)
    } catch (e) {
      setError(messageOf(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card title={customer ? `Edit ${customer.name}` : 'New customer'}>
      <Banner message={error} />
      <form onSubmit={submit}>
        <div className="form">
          <Field label="Name">
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </Field>
          <Field label="Tax ID" hint="13 digits">
            <input inputMode="numeric" value={taxId} onChange={(e) => setTaxId(e.target.value)} />
          </Field>
          <Field label="Payment terms">
            <select value={terms} onChange={(e) => setTerms(e.target.value as PaymentTerms)}>
              {TERMS.map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </Field>
        </div>
        <div className="actions">
          <button type="submit" disabled={busy}>
            {busy ? 'Saving…' : 'Save customer'}
          </button>
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </Card>
  )
}

export default function Customers() {
  const { user } = useAuth()
  const canEdit = user?.role === 'admin' || user?.role === 'sales'
  const isAdmin = user?.role === 'admin'
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [editing, setEditing] = useState<Customer | 'new' | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      setQuery(search)
      setPage(1)
    }, 250)
    return () => clearTimeout(timer)
  }, [search])

  const { data, error, loading, reload } = useLoad(
    () => api<CustomerPage>(`/api/customers?q=${encodeURIComponent(query)}&page=${page}`),
    [query, page],
  )

  async function setActive(customer: Customer, active: boolean) {
    setActionError(null)
    try {
      await api(`/api/customers/${customer.id}`, { method: 'PATCH', body: { active } })
      setNotice(`${customer.name} is now ${active ? 'active' : 'deactivated'}.`)
      reload()
    } catch (e) {
      setActionError(messageOf(e))
    }
  }

  const pages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1

  return (
    <>
      <PageHeader title="Customers">
        {canEdit && editing === null && <button onClick={() => setEditing('new')}>New customer</button>}
      </PageHeader>
      <Banner message={error ?? actionError} />
      <Banner message={notice} kind="success" />
      {canEdit && editing !== null && (
        <CustomerForm
          key={editing === 'new' ? 'new' : editing.id}
          customer={editing === 'new' ? null : editing}
          onCancel={() => setEditing(null)}
          onSaved={(message) => {
            setEditing(null)
            setNotice(message)
            reload()
          }}
        />
      )}
      <div className="card">
        <Field label="Search customers by name">
          <input type="search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Type part of a name" />
        </Field>
      </div>
      {loading && !data && <Loading />}
      {data && data.items.length === 0 && <Empty>{query ? 'No customers match your search.' : 'No customers yet.'}</Empty>}
      {data && data.items.length > 0 && (
        <>
          <Table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Tax ID</th>
                <th>Payment terms</th>
                <th>Status</th>
                {canEdit && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {data.items.map((customer) => (
                <tr key={customer.id} className={customer.active ? '' : 'inactive'}>
                  <td>{customer.name}</td>
                  <td>{customer.tax_id}</td>
                  <td>{customer.payment_terms}</td>
                  <td>{customer.active ? <Badge tone="good">Active</Badge> : <Badge tone="neutral">Deactivated</Badge>}</td>
                  {canEdit && (
                    <td>
                      <div className="row-actions">
                        <button className="secondary small" onClick={() => setEditing(customer)}>
                          Edit
                        </button>
                        {customer.active ? (
                          <button className="danger small" onClick={() => setActive(customer, false)}>
                            Deactivate
                          </button>
                        ) : (
                          isAdmin && (
                            <button className="secondary small" onClick={() => setActive(customer, true)}>
                              Reactivate
                            </button>
                          )
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </Table>
          <div className="pager">
            <button className="secondary small" disabled={page <= 1} onClick={() => setPage(page - 1)}>
              Previous
            </button>
            <span className="muted">
              Page {page} of {pages} · {data.total} customers
            </span>
            <button className="secondary small" disabled={page >= pages} onClick={() => setPage(page + 1)}>
              Next
            </button>
          </div>
        </>
      )}
    </>
  )
}
