# 14: Dashboard

**What to build:** Every logged-in user sees a Dashboard with four live numbers calculated from the data, using Bangkok time for "today".

**Blocked by:** 08 Low Stock badge, 13 Payments

**Status:** ready-for-agent

- [ ] The Dashboard shows Sales Today, the sum of today's Invoice subtotals excluding VAT, labelled as excluding VAT
- [ ] It shows the Low Stock count, which includes every Product below its Reorder Level (US-2)
- [ ] It shows Open Receivables, the total still owed including VAT
- [ ] It shows the number of open Invoices (Open or Partially Paid)
- [ ] After a full Payment of 9,630.00 THB, Open Receivables drops by 9,630.00 THB (US-4)
- [ ] An Invoice issued late in the evening in Bangkok counts as that Bangkok day
- [ ] All four numbers agree with the Invoice and Product screens
- [ ] Every Role can open the Dashboard, and it is readable on a phone
