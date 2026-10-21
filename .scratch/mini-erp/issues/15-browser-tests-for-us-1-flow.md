# 15: Browser tests for the US-1 flow

**What to build:** A small set of browser tests that walk the real screens through the Café Lune flow as two Roles, plus the access-denied page. These are the only automated browser tests; all other tests go through the API.

**Blocked by:** 13 Payments, 14 Dashboard

**Status:** ready-for-agent

- [ ] As Sales, the test confirms a 20 kg ARB-1KG order for Café Lune and sees On Hand go from 170 to 150
- [ ] The test opens `INV-0001` and sees 9,630.00 THB
- [ ] As Accountant, the test records the full Payment and the Invoice shows Paid
- [ ] The Dashboard shows Open Receivables dropped by 9,630.00 THB
- [ ] A Sales user opening the Accounting screen sees the access-denied page
- [ ] The tests run against a seeded test database and can be run with one documented command
