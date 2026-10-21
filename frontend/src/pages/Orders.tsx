import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { Badge, Banner, Empty, Field, Loading, PageHeader, Table } from '../components/ui'
import { dateTime, money } from '../format'
import type { OrderSummary } from '../types'
import { useLoad } from '../useLoad'

export default function Orders() {
  const [status, setStatus] = useState('')
  const { data, error, loading } = useLoad(
    () => api<OrderSummary[]>(`/api/orders${status ? `?status=${status}` : ''}`),
    [status],
  )

  return (
    <>
      <PageHeader title="Sales orders">
        <Link className="button" to="/orders/new">
          New order
        </Link>
      </PageHeader>
      <Banner message={error} />
      <div className="card">
        <Field label="Show">
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All orders</option>
            <option value="draft">Drafts</option>
            <option value="confirmed">Confirmed</option>
          </select>
        </Field>
      </div>
      {loading && !data && <Loading />}
      {data && data.length === 0 && <Empty>No orders yet. Start with “New order”.</Empty>}
      {data && data.length > 0 && (
        <Table>
          <thead>
            <tr>
              <th>Order</th>
              <th>Customer</th>
              <th>Created</th>
              <th className="num">Total (incl. VAT)</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map((order) => (
              <tr key={order.id}>
                <td>
                  <Link to={`/orders/${order.id}`}>{order.number ?? 'Draft'}</Link>
                </td>
                <td>{order.customer_name}</td>
                <td>{dateTime(order.created_at)}</td>
                <td className="num">{money(order.total)}</td>
                <td>{order.status === 'draft' ? <Badge tone="warn">Draft</Badge> : <Badge tone="good">Confirmed</Badge>}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </>
  )
}
