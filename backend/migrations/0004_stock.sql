create table stock_movements (
    id bigserial primary key,
    product_id uuid not null references products (id),
    movement_type text not null check (movement_type in ('stock_in', 'sale', 'adjustment')),
    quantity integer not null check (quantity <> 0),
    reason text,
    user_id uuid not null references profiles (id),
    created_at timestamptz not null default now(),
    check (
        (movement_type = 'stock_in' and quantity > 0)
        or (movement_type = 'sale' and quantity < 0)
        or movement_type = 'adjustment'
    ),
    check (movement_type <> 'adjustment' or (reason is not null and btrim(reason) <> ''))
);

create index stock_movements_product_idx on stock_movements (product_id, id desc);

create view product_stock as
select p.id as product_id, coalesce(sum(m.quantity), 0)::integer as on_hand
from products p
left join stock_movements m on m.product_id = p.id
group by p.id;

-- Second line of defence for rule 2: stock can never go negative.
-- The row lock serialises writers per product; FOR NO KEY UPDATE does not clash with the
-- FOR KEY SHARE lock the foreign key takes, so two concurrent inserts cannot deadlock.
create function check_stock_not_negative() returns trigger language plpgsql as $$
declare
    v_sku text;
    v_on_hand integer;
begin
    select sku into v_sku from products where id = new.product_id for no key update;
    select coalesce(sum(quantity), 0) into v_on_hand from stock_movements where product_id = new.product_id;
    if v_on_hand < 0 then
        raise exception 'Not enough stock for %', v_sku;
    end if;
    return null;
end;
$$;

create trigger stock_not_negative
after insert on stock_movements
for each row execute function check_stock_not_negative();
