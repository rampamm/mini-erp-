-- Confirming a sales order is one all-or-nothing step (ADR 0001): check stock, take the next
-- document numbers (ADR 0002), write the stock movements and issue the invoice together.
create function confirm_sales_order(p_order_id uuid, p_user_id uuid) returns uuid
language plpgsql as $$
declare
    v_order sales_orders%rowtype;
    v_customer customers%rowtype;
    v_line record;
    v_n integer;
    v_so_number text;
    v_inv_number text;
    v_subtotal numeric(12, 2);
    v_vat numeric(12, 2);
    v_issue_date date := (now() at time zone 'Asia/Bangkok')::date;
    v_due_date date;
    v_invoice_id uuid;
begin
    select * into v_order from sales_orders where id = p_order_id for update;
    if not found then
        raise exception 'Order not found';
    end if;
    if v_order.status <> 'draft' then
        raise exception 'This order is already confirmed';
    end if;
    if not exists (select 1 from sales_order_lines where order_id = p_order_id) then
        raise exception 'Add at least one line before confirming';
    end if;

    select * into v_customer from customers where id = v_order.customer_id;
    if not v_customer.active then
        raise exception 'Customer % is deactivated', v_customer.name;
    end if;

    -- Lock the products in a fixed order so two confirms cannot deadlock or oversell.
    perform 1 from products
    where id in (select product_id from sales_order_lines where order_id = p_order_id)
    order by id
    for no key update;

    for v_line in
        select p.sku, p.active, l.quantity, s.on_hand
        from sales_order_lines l
        join products p on p.id = l.product_id
        join product_stock s on s.product_id = p.id
        where l.order_id = p_order_id
        order by p.sku
    loop
        if not v_line.active then
            raise exception 'Product % is deactivated', v_line.sku;
        end if;
        if v_line.on_hand < v_line.quantity then
            raise exception 'Not enough stock for %', v_line.sku;
        end if;
    end loop;

    update document_counters set last_value = last_value + 1 where name = 'SO' returning last_value into v_n;
    v_so_number := 'SO-' || lpad(v_n::text, 4, '0');
    update document_counters set last_value = last_value + 1 where name = 'INV' returning last_value into v_n;
    v_inv_number := 'INV-' || lpad(v_n::text, 4, '0');

    insert into stock_movements (product_id, movement_type, quantity, reason, user_id)
    select product_id, 'sale', -quantity, v_so_number, p_user_id
    from sales_order_lines where order_id = p_order_id;

    select sum(quantity * unit_price) into v_subtotal from sales_order_lines where order_id = p_order_id;
    v_vat := calc_vat(v_subtotal);
    v_due_date := v_issue_date + case v_customer.payment_terms when 'Cash' then 0 when '15 days' then 15 else 30 end;

    insert into invoices (
        number, sales_order_id, customer_id, customer_name, customer_tax_id, payment_terms,
        issue_date, due_date, subtotal, vat, total, issued_by
    ) values (
        v_inv_number, p_order_id, v_customer.id, v_customer.name, v_customer.tax_id, v_customer.payment_terms,
        v_issue_date, v_due_date, v_subtotal, v_vat, v_subtotal + v_vat, p_user_id
    ) returning id into v_invoice_id;

    insert into invoice_lines (invoice_id, product_id, sku, name, unit, quantity, unit_price, line_total)
    select v_invoice_id, p.id, p.sku, p.name, p.unit, l.quantity, l.unit_price, l.quantity * l.unit_price
    from sales_order_lines l join products p on p.id = l.product_id
    where l.order_id = p_order_id;

    update sales_orders set status = 'confirmed', number = v_so_number, confirmed_at = now()
    where id = p_order_id;

    return v_invoice_id;
end;
$$;
