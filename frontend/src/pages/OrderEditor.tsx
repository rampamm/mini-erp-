import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, messageOf } from '../api'
import { Badge, Banner, Card, Empty, Field, Loading, PageHeader, Table } from '../components/ui'
import { dateTime, fromCents, money, quantity, toCents, vatCents } from '../format'
import type { CustomerPage, Order, Product } from '../types'
import { useLoad } from '../useLoad'

type Chosen = { id: string; name: string; tax_id: string; payment_terms: string }
type EditLine = { product_id: string; sku: string; name: string; unit: string; quantity: number; unit_price: string; on_hand: number }

function CustomerPicker({ onPick }: { onPick: (customer: Chosen) => void }) {
  const [text, setText] = useState('')
  const [query, setQuery] = useState('')
  useEffect(() => {
    const timer = setTimeout(() => setQuery(text), 250)
    return () => clearTimeout(timer)
  }, [text])
  const { data, error } = useLoad(
    () => api<CustomerPage>(`/api/customers?active=true&q=${encodeURIComponent(query)}`),
    [query],
  )

  return (
    <div>
      <Field label="Find the customer by name">
        <input type="search" value={text} onChange={(e) => setText(e.target.value)} placeholder="Type part of a name" autoFocus />
      </Field>
      <Banner message={error} />
      {data && data.items.length === 0 && <Empty>No active customers match.</Empty>}
      {data && data.items.length > 0 && (
        <div className="picker-results" role="listbox" aria-label="Matching customers">
          {data.items.map((c) => (
            <button type="button" key={c.id} role="option" aria-selected={false} onClick={() => onPick(c)}>
              {c.name} <span className="muted">· {c.payment_terms}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default function OrderEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const products = useLoad(() => api<Product[]>('/api/products?active=true'), [])
  const [order, setOrder] = useState<Order | null>(null)
  const [customer, setCustomer] = useState<Chosen | null>(null)
  const [lines, setLines] = useState<EditLine[]>([])
  const [loading, setLoading] = useState(Boolean(id))
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [pickProduct, setPickProduct] = useState('')
  const [pickQty, setPickQty] = useState('1')

  function apply(saved: Order) {
    setOrder(saved)
    setCustomer(saved.customer)
    setLines(saved.lines.map(({ line_total: _ignored, ...line }) => line))
  }

  useEffect(() => {
    if (!id) return
    api<Order>(`/api/orders/${id}`)
      .then(apply)
      .catch((e) => setError(messageOf(e)))
      .finally(() => setLoading(false))
  }, [id])

  const readOnly = order?.status === 'confirmed'
  const subtotal = lines.reduce((sum, l) => sum + toCents(l.unit_price) * l.quantity, 0)
  const vat = vatCents(subtotal)

  function addLine() {
    const product = products.data?.find((p) => p.id === pickProduct)
    const qty = Number(pickQty)
    if (!product) return setError('Choose a product to add')
    if (!Number.isInteger(qty) || qty <= 0) return setError('Quantity must be above 0')
    setError(null)
    setLines((current) => {
      const existing = current.find((l) => l.product_id === product.id)
      if (existing) return current.map((l) => (l.product_id === product.id ? { ...l, quantity: l.quantity + qty } : l))
      return [
        ...current,
        {
          product_id: product.id,
          sku: product.sku,
          name: product.name,
          unit: product.unit,
          quantity: qty,
          unit_price: product.price,
          on_hand: product.on_hand,
        },
      ]
    })
    setPickProduct('')
    setPickQty('1')
  }

  function setLineQty(productId: string, value: string) {
    const qty = Number(value)
    setLines((current) =>
      current.map((l) => (l.product_id === productId ? { ...l, quantity: Number.isFinite(qty) ? qty : l.quantity } : l)),
    )
  }

  async function save(): Promise<Order> {
    if (!customer) throw new Error('Choose a customer first')
    const body = { customer_id: customer.id, lines: lines.map((l) => ({ product_id: l.product_id, quantity: l.quantity })) }
    const saved = order
      ? await api<Order>(`/api/orders/${order.id}`, { method: 'PUT', body })
      : await api<Order>('/api/orders', { method: 'POST', body })
    apply(saved)
    if (!order) navigate(`/orders/${saved.id}`, { replace: true })
    return saved
  }

  async function run(action: () => Promise<void>) {
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      await action()
    } catch (e) {
      setError(messageOf(e))
    } finally {
      setBusy(false)
    }
  }

  const saveDraft = () =>
    run(async () => {
      await save()
      setNotice('Draft saved.')
    })

  const confirmOrder = () =>
    run(async () => {
      const saved = await save()
      const confirmed = await api<Order>(`/api/orders/${saved.id}/confirm`, { method: 'POST' })
      apply(confirmed)
      setNotice(`Order ${confirmed.number} confirmed. Invoice ${confirmed.invoice_number} issued.`)
    })

  const remove = () =>
    run(async () => {
      if (!order || !window.confirm('Delete this draft order?')) return
      await api(`/api/orders/${order.id}`, { method: 'DELETE' })
      navigate('/orders')
    })

  if (loading) return <Loading />

  const title = order ? (order.number ? `Order ${order.number}` : 'Draft order') : 'New order'

  return (
    <>
      <PageHeader title={title}>
        {order && (readOnly ? <Badge tone="good">Confirmed</Badge> : <Badge tone="warn">Draft</Badge>)}
        <Link className="button secondary" to="/orders">
          All orders
        </Link>
      </PageHeader>
      <Banner message={error} />
      <Banner message={notice} kind="success" />

      <Card title="Customer">
        {customer ? (
          <p>
            <strong>{customer.name}</strong> <span className="muted">· Payment terms: {customer.payment_terms}</span>{' '}
            {!readOnly && (
              <button className="secondary small" onClick={() => setCustomer(null)}>
                Change
              </button>
            )}
          </p>
        ) : (
          <CustomerPicker onPick={setCustomer} />
        )}
      </Card>

      {!readOnly && (
        <Card title="Add a product">
          <div className="form">
            <Field label="Product">
              <select value={pickProduct} onChange={(e) => setPickProduct(e.target.value)}>
                <option value="">Choose a product…</option>
                {products.data?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.sku} · {p.name} · {money(p.price)} ({quantity(p.on_hand, p.unit)} on hand)
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Quantity">
              <input inputMode="numeric" value={pickQty} onChange={(e) => setPickQty(e.target.value)} />
            </Field>
            <div className="form-action">
              <button type="button" onClick={addLine}>
                Add to order
              </button>
            </div>
          </div>
        </Card>
      )}

      {lines.length === 0 ? (
        <Empty>No products on this order yet.</Empty>
      ) : (
        <Table>
          <thead>
            <tr>
              <th>Product</th>
              <th className="num">Quantity</th>
              <th className="num">Price (excl. VAT)</th>
              <th className="num">Line total</th>
              {!readOnly && <th />}
            </tr>
          </thead>
          <tbody>
            {lines.map((line) => (
              <tr key={line.product_id}>
                <td>
                  {line.sku} · {line.name}
                  {!readOnly && line.quantity > line.on_hand && (
                    <div>
                      <Badge tone="bad">Only {quantity(line.on_hand, line.unit)} on hand</Badge>
                    </div>
                  )}
                </td>
                <td className="num">
                  {readOnly ? (
                    quantity(line.quantity, line.unit)
                  ) : (
                    <input
                      className="qty-input"
                      aria-label={`Quantity of ${line.sku}`}
                      inputMode="numeric"
                      value={line.quantity}
                      onChange={(e) => setLineQty(line.product_id, e.target.value)}
                    />
                  )}
                </td>
                <td className="num">{money(line.unit_price)}</td>
                <td className="num">{money(fromCents(toCents(line.unit_price) * line.quantity))}</td>
                {!readOnly && (
                  <td>
                    <button
                      className="danger small"
                      onClick={() => setLines(lines.filter((l) => l.product_id !== line.product_id))}
                    >
                      Remove
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      <div className="totals" aria-label="Order totals">
        <span>Subtotal</span>
        <span className="num">{money(fromCents(subtotal))}</span>
        <span>VAT 7%</span>
        <span className="num">{money(fromCents(vat))}</span>
        <span className="grand">Total</span>
        <span className="grand num">{money(fromCents(subtotal + vat))}</span>
      </div>

      {readOnly && order?.invoice_id && (
        <p>
          Confirmed {order.confirmed_at && dateTime(order.confirmed_at)}.{' '}
          <Link to={`/invoices/${order.invoice_id}`}>Open invoice {order.invoice_number}</Link>
        </p>
      )}

      {!readOnly && (
        <div className="actions">
          <button onClick={confirmOrder} disabled={busy || lines.length === 0 || !customer}>
            Confirm order and issue invoice
          </button>
          <button className="secondary" onClick={saveDraft} disabled={busy || !customer}>
            Save draft
          </button>
          {order && (
            <button className="danger" onClick={remove} disabled={busy}>
              Delete draft
            </button>
          )}
        </div>
      )}
    </>
  )
}
