# 06: Stock in and On Hand

**What to build:** Warehouse records stock in, and every Product shows its On Hand quantity, which is always the sum of its Stock Movements and is never typed in. Each Product has a movement history. The opening stock from the scenario is loaded as stock-in movements.

**Blocked by:** 04 Products

**Status:** ready-for-agent

- [ ] Warehouse records a stock in with Product, quantity above 0 and a note, and On Hand rises by exactly that quantity
- [ ] A quantity of 0 or less is rejected with a message saying what to fix
- [ ] There is no way to set On Hand directly through the screen or the API
- [ ] A Product's movement history lists type, quantity, reason, user and time
- [ ] Opening stock loads as ARB-1KG 170, ROB-1KG 35, BLD-1KG 90, DRP-10 240
- [ ] The Product list shows On Hand with its unit, for Sales, Warehouse and Accountant
- [ ] Sales and Accountant get `403` when recording stock in; Admin and Warehouse can
