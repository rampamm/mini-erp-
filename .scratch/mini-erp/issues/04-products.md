# 04: Products

**What to build:** Admin creates, lists, edits, deactivates and reactivates Products. Every Role that is allowed to see Products can list them with price and Reorder Level. The four sample Products from the scenario are loaded.

**Blocked by:** 02 Login, Roles and 403

**Status:** ready-for-agent

- [ ] Admin creates a Product with SKU, name, unit, cost, price and Reorder Level
- [ ] A duplicate SKU is rejected with "SKU already exists"
- [ ] A SKU with anything other than capital letters, digits and hyphens is rejected, and a SKU cannot be changed after creation
- [ ] A negative price or cost is rejected with a message saying what to fix
- [ ] Admin edits name, price, cost and Reorder Level, and changing a price does not change any existing order line or Invoice
- [ ] Admin deactivates a Product, which then cannot be chosen on new documents; its SKU stays reserved; Admin can reactivate it
- [ ] Sales, Warehouse and Accountant can list Products but get `403` on create, edit and deactivate
- [ ] ARB-1KG, ROB-1KG, BLD-1KG and DRP-10 exist with the scenario's values
- [ ] Prices show as `450.00 THB`
