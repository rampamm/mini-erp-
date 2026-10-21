# 13: Payments (US-4)

**What to build:** Accountant records a full or partial Payment against an Invoice. The Invoice status is always derived from its Payments, and Payments can never be edited.

**Blocked by:** 12 Invoice list and detail

**Status:** ready-for-agent

- [ ] Given open `INV-0001` of 9,630.00 THB, recording a full Payment sets its status to Paid (US-4)
- [ ] A partial Payment sets the status to Partially Paid and shows the remaining balance
- [ ] A Payment larger than the balance is rejected with a message saying what the balance is
- [ ] A Payment of 0 or less is rejected with a message saying what to fix
- [ ] Payments cannot be edited or deleted once saved
- [ ] The Invoice detail lists every Payment with date and amount
- [ ] Sales and Warehouse get `403` when recording a Payment; Accountant and Admin can
- [ ] An API endpoint returns Open Receivables, the total still owed including VAT, for the Dashboard to use
