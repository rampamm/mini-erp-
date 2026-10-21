-- Payments are listed in the order they were recorded; timestamps can tie inside one transaction.
alter table payments add column seq bigserial;
create unique index payments_seq_idx on payments (seq);
