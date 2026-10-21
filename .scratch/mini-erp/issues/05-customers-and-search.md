# 05: Customers and search (US-5)

**What to build:** Sales creates, edits and deactivates Customers with a required tax ID and Payment Terms, and finds one quickly with a name search. The three sample Customers are loaded.

**Blocked by:** 02 Login, Roles and 403

**Status:** ready-for-agent

- [ ] Sales creates a Customer with name, 13-digit tax ID and Payment Terms of Cash, 15 days or 30 days
- [ ] A tax ID that is not 13 digits is rejected with "Tax ID must be 13 digits", and a missing tax ID is rejected
- [ ] Sales edits and deactivates a Customer; a deactivated Customer cannot be chosen on new documents and Admin can reactivate it
- [ ] Given 200 Customers, typing part of a name filters the list within 1 second, case-insensitive, sorted by name, at most 20 rows per page (US-5)
- [ ] A search with no match says "No customers match"
- [ ] Accountant can list Customers but not edit; Warehouse gets `403` on Customers
- [ ] Café Lune, Brew Lab Ari and Sukhumvit Corner Café exist with the scenario's values
