create table products (
    id uuid primary key default gen_random_uuid(),
    sku text not null unique check (sku ~ '^[A-Z0-9-]+$'),
    name text not null check (btrim(name) <> ''),
    unit text not null check (btrim(unit) <> ''),
    cost numeric(12, 2) not null check (cost >= 0),
    price numeric(12, 2) not null check (price >= 0),
    reorder_level integer not null default 0 check (reorder_level >= 0),
    active boolean not null default true,
    created_at timestamptz not null default now()
);
