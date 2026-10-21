# Confirm-order runs as one Postgres function, not as Python code

The all-or-nothing work of confirming a sales order (lock stock rows, check stock, write stock movements, take the next document numbers, create the invoice) lives in a single Supabase Postgres function that FastAPI calls as one statement. We chose this over a multi-statement transaction in Python because it keeps rules 2 and 5 inside the database regardless of hosting; Cloudflare Hyperdrive has no confirmed support for multi-statement `SELECT ... FOR UPDATE` transactions. FastAPI still checks the caller's role before making the call.

## Consequences

- Business logic for confirm lives in SQL, so tests must run against a real Postgres, not mocks.
- Role checks stay in Python; the database function trusts that FastAPI already authorised the caller.
