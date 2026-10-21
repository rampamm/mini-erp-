import { Link } from 'react-router-dom'
import { api } from '../api'
import { Banner, Loading, PageHeader } from '../components/ui'
import { money } from '../format'
import type { Dashboard as DashboardData } from '../types'
import { useLoad } from '../useLoad'

export default function Dashboard() {
  const { data, error, loading } = useLoad(() => api<DashboardData>('/api/dashboard'), [])

  return (
    <>
      <PageHeader title="Dashboard" />
      <Banner message={error} />
      {loading && !data && <Loading />}
      {data && (
        <div className="grid">
          <div className="stat">
            <div className="label">Sales today</div>
            <div className="value">{money(data.sales_today)}</div>
            <div className="note">Excluding VAT, Bangkok time</div>
          </div>
          <div className="stat">
            <div className="label">Low-stock products</div>
            <div className="value">{data.low_stock_count}</div>
            <div className="note">
              <Link to="/products">See products</Link>
            </div>
          </div>
          <div className="stat">
            <div className="label">Open receivables</div>
            <div className="value">{money(data.open_receivables)}</div>
            <div className="note">Still owed, including VAT</div>
          </div>
          <div className="stat">
            <div className="label">Open invoices</div>
            <div className="value">{data.open_invoices}</div>
            <div className="note">Not fully paid</div>
          </div>
        </div>
      )}
    </>
  )
}
