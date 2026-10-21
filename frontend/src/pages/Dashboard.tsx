import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import { Banner, Loading, PageHeader } from '../components/ui'
import type { Dashboard as DashboardData } from '../types'
import { useLoad } from '../useLoad'

const amount = new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

function Thb({ value }: { value: string }) {
  return (
    <>
      {amount.format(Number(value))} <small>THB</small>
    </>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const { data, error, loading } = useLoad(() => api<DashboardData>('/api/dashboard'), [])
  const firstName = user?.full_name.split(' ').slice(-1)[0] ?? ''

  return (
    <>
      <PageHeader title="Dashboard" subtitle={`Welcome back, ${firstName}. Here is how Siam Bean is doing right now.`} />
      <Banner message={error} />
      {loading && !data && <Loading />}
      {data && (
        <div className="grid stats">
          <div className="stat">
            <div className="label">Sales today</div>
            <div className="value">
              <Thb value={data.sales_today} />
            </div>
            <div className="note">Excluding VAT, Bangkok time</div>
          </div>
          <div className={`stat ${data.low_stock_count > 0 ? 'tone-amber' : 'tone-moss'}`}>
            <div className="label">Low-stock products</div>
            <div className="value">{data.low_stock_count}</div>
            <div className="note">
              <Link to="/products">See products</Link>
            </div>
          </div>
          <div className="stat tone-sky">
            <div className="label">Open receivables</div>
            <div className="value">
              <Thb value={data.open_receivables} />
            </div>
            <div className="note">Still owed, including VAT</div>
          </div>
          <div className="stat tone-sky">
            <div className="label">Open invoices</div>
            <div className="value">{data.open_invoices}</div>
            <div className="note">Not fully paid</div>
          </div>
        </div>
      )}
    </>
  )
}
