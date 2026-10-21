-- VAT is 7% of an invoice subtotal, rounded half-up to 2 decimals, calculated once per invoice.
create function calc_vat(subtotal numeric) returns numeric
language sql immutable as $$ select round(subtotal * 0.07, 2) $$;

create table document_counters (
    name text primary key,
    last_value integer not null default 0
);
insert into document_counters (name) values ('SO'), ('INV');

create table sales_orders (
    id uuid primary key default gen_random_uuid(),
    number text unique,
    customer_id uuid not null references customers (id),
    status text not null default 'draft' check (status in ('draft', 'confirmed')),
    created_by uuid not null references profiles (id),
    created_at timestamptz not null default now(),
    confirmed_at timestamptz,
    check ((status = 'draft' and number is null) or (status = 'confirmed' and number is not null))
);

create table sales_order_lines (
    id uuid primary key default gen_random_uuid(),
    order_id uuid not null references sales_orders (id) on delete cascade,
    product_id uuid not null references products (id),
    quantity integer not null check (quantity > 0),
    unit_price numeric(12, 2) not null check (unit_price >= 0),
    unique (order_id, product_id)
);

create table invoices (
    id uuid primary key default gen_random_uuid(),
    number text not null unique,
    sales_order_id uuid not null unique references sales_orders (id),
    customer_id uuid not null references customers (id),
    customer_name text not null,
    customer_tax_id text not null,
    payment_terms text not null,
    issue_date date not null,
    due_date date not null,
    subtotal numeric(12, 2) not null,
    vat numeric(12, 2) not null,
    total numeric(12, 2) not null,
    issued_by uuid not null references profiles (id),
    created_at timestamptz not null default now(),
    check (total = subtotal + vat)
);

create table invoice_lines (
    id uuid primary key default gen_random_uuid(),
    invoice_id uuid not null references invoices (id),
    product_id uuid not null references products (id),
    sku text not null,
    name text not null,
    unit text not null,
    quantity integer not null check (quantity > 0),
    unit_price numeric(12, 2) not null,
    line_total numeric(12, 2) not null
);

create table payments (
    id uuid primary key default gen_random_uuid(),
    invoice_id uuid not null references invoices (id),
    amount numeric(12, 2) not null check (amount > 0),
    paid_on date not null,
    recorded_by uuid not null references profiles (id),
    created_at timestamptz not null default now()
);

create index payments_invoice_idx on payments (invoice_id);
create index invoice_lines_invoice_idx on invoice_lines (invoice_id);
create index sales_order_lines_order_idx on sales_order_lines (order_id);

-- Issued documents and payments are never edited or deleted.
create function forbid_change() returns trigger language plpgsql as $$
begin
    raise exception 'Issued documents and payments cannot be changed or deleted';
end;
$$;

create trigger invoices_immutable before update or delete on invoices
    for each row execute function forbid_change();
create trigger invoice_lines_immutable before update or delete on invoice_lines
    for each row execute function forbid_change();
create trigger payments_immutable before update or delete on payments
    for each row execute function forbid_change();

-- Status is always derived from the payments, never stored.
create view invoice_summary as
select
    i.*,
    coalesce(sum(p.amount), 0)::numeric(12, 2) as paid,
    (i.total - coalesce(sum(p.amount), 0))::numeric(12, 2) as balance,
    case
        when coalesce(sum(p.amount), 0) = 0 then 'open'
        when coalesce(sum(p.amount), 0) < i.total then 'partially_paid'
        else 'paid'
    end as status,
    (i.total - coalesce(sum(p.amount), 0) > 0
        and i.due_date < (now() at time zone 'Asia/Bangkok')::date) as overdue
from invoices i
left join payments p on p.invoice_id = i.id
group by i.id;
