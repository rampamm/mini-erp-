# Document numbers come from a counter table, not a Postgres sequence

`SO-` and `INV-` numbers are taken from a `document_counters` row that is locked and incremented inside the confirm-order transaction. A Postgres sequence is simpler but leaves gaps whenever a confirm fails after taking a number, and an accountant will question a gap in invoice numbers. With a counter table a rollback also rolls back the number, so numbers stay sequential and are never reused.

## Consequences

- Confirmations serialise briefly on the counter row; acceptable at this business's volume.
- Numbers are assigned at confirm, so draft orders have no number.
