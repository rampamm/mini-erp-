-- Supabase publishes everything in `public` through its Data API. This app talks to Postgres
-- directly as the table owner (which bypasses row-level security), so nothing here needs to be
-- reachable through the API: switch RLS on with no policies and strip the API roles' grants.
do $$
declare
    r record;
begin
    for r in
        select c.relname
        from pg_class c join pg_namespace n on n.oid = c.relnamespace
        where n.nspname = 'public' and c.relkind = 'r'
    loop
        execute format('alter table public.%I enable row level security', r.relname);
    end loop;

    for r in
        select c.relname
        from pg_class c join pg_namespace n on n.oid = c.relnamespace
        where n.nspname = 'public' and c.relkind = 'v'
    loop
        execute format('alter view public.%I set (security_invoker = true)', r.relname);
    end loop;

    for r in
        select p.oid::regprocedure as signature
        from pg_proc p join pg_namespace n on n.oid = p.pronamespace
        where n.nspname = 'public'
    loop
        execute format('revoke all on function %s from public', r.signature);
    end loop;

    for r in select rolname from pg_roles where rolname in ('anon', 'authenticated') loop
        execute format('revoke all on all tables in schema public from %I', r.rolname);
        execute format('revoke all on all sequences in schema public from %I', r.rolname);
        execute format('revoke all on all functions in schema public from %I', r.rolname);
        execute format('alter default privileges in schema public revoke all on tables from %I', r.rolname);
        execute format('alter default privileges in schema public revoke all on functions from %I', r.rolname);
    end loop;
end
$$;
