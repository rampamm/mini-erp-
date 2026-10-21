import { expect, test, type Page } from '@playwright/test'

async function logIn(page: Page, email: string) {
  await page.goto('/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password').fill('demo1234')
  await page.getByRole('button', { name: 'Log in', exact: true }).click()
  await expect(page.getByRole('navigation', { name: 'Main' })).toBeVisible()
}

async function logOut(page: Page) {
  await page.getByRole('button', { name: 'Log out' }).click()
  await expect(page).toHaveURL(/\/login/)
}

async function chooseProduct(page: Page, sku: string) {
  const select = page.getByLabel('Product')
  const value = await select.locator('option', { hasText: sku }).getAttribute('value')
  await select.selectOption(value!)
}

test.describe.configure({ mode: 'serial' })

test('a Sales user opening the Accounting screen sees the access-denied page', async ({ page }) => {
  await logIn(page, 'nok@siambean.test')
  await expect(page.getByRole('link', { name: 'Accounting' })).toHaveCount(0)

  await page.goto('/accounting')

  await expect(page.getByRole('heading', { name: 'Access denied' })).toBeVisible()
})

test('a Warehouse user cannot open the orders screen', async ({ page }) => {
  await logIn(page, 'lek@siambean.test')

  await page.goto('/orders')

  await expect(page.getByRole('heading', { name: 'Access denied' })).toBeVisible()
})

test('Café Lune orders 20 kg: order, stock, invoice, payment, dashboard', async ({ page }) => {
  // Sales takes the order
  await logIn(page, 'nok@siambean.test')
  await page.getByRole('link', { name: 'Orders' }).click()
  await page.getByRole('link', { name: 'New order' }).click()

  await page.getByLabel('Find the customer by name').fill('lune')
  await page.getByRole('option', { name: /Café Lune/ }).click()
  await chooseProduct(page, 'ARB-1KG')
  await page.getByLabel('Quantity', { exact: true }).fill('20')
  await page.getByRole('button', { name: 'Add to order' }).click()
  await expect(page.locator('.totals')).toContainText('9,630.00 THB')

  await page.getByRole('button', { name: 'Confirm order and issue invoice' }).click()
  await expect(page.getByText('Order SO-0001 confirmed. Invoice INV-0001 issued.')).toBeVisible()

  await page.getByRole('link', { name: 'Products' }).click()
  await expect(page.getByRole('row', { name: /ARB-1KG/ })).toContainText('150 kg')

  await page.getByRole('link', { name: 'Invoices' }).click()
  await page.getByRole('link', { name: 'INV-0001' }).click()
  await expect(page.locator('.totals')).toContainText('9,630.00 THB')
  await logOut(page)

  // Accountant records the payment
  await logIn(page, 'fon@siambean.test')
  await page.getByRole('link', { name: 'Accounting' }).click()
  await expect(page.getByText('Total still owed').locator('..')).toContainText('9,630.00 THB')
  await page.getByRole('link', { name: 'INV-0001' }).click()
  await page.getByRole('button', { name: 'Fill the full balance' }).click()
  await page.getByRole('button', { name: 'Record payment' }).click()
  await expect(page.getByText('Payment of 9,630.00 THB recorded.')).toBeVisible()
  await expect(page.getByText('Paid', { exact: true }).first()).toBeVisible()

  // The dashboard agrees
  await page.getByRole('link', { name: 'Dashboard' }).click()
  await expect(page.getByText('Open receivables').locator('..')).toContainText('0.00 THB')
  await expect(page.getByText('Open invoices').locator('..')).toContainText('0')
})

test('too little stock shows the SKU and changes nothing', async ({ page }) => {
  await logIn(page, 'nok@siambean.test')
  await page.goto('/orders/new')
  await page.getByLabel('Find the customer by name').fill('brew')
  await page.getByRole('option', { name: /Brew Lab Ari/ }).click()
  await chooseProduct(page, 'ROB-1KG')
  await page.getByLabel('Quantity', { exact: true }).fill('36')
  await page.getByRole('button', { name: 'Add to order' }).click()

  await page.getByRole('button', { name: 'Confirm order and issue invoice' }).click()

  await expect(page.getByRole('alert')).toContainText('Not enough stock for ROB-1KG')
  await page.getByRole('link', { name: 'Products' }).click()
  await expect(page.getByRole('row', { name: /ROB-1KG/ })).toContainText('35 kg')
})
