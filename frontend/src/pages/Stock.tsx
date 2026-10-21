import { useState, type FormEvent } from 'react'
import { api, messageOf } from '../api'
import { Badge, Banner, Card, Empty, Field, Loading, PageHeader, Table } from '../components/ui'
import { dateTime, quantity } from '../format'
import type { Movement, Product } from '../types'
import { useLoad } from '../useLoad'

const TYPE_LABEL = { stock_in: 'Stock in', sale: 'Sale', adjustment: 'Adjustment' } as const

export default function Stock() {
  const products = useLoad(() => api<Product[]>('/api/products?active=true'), [])
  const [filter, setFilter] = useState('')
  const history = useLoad(
    () => api<Movement[]>(`/api/stock/movements${filter ? `?product_id=${filter}` : ''}`),
    [filter],
  )
  const [inProduct, setInProduct] = useState('')
  const [inQty, setInQty] = useState('')
  const [inNote, setInNote] = useState('')
  const [adjProduct, setAdjProduct] = useState('')
  const [adjQty, setAdjQty] = useState('')
  const [adjReason, setAdjReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  async function run(action: () => Promise<unknown>, done: string, reset: () => void) {
    setError(null)
    setNotice(null)
    try {
      await action()
      setNotice(done)
      reset()
      products.reload()
      history.reload()
    } catch (e) {
      setError(messageOf(e))
    }
  }

  const submitIn = (event: FormEvent) => {
    event.preventDefault()
    if (!inProduct) return setError('Choose a product')
    if (!/^\d+$/.test(inQty.trim())) return setError('Quantity must be above 0')
    return run(
      () =>
        api('/api/stock/in', {
          method: 'POST',
          body: { product_id: inProduct, quantity: Number(inQty), note: inNote || null },
        }),
      'Stock in recorded.',
      () => {
        setInQty('')
        setInNote('')
      },
    )
  }

  const submitAdjustment = (event: FormEvent) => {
    event.preventDefault()
    if (!adjProduct) return setError('Choose a product')
    if (!/^-?\d+$/.test(adjQty.trim())) return setError('Quantity must be a whole number, like -3 or 5')
    return run(
      () =>
        api('/api/stock/adjustments', {
          method: 'POST',
          body: { product_id: adjProduct, quantity: Number(adjQty), reason: adjReason },
        }),
      'Adjustment recorded.',
      () => {
        setAdjQty('')
        setAdjReason('')
      },
    )
  }

  const options = products.data ?? []
  const picker = (value: string, onChange: (v: string) => void) => (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">Choose a product…</option>
      {options.map((p) => (
        <option key={p.id} value={p.id}>
          {p.sku} · {p.name} ({quantity(p.on_hand, p.unit)} on hand)
        </option>
      ))}
    </select>
  )

  return (
    <>
      <PageHeader title="Stock" />
      <Banner message={error ?? products.error ?? history.error} />
      <Banner message={notice} kind="success" />
      <div className="grid">
        <Card title="Stock in">
          <form onSubmit={submitIn}>
            <div className="form">
              <Field label="Product">{picker(inProduct, setInProduct)}</Field>
              <Field label="Quantity received">
                <input inputMode="numeric" value={inQty} onChange={(e) => setInQty(e.target.value)} />
              </Field>
              <Field label="Note (optional)">
                <input value={inNote} onChange={(e) => setInNote(e.target.value)} placeholder="Delivery from Doi Chang Farm" />
              </Field>
            </div>
            <div className="actions">
              <button type="submit">Record stock in</button>
            </div>
          </form>
        </Card>
        <Card title="Adjustment">
          <form onSubmit={submitAdjustment}>
            <div className="form">
              <Field label="Product">{picker(adjProduct, setAdjProduct)}</Field>
              <Field label="Quantity (use − to remove)">
                <input inputMode="numeric" value={adjQty} onChange={(e) => setAdjQty(e.target.value)} placeholder="-3" />
              </Field>
              <Field label="Reason (required)">
                <input value={adjReason} onChange={(e) => setAdjReason(e.target.value)} placeholder="Damaged bags" />
              </Field>
            </div>
            <div className="actions">
              <button type="submit">Record adjustment</button>
            </div>
          </form>
        </Card>
      </div>

      <h2>History</h2>
      <div className="card">
        <Field label="Show movements for">
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="">All products</option>
            {options.map((p) => (
              <option key={p.id} value={p.id}>
                {p.sku}
              </option>
            ))}
          </select>
        </Field>
      </div>
      {history.loading && !history.data && <Loading />}
      {history.data && history.data.length === 0 && <Empty>No stock movements yet.</Empty>}
      {history.data && history.data.length > 0 && (
        <Table>
          <thead>
            <tr>
              <th>When</th>
              <th>Product</th>
              <th>Type</th>
              <th className="num">Quantity</th>
              <th>Reason</th>
              <th>By</th>
            </tr>
          </thead>
          <tbody>
            {history.data.map((m) => (
              <tr key={m.id}>
                <td>{dateTime(m.created_at)}</td>
                <td>{m.sku}</td>
                <td>
                  <Badge tone={m.quantity > 0 ? 'good' : 'neutral'}>{TYPE_LABEL[m.movement_type]}</Badge>
                </td>
                <td className="num">{m.quantity > 0 ? `+${m.quantity}` : m.quantity}</td>
                <td>{m.reason ?? ''}</td>
                <td>{m.user_name}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </>
  )
}
