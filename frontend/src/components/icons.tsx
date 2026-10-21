import type { ReactNode } from 'react'

const paths: Record<string, ReactNode> = {
  dashboard: (
    <>
      <rect x="3" y="3" width="7.5" height="9" rx="1.8" />
      <rect x="13.5" y="3" width="7.5" height="5.5" rx="1.8" />
      <rect x="13.5" y="12" width="7.5" height="9" rx="1.8" />
      <rect x="3" y="15.5" width="7.5" height="5.5" rx="1.8" />
    </>
  ),
  products: (
    <>
      <path d="M21 8.2 12 3 3 8.2v7.6L12 21l9-5.2z" />
      <path d="m3.3 8.4 8.7 5 8.7-5M12 13.4V21" />
    </>
  ),
  customers: (
    <>
      <circle cx="9" cy="8" r="3.5" />
      <path d="M2.5 20c.6-3.6 3.2-5.5 6.5-5.5s5.9 1.9 6.5 5.5" />
      <path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.8c2 .6 3.1 2.3 3.5 5.2" />
    </>
  ),
  stock: (
    <>
      <path d="m12 3 9 4.5-9 4.5-9-4.5z" />
      <path d="m3 12 9 4.5 9-4.5M3 16.5 12 21l9-4.5" />
    </>
  ),
  orders: (
    <>
      <rect x="5" y="4" width="14" height="17" rx="2.2" />
      <path d="M9 4V3h6v1M9 10h6M9 14h6M9 18h3" />
    </>
  ),
  invoices: (
    <>
      <path d="M6 3h9l4 4v14H6z" />
      <path d="M14.5 3v4.5H19M9 12h7M9 16h7" />
    </>
  ),
  accounting: (
    <>
      <rect x="3" y="6" width="18" height="13" rx="2.5" />
      <path d="M3 10h18M16.5 15h1.5" />
      <path d="M6 6V5a2 2 0 0 1 2-2h8" />
    </>
  ),
  users: (
    <>
      <path d="M12 3 4.5 6v5.5c0 4.4 3 8 7.5 9.5 4.5-1.5 7.5-5.1 7.5-9.5V6z" />
      <path d="m9 12 2.2 2.2L15.5 10" />
    </>
  ),
}

export function NavIcon({ name }: { name: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {paths[name]}
    </svg>
  )
}

export function BrandMark() {
  return (
    <svg className="brand-mark" viewBox="0 0 48 48" aria-hidden="true">
      <defs>
        <linearGradient id="bm" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#f0b783" />
          <stop offset="1" stopColor="#a8531c" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="13" fill="url(#bm)" />
      <ellipse cx="24" cy="24" rx="10.5" ry="14" transform="rotate(35 24 24)" fill="#241a14" />
      <path d="M17.5 31.5c4.5-4 8.5-7.5 13-15" stroke="#f3e9db" strokeWidth="2.4" strokeLinecap="round" fill="none" />
    </svg>
  )
}
