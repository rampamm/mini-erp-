import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { Badge, Banner, Empty, Field, Loading, PageHeader, Table } from '../components/ui'
import { date, money } from '../format'
import type { InvoiceSummary } from '../types'
import { useLoad } from '../useLoad'

export function StatusBadge({ invoice }: { invoice: Pick<InvoiceSummary, 'status' | 'overdue'> }) {
  return (
    <>
      {invoice.status === 'paid' && <Badge tone="good">Paid</Badge>}
      {invoice.status === 'partially_paid' && <Badge tone="info">Partially paid</Badge>}
      {invoice.status === 'open' && <Badge tone="neutral">Open</Badge>}{' '}
      {invoice.overdue && <Badge tone="bad">Overdue</Badge>}
    </>
  )
}

export default function Invoices() {
  const [status, setStatus] = useState('')
  const { data, error, loading } = useLoad(
    () => api<InvoiceSummary[]>(`/api/invoices${status ? `?status=${status}` : ''}`),
    [status],
  )

  return (
    <>
      <PageHeader title="Invoices" />
      <Banner message={error} />
      <div className="card">
        <Field label="Show">
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All invoices</option>
            <option value="open">Open</option>
            <option value="partially_paid">Partially paid</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
          </select>
        </Field>
      </div>
      {loading && !data && <Loading />}
      {data && data.length === 0 && <Empty>{status ? 'No invoices with this status.' : 'No invoices yet.'}</Empty>}
      {data && data.length > 0 && (
        <Table>
          <thead>
            <tr>
              <th>Invoice</th>
              <th>Customer</th>
              <th>Issued</th>
              <th>Due</th>
              <th className="num">Total</th>
              <th className="num">Balance</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map((invoice) => (
              <tr key={invoice.id}>
                <td>
                  <Link to={`/invoices/${invoice.id}`}>{invoice.number}</Link>
                </td>
                <td>{invoice.customer_name}</td>
                <td>{date(invoice.issue_date)}</td>
                <td>{date(invoice.due_date)}</td>
                <td className="num">{money(invoice.total)}</td>
                <td className="num">{money(invoice.balance)}</td>
                <td>
                  <StatusBadge invoice={invoice} />
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </>
  )
}
