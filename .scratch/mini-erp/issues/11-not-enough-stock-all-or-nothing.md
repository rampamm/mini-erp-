# 11: Not enough stock, all-or-nothing and racing confirms

**What to build:** Confirming an order that cannot be fulfilled fails clearly and changes nothing, and two people confirming at the same moment can never oversell the same stock.

**Blocked by:** 10 Confirm order issues Invoice

**Status:** ready-for-agent

- [ ] Given a line quantity greater than On Hand, confirming shows "Not enough stock for ARB-1KG" and changes nothing (US-1)
- [ ] After a failed confirm no stock movement, Invoice or document number exists, and the next successful confirm still gets the next number with no gap
- [ ] If one line of a multi-line order is short, no line is deducted
- [ ] An order with no lines is rejected on confirm with a message saying what to fix
- [ ] A deactivated Product or Customer on a draft is rejected on confirm
- [ ] Two confirms racing for the same stock cannot both succeed when the stock only covers one, and On Hand never goes below zero
