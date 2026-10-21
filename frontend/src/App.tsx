import type { ReactElement } from 'react'
import { BrowserRouter, Navigate, NavLink, Outlet, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth'
import { BrandMark, NavIcon } from './components/icons'
import { Loading } from './components/ui'
import { roleLabel } from './format'
import type { Role } from './types'
import AccessDenied from './pages/AccessDenied'
import Accounting from './pages/Accounting'
import Customers from './pages/Customers'
import Dashboard from './pages/Dashboard'
import InvoiceDetail from './pages/InvoiceDetail'
import Invoices from './pages/Invoices'
import Login from './pages/Login'
import NotFound from './pages/NotFound'
import OrderEditor from './pages/OrderEditor'
import Orders from './pages/Orders'
import Products from './pages/Products'
import Stock from './pages/Stock'
import Users from './pages/Users'

const ALL: Role[] = ['admin', 'sales', 'warehouse', 'accountant']

const NAV: { to: string; label: string; icon: string; roles: Role[] }[] = [
  { to: '/', label: 'Dashboard', icon: 'dashboard', roles: ALL },
  { to: '/products', label: 'Products', icon: 'products', roles: ALL },
  { to: '/customers', label: 'Customers', icon: 'customers', roles: ['admin', 'sales', 'accountant'] },
  { to: '/stock', label: 'Stock', icon: 'stock', roles: ['admin', 'warehouse'] },
  { to: '/orders', label: 'Orders', icon: 'orders', roles: ['admin', 'sales'] },
  { to: '/invoices', label: 'Invoices', icon: 'invoices', roles: ['admin', 'sales', 'accountant'] },
  { to: '/accounting', label: 'Accounting', icon: 'accounting', roles: ['admin', 'accountant'] },
  { to: '/users', label: 'Users', icon: 'users', roles: ['admin'] },
]

function Shell() {
  const { user, loading, logout } = useAuth()
  if (loading) return <Loading label="Loading your session…" />
  if (!user) return <Navigate to="/login" replace />

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <BrandMark />
          <span className="brand-name">
            Siam Bean<small>ERP</small>
          </span>
        </div>
        <nav className="nav" aria-label="Main">
          {NAV.filter((item) => item.roles.includes(user.role)).map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'}>
              <NavIcon name={item.icon} />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="whoami">
          <div className="avatar" aria-hidden="true">
            {user.full_name.trim().split(' ').slice(-1)[0].charAt(0).toUpperCase()}
          </div>
          <div className="who">{user.full_name}</div>
          <div className="role">{roleLabel(user.role)}</div>
          <button className="secondary small" onClick={logout}>
            Log out
          </button>
        </div>
      </aside>
      <main className="container">
        <Outlet />
      </main>
    </div>
  )
}

function Guard({ roles, children }: { roles: Role[]; children: ReactElement }) {
  const { user } = useAuth()
  if (!user || !roles.includes(user.role)) return <AccessDenied />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<Shell />}>
            <Route index element={<Dashboard />} />
            <Route path="products" element={<Products />} />
            <Route
              path="customers"
              element={
                <Guard roles={['admin', 'sales', 'accountant']}>
                  <Customers />
                </Guard>
              }
            />
            <Route
              path="stock"
              element={
                <Guard roles={['admin', 'warehouse']}>
                  <Stock />
                </Guard>
              }
            />
            <Route
              path="orders"
              element={
                <Guard roles={['admin', 'sales']}>
                  <Orders />
                </Guard>
              }
            />
            <Route
              path="orders/new"
              element={
                <Guard roles={['admin', 'sales']}>
                  <OrderEditor />
                </Guard>
              }
            />
            <Route
              path="orders/:id"
              element={
                <Guard roles={['admin', 'sales']}>
                  <OrderEditor />
                </Guard>
              }
            />
            <Route
              path="invoices"
              element={
                <Guard roles={['admin', 'sales', 'accountant']}>
                  <Invoices />
                </Guard>
              }
            />
            <Route
              path="invoices/:id"
              element={
                <Guard roles={['admin', 'sales', 'accountant']}>
                  <InvoiceDetail />
                </Guard>
              }
            />
            <Route
              path="accounting"
              element={
                <Guard roles={['admin', 'accountant']}>
                  <Accounting />
                </Guard>
              }
            />
            <Route
              path="users"
              element={
                <Guard roles={['admin']}>
                  <Users />
                </Guard>
              }
            />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
