import { useState, type FormEvent } from 'react'
import { api, messageOf } from '../api'
import { useAuth } from '../auth'
import { Badge, Banner, Card, Empty, Field, Loading, PageHeader, Table } from '../components/ui'
import { money, quantity } from '../format'
import type { Product } from '../types'
import { useLoad } from '../useLoad'

type Draft = { sku: string; name: string; unit: string; cost: string; price: string; reorder_level: string }

const blank: Draft = { sku: '', name: '', unit: 'kg', cost: '', price: '', reorder_level: '0' }

function ProductForm({
  product,
  onSaved,
  onCancel,
}: {
  product: Product | null
  onSaved: (message: string) => void
  onCancel: () => void
}) {
  const [draft, setDraft] = useState<Draft>(
    product
      ? {
          sku: product.sku,
          name: product.name,
          unit: product.unit,
          cost: product.cost,
          price: product.price,
          reorder_level: String(product.reorder_level),
        }
      : blank,
  )
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const set = (key: keyof Draft) => (e: { target: { value: string } }) => setDraft({ ...draft, [key]: e.target.value })

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    const body = {
      name: draft.name,
      unit: draft.unit,
      cost: draft.cost,
      price: draft.price,
      reorder_level: draft.reorder_level === '' ? null : Number(draft.reorder_level),
    }
    try {
      if (product) {
        await api(`/api/products/${product.id}`, { method: 'PATCH', body })
        onSaved(`Saved ${product.sku}.`)
      } else {
        await api('/api/products', { method: 'POST', body: { ...body, sku: draft.sku } })
        onSaved(`Created ${draft.sku}.`)
      }
    } catch (e) {
      setError(messageOf(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card title={product ? `Edit ${product.sku}` : 'New product'}>
      <Banner message={error} />
      <form onSubmit={submit}>
        <div className="form">
          <Field label="SKU" hint={product ? 'A SKU cannot be changed' : 'Capital letters, digits and hyphens'}>
            <input value={draft.sku} onChange={set('sku')} disabled={Boolean(product)} placeholder="ARB-1KG" />
          </Field>
          <Field label="Name">
            <input value={draft.name} onChange={set('name')} />
          </Field>
          <Field label="Unit">
            <input value={draft.unit} onChange={set('unit')} />
          </Field>
          <Field label="Cost (THB)">
            <input inputMode="decimal" value={draft.cost} onChange={set('cost')} />
          </Field>
          <Field label="Price (THB, excluding VAT)">
            <input inputMode="decimal" value={draft.price} onChange={set('price')} />
          </Field>
          <Field label="Reorder level">
            <input inputMode="numeric" value={draft.reorder_level} onChange={set('reorder_level')} />
          </Field>
        </div>
        <div className="actions">
          <button type="submit" disabled={busy}>
            {busy ? 'Saving…' : 'Save product'}
          </button>
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </Card>
  )
}

export default function Products() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const { data, error, loading, reload } = useLoad(() => api<Product[]>('/api/products'), [])
  const [editing, setEditing] = useState<Product | 'new' | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  async function setActive(product: Product, active: boolean) {
    setActionError(null)
    try {
      await api(`/api/products/${product.id}`, { method: 'PATCH', body: { active } })
      setNotice(`${product.sku} is now ${active ? 'active' : 'deactivated'}.`)
      reload()
    } catch (e) {
      setActionError(messageOf(e))
    }
  }

  return (
    <>
      <PageHeader title="Products">
        {isAdmin && editing === null && <button onClick={() => setEditing('new')}>New product</button>}
      </PageHeader>
      <Banner message={error ?? actionError} />
      <Banner message={notice} kind="success" />
      {isAdmin && editing !== null && (
        <ProductForm
          key={editing === 'new' ? 'new' : editing.id}
          product={editing === 'new' ? null : editing}
          onCancel={() => setEditing(null)}
          onSaved={(message) => {
            setEditing(null)
            setNotice(message)
            reload()
          }}
        />
      )}
      {loading && !data && <Loading />}
      {data && data.length === 0 && <Empty>No products yet.</Empty>}
      {data && data.length > 0 && (
        <Table>
          <thead>
            <tr>
              <th>SKU</th>
              <th>Name</th>
              <th className="num">On hand</th>
              <th className="num">Reorder level</th>
              <th className="num">Price</th>
              <th>Status</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {data.map((product) => (
              <tr key={product.id} className={product.active ? '' : 'inactive'}>
                <td>{product.sku}</td>
                <td>{product.name}</td>
                <td className="num">
                  {quantity(product.on_hand, product.unit)} {product.low_stock && product.active && <Badge tone="warn">Low stock</Badge>}
                </td>
                <td className="num">{product.reorder_level}</td>
                <td className="num">{money(product.price)}</td>
                <td>{product.active ? <Badge tone="good">Active</Badge> : <Badge tone="neutral">Deactivated</Badge>}</td>
                {isAdmin && (
                  <td>
                    <div className="row-actions">
                      <button className="secondary small" onClick={() => setEditing(product)}>
                        Edit
                      </button>
                      {product.active ? (
                        <button className="danger small" onClick={() => setActive(product, false)}>
                          Deactivate
                        </button>
                      ) : (
                        <button className="secondary small" onClick={() => setActive(product, true)}>
                          Reactivate
                        </button>
                      )}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </>
  )
}
