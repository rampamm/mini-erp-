export type Role = 'admin' | 'sales' | 'warehouse' | 'accountant'

export type User = { id: string; email: string; full_name: string; role: Role; active: boolean }

export type Product = {
  id: string
  sku: string
  name: string
  unit: string
  cost: string
  price: string
  reorder_level: number
  active: boolean
  on_hand: number
  low_stock: boolean
}

export type PaymentTerms = 'Cash' | '15 days' | '30 days'

export type Customer = { id: string; name: string; tax_id: string; payment_terms: PaymentTerms; active: boolean }

export type CustomerPage = { items: Customer[]; total: number; page: number; page_size: number }

export type Movement = {
  id: number
  product_id: string
  sku: string
  movement_type: 'stock_in' | 'sale' | 'adjustment'
  quantity: number
  reason: string | null
  user_name: string
  created_at: string
}

export type OrderLine = {
  product_id: string
  sku: string
  name: string
  unit: string
  quantity: number
  unit_price: string
  line_total: string
  on_hand: number
}

export type Order = {
  id: string
  number: string | null
  status: 'draft' | 'confirmed'
  customer: { id: string; name: string; tax_id: string; payment_terms: string }
  lines: OrderLine[]
  subtotal: string
  vat: string
  total: string
  created_at: string
  confirmed_at: string | null
  invoice_id: string | null
  invoice_number: string | null
}

export type OrderSummary = {
  id: string
  number: string | null
  status: 'draft' | 'confirmed'
  customer_name: string
  total: string
  created_at: string
}

export type InvoiceStatus = 'open' | 'partially_paid' | 'paid'

export type InvoiceSummary = {
  id: string
  number: string
  order_number: string
  customer_name: string
  issue_date: string
  due_date: string
  total: string
  paid: string
  balance: string
  status: InvoiceStatus
  overdue: boolean
}

export type Payment = {
  id: string
  invoice_id: string
  amount: string
  paid_on: string
  recorded_by: string
  created_at: string
}

export type Invoice = InvoiceSummary & {
  customer: { name: string; tax_id: string; payment_terms: string }
  subtotal: string
  vat: string
  lines: { sku: string; name: string; unit: string; quantity: number; unit_price: string; line_total: string }[]
  payments: Payment[]
}

export type Dashboard = {
  sales_today: string
  low_stock_count: number
  open_receivables: string
  open_invoices: number
}
