# Siam Bean ERP

A small ERP for Siam Bean Co., a Bangkok coffee-bean distributor, that turns a customer order into stock changes, an invoice and a payment record in one system.

## Language

### People and roles

**Role**:
The single job function a user has (Admin, Sales, Warehouse or Accountant), which decides what they can see and do.
_Avoid_: Permission level, user type, group

**Admin**:
The owner's role; can do everything, including managing users and prices.
_Avoid_: Superuser, owner account

### Master data

**Product**:
A coffee item Siam Bean sells, identified by its SKU and carrying a cost, a price and a reorder level.
_Avoid_: Item, article, bean

**SKU**:
The unique, unchanging code of a product, such as `ARB-1KG`.
_Avoid_: Product code, item number

**Customer**:
A café that buys from Siam Bean, identified by name and a required tax ID, with agreed payment terms.
_Avoid_: Client, buyer, account

**Payment Terms**:
How long a customer has to pay after an invoice is issued (Cash, 15 days, 30 days).
_Avoid_: Credit period, due terms

**Deactivated**:
A product or customer that can no longer be used on new documents but stays in the records that already use it.
_Avoid_: Deleted, archived, disabled

### Stock

**Stock Movement**:
One recorded change to a product's stock: positive for stock in, negative for stock out, each with a type and a reason.
_Avoid_: Stock transaction, inventory entry

**Stock In**:
A movement that adds received beans to stock.
_Avoid_: Receipt, restock

**Adjustment**:
A movement, positive or negative, that changes stock for any reason other than stock in or a sale (a physical recount, damaged bags, samples), always with a stated reason.
_Avoid_: Stock edit, correction, stock out, write-off

**On Hand**:
The quantity of a product in the warehouse, defined as the sum of all its stock movements; never typed in by anyone.
_Avoid_: Stock level, inventory count, quantity available

**Reorder Level**:
The on-hand quantity below which a product needs to be bought again.
_Avoid_: Minimum stock, threshold

**Low Stock**:
The state of a product whose on-hand quantity is below its reorder level.
_Avoid_: Out of stock, shortage

### Selling and money

**Sales Order**:
A customer's request for products, in one of two states: Draft (being prepared, no effect on stock) or Confirmed (stock deducted and invoice issued).
_Avoid_: Order, purchase, booking

**Order Line**:
One product, quantity and unit price on a sales order, with the price copied from the product at the time of ordering and excluding VAT.
_Avoid_: Item, row

**Confirm**:
The single act that turns a draft sales order into a confirmed one by deducting stock and issuing its invoice together, or doing nothing at all if it cannot.
_Avoid_: Place, submit, approve

**Invoice**:
The request for payment issued when a sales order is confirmed, showing subtotal, 7% VAT and total; it keeps the customer's name, tax ID and due date as they were on the day it was issued and never changes afterwards.
_Avoid_: Bill, receipt

**Due Date**:
The date an invoice must be paid by, set from the customer's payment terms on the day it is issued.
_Avoid_: Payment date, deadline

**Overdue**:
An invoice past its due date that is not yet fully paid.
_Avoid_: Late, past due

**VAT**:
The 7% value-added tax added on top of an invoice's subtotal.
_Avoid_: Tax, GST

**Payment**:
Money received from a customer against one invoice; may cover all or part of it and is never edited afterwards.
_Avoid_: Receipt, settlement

**Invoice Status**:
Whether an invoice is Open (nothing paid), Partially Paid or Paid, always derived from its payments.
_Avoid_: Payment state

**Open Receivables**:
The total still owed to Siam Bean across all invoices that are not fully paid.
_Avoid_: Debt, outstanding balance, AR

**Sales Today**:
The sum of invoice subtotals, excluding VAT, for invoices issued today in Bangkok time.
_Avoid_: Revenue, turnover, daily total

**Document Number**:
The sequential, never-reused, gap-free identifier of a confirmed sales order (`SO-0001`) or an invoice (`INV-0001`).
_Avoid_: Reference, ID, serial
