# 03: Admin manages users

**What to build:** The Admin can create a user with an email, a temporary password and one Role, change a user's Role, and deactivate or reactivate a user. There is no public sign-up.

**Blocked by:** 02 Login, Roles and 403

**Status:** ready-for-agent

- [ ] Admin creates a user and assigns one Role, and that user can then log in
- [ ] There is no sign-up page or open sign-up endpoint
- [ ] Admin changes a user's Role and the new Role applies on the next request
- [ ] Admin deactivates a user, who can no longer log in, and can reactivate them
- [ ] Non-Admin Roles get `403` on every user-management endpoint and see an access-denied page
- [ ] Creating a user with a missing email, a duplicate email or no Role is rejected with a message saying what to fix
