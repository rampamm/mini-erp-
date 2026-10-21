create table customers (
    id uuid primary key default gen_random_uuid(),
    name text not null check (btrim(name) <> ''),
    tax_id text not null check (tax_id ~ '^[0-9]{13}$'),
    payment_terms text not null check (payment_terms in ('Cash', '15 days', '30 days')),
    active boolean not null default true,
    created_at timestamptz not null default now()
);

create index customers_name_idx on customers (lower(name), id);
