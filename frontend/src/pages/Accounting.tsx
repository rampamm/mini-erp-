import { Link } from 'react-router-dom'
import { api } from '../api'
import { Banner, Empty, Loading, PageHeader, Table } from '../components/ui'
import { date, money } from '../format'
import type { InvoiceSummary } from '../types'
import { useLoad } from '../useLoad'
import { StatusBadge } from './Invoices'

type Receivables = { items: InvoiceSummary[]; total_open: string }

export default function Accounting() {
  const { data, error, loading } = useLoad(() => api<Receivables>('/api/accounting/receivables'), [])

  return (
    <>
      <PageHeader title="Accounting: who still owes us" />
      <Banner message={error} />
      {loading && !data && <Loading />}
      {data && (
        <>
          <div className="stat" style={{ marginBottom: '1rem' }}>
            <div className="label">Total still owed</div>
            <div className="value">{money(data.total_open)}</div>
            <div className="note">Including VAT, across {data.items.length} invoices</div>
          </div>
          {data.items.length === 0 ? (
            <Empty>Nobody owes anything. All invoices are paid.</Empty>
          ) : (
            <Table>
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Customer</th>
                  <th>Due</th>
                  <th className="num">Balance</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((invoice) => (
                  <tr key={invoice.id}>
                    <td>
                      <Link to={`/invoices/${invoice.id}`}>{invoice.number}</Link>
                    </td>
                    <td>{invoice.customer_name}</td>
                    <td>{date(invoice.due_date)}</td>
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
      )}
    </>
  )
}
