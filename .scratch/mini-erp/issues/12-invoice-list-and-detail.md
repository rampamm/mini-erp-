# 12: Invoice list and detail

**What to build:** Accountant and Sales can list Invoices filtered by status and open one to see its lines, totals, Due Date and balance. An Invoice that is past its Due Date and not fully paid shows as Overdue.

**Blocked by:** 10 Confirm order issues Invoice

**Status:** ready-for-agent

- [ ] The Invoice list shows number, Customer, total, balance, Due Date and status, with money as `9,630.00 THB`
- [ ] The list can be filtered by Open, Partially Paid, Paid and Overdue
- [ ] An Invoice past its Due Date with a balance above zero shows as Overdue, derived from the dates and not stored
- [ ] The detail screen shows the lines, subtotal, VAT, total and the Customer details saved on the Invoice
- [ ] Sales can open an Invoice from the confirmed order
- [ ] Warehouse gets `403` on Invoices; Sales and Accountant can view; Admin can do everything
- [ ] An empty list says "No invoices yet"
