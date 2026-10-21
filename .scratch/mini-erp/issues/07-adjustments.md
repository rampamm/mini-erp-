# 07: Adjustments

**What to build:** Warehouse records an Adjustment, a positive or negative stock change with a required reason, to cover recounts, damaged bags and samples. Stock can never go below zero.

**Blocked by:** 06 Stock in and On Hand

**Status:** ready-for-agent

- [ ] Warehouse records an Adjustment with Product, a positive or negative quantity and a required reason
- [ ] An Adjustment with no reason is rejected with a message saying a reason is needed
- [ ] An Adjustment that would take On Hand below zero is rejected, and nothing changes
- [ ] The Adjustment shows in the Product's movement history with its reason and the user who made it
- [ ] Sales and Accountant get `403` on Adjustments; Admin and Warehouse can
