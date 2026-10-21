Status: ready-for-agent

# Mini ERP for Siam Bean Co.

## Problem Statement

Siam Bean Co. is a five-person coffee-bean distributor in Bangkok that sells 1 kg bags to about 80 cafés. Orders arrive by LINE and phone, and sales staff retype them into a spreadsheet. Stock lives in a second spreadsheet that never agrees with the first. Invoices are made by hand in Word and numbered manually. The owner's words: stock is always wrong, each invoice takes an hour and the numbers get mixed up, nobody knows who still owes money, sales promise beans that are not there, and anyone can change anything.

## Solution

One web system where a Sales order, once confirmed, deducts stock and issues a numbered Invoice in a single step, an Accountant records Payments against Invoices, and the owner sees live numbers on a Dashboard. Each of the four Roles (Admin, Sales, Warehouse, Accountant) sees and does only what they are allowed to, and the server enforces it. It is deployed at a public URL that works on a phone.

## User Stories

### Login and Roles

1. As an Admin, I want to create a user account and assign it one Role, so that each person only sees and does what they are allowed to.
2. As an Admin, I want there to be no public sign-up, so that nobody outside the company can get in.
3. As an Admin, I want to deactivate a user, so that a person who leaves can no longer log in.
4. As a staff member, I want to log in with my email and password, so that the system knows who I am.
5. As a staff member, I want to log out, so that nobody else uses my session on a shared computer.
6. As a Sales user, I want to see an access-denied page when I open the Accounting screen, so that I know I am not allowed there.
7. As the owner, I want the server to return `403` when the wrong Role calls an endpoint directly, so that hiding a button is not the only protection.
8. As a Warehouse user, I want the confirm-order action to be refused when I call it directly, so that only Sales and Admin can confirm.
9. As an Admin, I want every screen and action available to me, so that I can run and fix anything.
10. As a demo presenter, I want one seeded demo account per Role listed in the README, so that I can show two Roles live.
11. As any logged-in user, I want to see the Dashboard, so that I know how the business is doing.
12. As a user whose session has expired, I want to be sent to the login page, so that I am not left on a broken screen.

### Products

13. As an Admin, I want to create a Product with SKU, name, unit, cost, price and Reorder Level, so that it can be sold.
14. As an Admin, I want an error saying "SKU already exists" when I reuse a SKU, so that two Products never share a code.
15. As an Admin, I want a SKU limited to capital letters, digits and hyphens and fixed after creation, so that codes stay consistent.
16. As an Admin, I want an error when a price or cost is below 0, so that bad prices cannot be saved.
17. As an Admin, I want to edit a Product's name, price, cost and Reorder Level, so that master data stays current.
18. As an Admin, I want changing a price to leave old orders and Invoices untouched, so that history never changes.
19. As an Admin, I want to deactivate a Product that has documents, so that it cannot be sold again but history still shows it.
20. As an Admin, I want to reactivate a deactivated Product, so that a mistake can be undone.
21. As an Admin, I want a deactivated Product to keep its SKU reserved, so that the code is never reused for a different item.
22. As a Sales user, I want to view Products with their On Hand quantity, so that I do not promise beans we do not have.
23. As a Warehouse user, I want to view Products with their On Hand quantity, so that I know what is in the warehouse.
24. As an Accountant, I want to view Products, so that I can read Invoice lines in context.
25. As a user with view-only access, I want no edit controls on Products, so that I do not try things I cannot do.
26. As a Warehouse user, I want a Low Stock badge on any Product below its Reorder Level, so that I can reorder in time.
27. As a Warehouse user, I want Robusta (ROB-1KG, 35 on hand against 40) to show Low Stock from the start, so that the sample data demonstrates the feature.
28. As a user, I want the Product list to show money as `450.00 THB` and quantities with their unit, so that numbers read like money.

### Customers

29. As a Sales user, I want to create a Customer with name, tax ID and Payment Terms, so that I can sell to a new café.
30. As a Sales user, I want an error "Tax ID must be 13 digits" for a bad tax ID, so that I know exactly what to fix.
31. As a Sales user, I want to edit a Customer, so that details stay correct.
32. As a Sales user, I want to deactivate a Customer, so that a café we stopped serving cannot get new orders.
33. As an Admin, I want to reactivate a Customer, so that a returning café can order again.
34. As a Sales user, I want to search Customers by part of a name, case-insensitive, so that I find one quickly.
35. As a Sales user, I want the search to respond within 1 second with 200 Customers, so that it feels instant.
36. As a Sales user, I want results at most 20 rows per page sorted by name, so that the list is easy to scan.
37. As a Sales user, I want an empty search to say "No customers match", so that I know the search worked.
38. As an Accountant, I want to view Customers, so that I know who an Invoice is for.
39. As a Warehouse user, I want no access to Customer editing, so that master data stays controlled.
40. As an Admin, I want Payment Terms of Cash, 15 days or 30 days on each Customer, so that Due Dates are right.

### Sales Orders

41. As a Sales user, I want to create a draft Sales Order for an active Customer, so that I can prepare an order from a LINE message.
42. As a Sales user, I want to add Order Lines by choosing an active Product and a quantity, so that I build the order.
43. As a Sales user, I want the line price filled from the Product's current price and not editable, so that prices stay under Admin control.
44. As a Sales user, I want the quantity to be above 0, so that nonsense lines are rejected with a clear message.
45. As a Sales user, I want to see the line total and the order subtotal, VAT and total while I edit, so that I can read the numbers back to the café.
46. As a Sales user, I want to edit and delete a draft Sales Order, so that mistakes before confirming cost nothing.
47. As a Sales user, I want a draft to have no document number, so that numbers are only used by real orders.
48. As a Sales user, I want deactivated Products and Customers hidden from the pickers, so that I cannot order from them.
49. As a Sales user, I want to see current On Hand next to each Product while I add lines, so that I can avoid over-promising.
50. As a Sales user, I want to confirm a draft Sales Order, so that stock is deducted and an Invoice is issued.
51. As a Sales user, I want the confirm action to give the order a number like `SO-0001`, so that it can be referred to on the phone.
52. As a Sales user, I want to see "Not enough stock for ARB-1KG" when a line exceeds On Hand, so that I know which product is short.
53. As a Sales user, I want a failed confirm to change nothing, so that no half-done order is left behind.
54. As a Sales user, I want a confirmed Sales Order to be read-only, so that it cannot be altered after the Invoice is issued.
55. As a Sales user, I want to list Sales Orders filtered by Draft or Confirmed, so that I find open work.
56. As a Warehouse user, I want no way to confirm an order, so that stock is not deducted without Sales.
57. As the owner, I want a mistaken confirmed order to be fixed by an Adjustment with a note, so that nothing is deleted from the records.
58. As a Sales user, I want an order with no lines to be rejected on confirm with a clear message, so that empty Invoices cannot exist.

### Confirm to Invoice

59. As the owner, I want confirming 20 kg of `ARB-1KG` at 450 THB for Café Lune to leave 150 kg On Hand, so that stock is correct immediately.
60. As the owner, I want that same order to create `INV-0001` with subtotal 9,000.00, VAT 630.00 and total 9,630.00 THB, so that the Invoice is exactly right.
61. As an Accountant, I want an Invoice to contain the same lines as the order, so that I can verify it against what was sold.
62. As an Accountant, I want VAT calculated once on the Invoice subtotal at 7% rounded to 2 decimals, so that totals do not drift.
63. As an Accountant, I want Invoice numbers sequential with no gaps and never reused, so that the books reconcile.
64. As an Accountant, I want the Invoice to keep the Customer's name, tax ID and Due Date from the day of issue, so that later edits cannot change an issued Invoice.
65. As the owner, I want confirming to create the stock movements and the Invoice in one all-or-nothing step, so that the numbers cannot disagree.
66. As the owner, I want two people confirming at the same moment to never oversell the same stock, so that On Hand cannot go negative.
67. As an Accountant, I want a Due Date set from the Customer's Payment Terms (Cash = same day), so that I know when money is expected.
68. As an Accountant, I want an Invoice past its Due Date and not fully paid to show as Overdue, so that I can chase it.
69. As a Sales user, I want to open the Invoice from the confirmed order, so that I can check it.
70. As an Accountant, I want to list Invoices filtered by Open, Partially Paid, Paid and Overdue, so that I see who owes money.

### Stock

71. As a Warehouse user, I want a stock-in form with Product, quantity above 0 and a note, so that received beans are added to stock.
72. As a Warehouse user, I want On Hand to rise by exactly the quantity I enter, so that the count is trustworthy.
73. As a Warehouse user, I want to record an Adjustment with a positive or negative quantity and a required reason, so that physical counts and damaged bags are explained.
74. As a Warehouse user, I want an Adjustment that would make On Hand negative to be rejected with a clear message, so that stock never goes below zero.
75. As the owner, I want nobody to type an On Hand number directly, so that stock is always the sum of recorded movements.
76. As a Warehouse user, I want to see a Product's movement history with type, quantity, reason, user and time, so that I can explain any number.
77. As the owner, I want the opening stock (170, 35, 90, 240) loaded as stock-in movements, so that the sample data is consistent.
78. As a Sales user, I want to be unable to record stock-in or Adjustments, so that stock cannot be changed to make an order pass.
79. As an Admin, I want to do every stock action, so that I can cover for the Warehouse user.

### Payments

80. As an Accountant, I want to record a Payment against an Invoice with an amount and a date, so that I know what is still owed.
81. As an Accountant, I want a full Payment to change `INV-0001` (9,630.00 THB) to Paid, so that settled Invoices are clear.
82. As an Accountant, I want a partial Payment to change the Invoice to Partially Paid and show the balance, so that I track instalments.
83. As an Accountant, I want a Payment larger than the balance to be rejected with a clear message, so that overpaying cannot happen.
84. As an Accountant, I want a Payment amount above 0, so that empty payments cannot be saved.
85. As an Accountant, I want Payments to be unchangeable once saved, so that the record is trustworthy.
86. As an Accountant, I want the Invoice status derived from its Payments, so that it can never disagree with them.
87. As an Accountant, I want to see all Payments on an Invoice, so that I can explain the balance.
88. As a Sales user, I want to be unable to record Payments, so that money handling stays with the Accountant.
89. As the owner, I want Open Receivables on the Dashboard to drop by 9,630.00 THB when `INV-0001` is paid in full, so that I see the effect at once.

### Dashboard

90. As the owner, I want Sales Today (excluding VAT) on the Dashboard, so that I see today's sales without asking.
91. As the owner, I want a Low Stock count on the Dashboard that includes every Product below its Reorder Level, so that I know what to reorder.
92. As the owner, I want Open Receivables (including VAT) on the Dashboard, so that I know who owes me money.
93. As the owner, I want the number of open Invoices on the Dashboard, so that I see how many need chasing.
94. As the owner, I want "today" to mean Bangkok time, so that late-evening sales land on the right day.
95. As a user, I want all Dashboard numbers to be calculated live from the data, so that they always agree with the other screens.
96. As a user, I want the Dashboard readable on a phone, so that I can check it away from the office.

### Quality and demo

97. As a user, I want every error to say what to fix, so that I can correct it without help.
98. As a user, I want empty lists to say so (for example "No invoices yet"), so that an empty screen is not mistaken for a bug.
99. As a user, I want money shown as `9,630.00 THB`, quantities with their unit and dates as `21 Oct 2026` in English, so that the system is easy to read.
100. As Nok from Sales, I want to create and confirm an order without any training, so that the system replaces the spreadsheet.
101. As the course instructor, I want the system on a public URL that works on a phone, with no secret keys in git or the frontend, so that it can be scored live.
102. As a presenter, I want the Café Lune flow (order, stock 170 to 150, `INV-0001`, payment, Dashboard) to work end to end as two Roles, so that the demo succeeds.

## Implementation Decisions

- **Stack.** Supabase Postgres and Auth, a Python FastAPI backend managed with uv, a React TypeScript frontend built with Vite, deployed on Cloudflare. Deployment of the backend is settled by a spike (see Further Notes).
- **Identity and Roles.** Supabase Auth proves who the user is. A profile record holds exactly one Role per user. FastAPI checks the Role on every endpoint by reading it from the database, never from token metadata a user could change. Admin creates all users; there is no public sign-up. Deactivated users cannot log in.
- **Permission matrix** (enforced server-side):
  - Admin: everything.
  - Sales: edit Customers; create, edit and confirm Sales Orders; view Products with On Hand and Invoices.
  - Warehouse: stock in and Adjustments; view Products with On Hand.
  - Accountant: record Payments; view Invoices, Products and Customers.
  - Everyone: Dashboard. Only Admin edits Products and prices.
- **Master data.** Products and Customers are deactivated and never deleted. A deactivated record cannot be chosen on new documents but stays visible on existing ones, and Admin can reactivate it. SKU is unique and immutable and stays reserved.
- **Validation.** SKU is capital letters, digits and hyphens. Tax ID is exactly 13 digits. Price and cost are 0 or more. Order-line quantity is above 0. Payment amount is above 0 and cannot exceed the balance. Messages state what to fix in plain English.
- **Stock.** A single movement record per change, with signed quantity, type (stock in, sale, adjustment), reason, user and time. On Hand is the sum of movements and is never stored. A database-level check is the second line of defence against negative stock. Opening stock is loaded as stock-in movements.
- **Sales Order lifecycle.** Draft then Confirmed. Drafts are editable and deletable and carry no number. There is no cancel after confirm; mistakes are corrected with an Adjustment and a note. Line prices are copied from the Product when the line is added and are not editable by Sales.
- **Confirm.** One Postgres function performs the whole confirm: lock the stock rows, check stock, write sale movements, take the next `SO-` and `INV-` numbers, create the Invoice with its lines. FastAPI checks the Role and calls it as a single statement (ADR 0001). Any failure rolls everything back and returns "Not enough stock for <SKU>".
- **Document numbers.** Taken from a counter record locked and incremented inside the confirm, so numbers are sequential, gap-free and never reused (ADR 0002).
- **Money.** Stored as exact decimals with 2 places, never floats. VAT is 7% of the Invoice subtotal, rounded half-up to 2 places, calculated once per Invoice. The Invoice stores subtotal, VAT and total.
- **Invoice.** Snapshots the Customer's name, tax ID and Due Date at issue and never changes. Due Date comes from Payment Terms (Cash: same day; 15 days; 30 days). Overdue is derived from the Due Date and the balance, not stored.
- **Payments.** A separate record per payment, append-only. Balance is the total minus the sum of Payments. Invoice Status (Open, Partially Paid, Paid) is derived.
- **Dashboard.** Four live numbers: Sales Today (sum of Invoice subtotals excluding VAT, Bangkok time), Low Stock count, Open Receivables (including VAT), open Invoice count.
- **Search.** Server-side, case-insensitive "contains" match on Customer name, 20 rows per page, sorted by name.
- **Display.** English only. Money as `9,630.00 THB`, quantities with unit, dates as `21 Oct 2026`, all in Bangkok time.
- **Seed data.** The four sample Products, three sample Customers and opening stock from the scenario, plus one demo user per Role.
- **Out-of-reach rules.** Rules 1 to 9 of the scenario hold on the server or in the database, not only on screen.

## Testing Decisions

- **What makes a good test.** It checks external behaviour only: the response of an endpoint, or what a user sees, and the resulting data. It never asserts on internal functions, table internals or how something is implemented. A test is written and seen to fail before its code is written (red before green).
- **Seam 1, the HTTP API (primary).** Tests call the FastAPI endpoints through its test client, logged in as a given Role, against a real Postgres running in local Docker with the same schema migrations used for Supabase. Each test rolls back so tests stay independent. No database mocks, because the confirm rules live in SQL (ADR 0001). This seam covers `403` checks per Role, validation messages, the US-1 to US-5 acceptance examples, document numbering, VAT figures, deactivation, payments, derived statuses, the Dashboard numbers and the no-negative-stock rule, including two confirms racing for the same stock.
- **Seam 2, the browser (small).** A small set of browser tests covers the US-1 flow end to end through the real screens (Sales confirms an order, Accountant records the payment, the Dashboard updates) and the access-denied page for the wrong Role. No other screens get automated browser tests.
- **Prior art.** None; this is a new repo. The first API tests set the pattern: a fixture for the test database, a fixture per Role, and the acceptance examples from `docs/scenario.md` as test cases.

## Out of Scope

- Quotations and delivery notes.
- Cancelling or voiding a confirmed order or Invoice.
- Discounts or per-order price overrides.
- Purchasing, suppliers and goods receipts (bonus only).
- More than one company, or more than one warehouse (bonus only for the company).
- HR, payroll, withholding tax and LINE integration.
- Thai-language interface.
- Searching Customers by tax ID.
- Public self-service sign-up.

## Further Notes

- **Deployment spike first.** The first deploy ticket runs a Cloudflare Worker with one `BEGIN; SELECT ... FOR UPDATE; COMMIT` through Hyperdrive. If it works, FastAPI and React both run on Cloudflare. If it fails, React stays on Cloudflare static assets and FastAPI moves to a conventional host (Render or Fly). Because confirm is a single database function, the choice does not change the design.
- **Success check.** Café Lune's 20 kg order must go order, stock (170 to 150), `INV-0001` (9,630.00 THB), payment and Dashboard on the live URL with the numbers agreeing on every screen, and a Warehouse user must get `403` on confirm even when calling the API directly.
- **Vocabulary.** All terms follow `GLOSSARY.md`. Decisions are in `docs/adr/`.
