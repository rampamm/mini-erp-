# 10: Confirm order issues Invoice (US-1 happy path)

**What to build:** Sales confirms a draft and, in one step, the order gets its `SO-` number, stock goes down, and an Invoice with its own `INV-` number is issued. This uses the single Postgres function from ADR 0001 and the gap-free counter from ADR 0002. The Invoice shows subtotal, 7% VAT and total, and keeps the customer's name, tax ID and Due Date as they were on the day it was issued.

**Blocked by:** 09 Draft Sales Orders

**Status:** ready-for-agent

- [ ] Given 170 kg of ARB-1KG, confirming 20 kg at 450 THB for Café Lune leaves 150 kg On Hand (US-1)
- [ ] That order is `SO-0001` and the Invoice is `INV-0001` showing 9,000.00 + 630.00 VAT = 9,630.00 THB (US-1)
- [ ] The Invoice has the same lines as the order
- [ ] VAT is 7% of the subtotal rounded half-up to 2 decimals, calculated once per Invoice
- [ ] The Invoice keeps the Customer's name, tax ID and Due Date from the day of issue; later Customer edits do not change it
- [ ] Due Date follows Payment Terms: Cash is the same day, 15 days and 30 days are added to the issue date
- [ ] A confirmed Sales Order is read-only
- [ ] Document numbers are sequential and are never reused
- [ ] Warehouse and Accountant get `403` on confirm; Sales and Admin can confirm
