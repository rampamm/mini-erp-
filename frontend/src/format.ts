const amount = new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

export const money = (value: string | number) => `${amount.format(Number(value))} THB`

export const quantity = (n: number, unit: string) => `${n.toLocaleString('en-US')} ${unit}`

export const date = (value: string) =>
  new Date(`${value.slice(0, 10)}T00:00:00`).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })

export const dateTime = (value: string) =>
  new Date(value).toLocaleString('en-GB', {
    timeZone: 'Asia/Bangkok',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

export const toCents = (price: string) => Math.round(Number(price) * 100)

export const fromCents = (cents: number) => (cents / 100).toFixed(2)

// 7% VAT rounded half-up, the same rule the server applies.
export const vatCents = (subtotalCents: number) => Math.floor((subtotalCents * 7 + 50) / 100)

export const roleLabel = (role: string) => role.charAt(0).toUpperCase() + role.slice(1)
