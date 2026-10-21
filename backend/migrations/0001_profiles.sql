create table profiles (
    id uuid primary key default gen_random_uuid(),
    email text not null unique,
    full_name text not null,
    role text not null check (role in ('admin', 'sales', 'warehouse', 'accountant')),
    active boolean not null default true,
    password_hash text,
    created_at timestamptz not null default now()
);
