# 09: Draft Sales Orders

**What to build:** Sales prepares a draft Sales Order for an active Customer by adding Order Lines. Each line price is copied from the Product and cannot be edited, and the screen shows line totals plus subtotal, VAT and total. Drafts have no number, change nothing in stock, and can be edited or deleted freely.

**Blocked by:** 04 Products, 05 Customers and search, 06 Stock in and On Hand

**Status:** ready-for-agent

- [ ] Sales creates a draft for an active Customer and adds lines by choosing an active Product and a quantity above 0
- [ ] The line price is copied from the Product and cannot be changed by Sales
- [ ] Changing a Product's price afterwards does not change lines already on a draft
- [ ] The order shows each line total and the subtotal, 7% VAT and total as Sales edits
- [ ] The current On Hand is shown beside each Product while adding lines
- [ ] Deactivated Products and Customers do not appear in the pickers
- [ ] Sales edits and deletes a draft, which has no number and does not touch stock
- [ ] A quantity of 0 or less is rejected with a message saying what to fix
- [ ] Sales Orders can be listed filtered by Draft or Confirmed
- [ ] Warehouse and Accountant get `403` when creating or editing drafts
