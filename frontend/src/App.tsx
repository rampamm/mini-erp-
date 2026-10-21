import type { ReactElement } from 'react'
import { BrowserRouter, Navigate, NavLink, Outlet, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth'
import { Badge, Loading } from './components/ui'
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

const NAV: { to: string; label: string; roles: Role[] }[] = [
  { to: '/', label: 'Dashboard', roles: ALL },
  { to: '/products', label: 'Products', roles: ALL },
  { to: '/customers', label: 'Customers', roles: ['admin', 'sales', 'accountant'] },
  { to: '/stock', label: 'Stock', roles: ['admin', 'warehouse'] },
  { to: '/orders', label: 'Orders', roles: ['admin', 'sales'] },
  { to: '/invoices', label: 'Invoices', roles: ['admin', 'sales', 'accountant'] },
  { to: '/accounting', label: 'Accounting', roles: ['admin', 'accountant'] },
  { to: '/users', label: 'Users', roles: ['admin'] },
]

function Shell() {
  const { user, loading, logout } = useAuth()
  if (loading) return <Loading label="Loading your session…" />
  if (!user) return <Navigate to="/login" replace />

  return (
    <>
      <header className="topbar">
        <span className="brand">Siam Bean ERP</span>
        <nav className="nav" aria-label="Main">
          {NAV.filter((item) => item.roles.includes(user.role)).map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'}>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="whoami">
          <span>{user.full_name}</span>
          <Badge tone="info">{roleLabel(user.role)}</Badge>
          <button className="secondary small" onClick={logout}>
            Log out
          </button>
        </div>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
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
