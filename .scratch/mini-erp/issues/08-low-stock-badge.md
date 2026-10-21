# 08: Low Stock badge (US-2)

**What to build:** Any Product whose On Hand is below its Reorder Level shows a Low Stock badge in the Product list, so Warehouse can see what to reorder.

**Blocked by:** 06 Stock in and On Hand

**Status:** ready-for-agent

- [ ] A Product below its Reorder Level shows a Low Stock badge in the Product list (US-2)
- [ ] A Product exactly at its Reorder Level does not show the badge
- [ ] ROB-1KG (35 on hand against 40) shows the badge from the start, and ARB-1KG, BLD-1KG and DRP-10 do not
- [ ] Stock in that lifts a Product to or above its Reorder Level removes the badge
- [ ] An API endpoint returns the count of Low Stock Products for the Dashboard to use
