import { useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, messageOf } from '../api'
import { useAuth } from '../auth'
import { Banner, Card, Empty, Field, Loading, PageHeader, Table } from '../components/ui'
import { date, money, quantity } from '../format'
import type { Invoice } from '../types'
import { useLoad } from '../useLoad'
import { StatusBadge } from './Invoices'

export default function InvoiceDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const canPay = user?.role === 'admin' || user?.role === 'accountant'
  const { data: invoice, error, loading, reload } = useLoad(() => api<Invoice>(`/api/invoices/${id}`), [id])
  const [amount, setAmount] = useState('')
  const [paidOn, setPaidOn] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function pay(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setFormError(null)
    setNotice(null)
    try {
      await api(`/api/invoices/${id}/payments`, {
        method: 'POST',
        body: { amount, paid_on: paidOn || null },
      })
      setNotice(`Payment of ${money(amount)} recorded.`)
      setAmount('')
      setPaidOn('')
      reload()
    } catch (e) {
      setFormError(messageOf(e))
    } finally {
      setBusy(false)
    }
  }

  if (loading && !invoice) return <Loading />
  if (!invoice) return <Banner message={error ?? 'Invoice not found'} />

  return (
    <>
      <PageHeader title={`Invoice ${invoice.number}`}>
        <StatusBadge invoice={invoice} />
        <Link className="button secondary" to="/invoices">
          All invoices
        </Link>
      </PageHeader>
      <Banner message={notice} kind="success" />

      <div className="grid">
        <Card title="Customer">
          <strong>{invoice.customer.name}</strong>
          <br />
          Tax ID {invoice.customer.tax_id}
          <br />
          <span className="muted">Payment terms: {invoice.customer.payment_terms}</span>
        </Card>
        <Card title="Dates">
          Issued {date(invoice.issue_date)}
          <br />
          Due {date(invoice.due_date)}
          <br />
          <span className="muted">From order {invoice.order_number}</span>
        </Card>
      </div>

      <Table>
        <thead>
          <tr>
            <th>Product</th>
            <th className="num">Quantity</th>
            <th className="num">Price (excl. VAT)</th>
            <th className="num">Line total</th>
          </tr>
        </thead>
        <tbody>
          {invoice.lines.map((line) => (
            <tr key={line.sku}>
              <td>
                {line.sku} · {line.name}
              </td>
              <td className="num">{quantity(line.quantity, line.unit)}</td>
              <td className="num">{money(line.unit_price)}</td>
              <td className="num">{money(line.line_total)}</td>
            </tr>
          ))}
        </tbody>
      </Table>
      <div className="totals" aria-label="Invoice totals">
        <span>Subtotal</span>
        <span className="num">{money(invoice.subtotal)}</span>
        <span>VAT 7%</span>
        <span className="num">{money(invoice.vat)}</span>
        <span className="grand">Total</span>
        <span className="grand num">{money(invoice.total)}</span>
        <span>Paid</span>
        <span className="num">{money(invoice.paid)}</span>
        <span className="grand">Balance</span>
        <span className="grand num">{money(invoice.balance)}</span>
      </div>

      <h2>Payments</h2>
      {invoice.payments.length === 0 ? (
        <Empty>No payments recorded yet.</Empty>
      ) : (
        <Table>
          <thead>
            <tr>
              <th>Date</th>
              <th className="num">Amount</th>
              <th>Recorded by</th>
            </tr>
          </thead>
          <tbody>
            {invoice.payments.map((payment) => (
              <tr key={payment.id}>
                <td>{date(payment.paid_on)}</td>
                <td className="num">{money(payment.amount)}</td>
                <td>{payment.recorded_by}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {canPay && invoice.status !== 'paid' && (
        <Card title="Record a payment">
          <Banner message={formError} />
          <form onSubmit={pay}>
            <div className="form">
              <Field label="Amount (THB)">
                <input inputMode="decimal" value={amount} onChange={(e) => setAmount(e.target.value)} />
              </Field>
              <Field label="Payment date (optional)" hint="Today if left empty">
                <input type="date" value={paidOn} onChange={(e) => setPaidOn(e.target.value)} />
              </Field>
            </div>
            <div className="actions">
              <button type="submit" disabled={busy}>
                Record payment
              </button>
              <button type="button" className="secondary" onClick={() => setAmount(invoice.balance)}>
                Fill the full balance
              </button>
            </div>
          </form>
        </Card>
      )}
    </>
  )
}
