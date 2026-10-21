# 02: Login, Roles and 403

**What to build:** Staff log in with email and password, each user has exactly one Role (Admin, Sales, Warehouse or Accountant), and the server enforces the permission matrix. The wrong Role gets `403` from the API even when the button is hidden, and the screen shows an access-denied page. Everyone who is logged in sees the Dashboard page. The four demo accounts, one per Role, are seeded.

**Blocked by:** 01 Project skeleton and deploy spike

**Status:** ready-for-agent

- [ ] A user can log in and log out, and an expired session sends them to the login page
- [ ] The Role is read from the database on every request, never from token data the user could edit
- [ ] A Sales user opening the Accounting screen sees an access-denied page, and the matching API returns `403` (US-3)
- [ ] A Warehouse user calling the confirm-order API directly gets `403` (US-3)
- [ ] An Admin opens the same screens and they load (US-3)
- [ ] A deactivated user cannot log in
- [ ] The permission matrix is enforced on every existing endpoint, tested per Role through the API
- [ ] The four demo accounts are seeded, one per Role
