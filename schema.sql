create table
  public.capacity_ledger (
    id bigint generated by default as identity not null,
    transaction_id bigint generated by default as identity not null,
    type text not null,
    change integer not null,
    constraint capacity_ledger_pkey primary key (id),
    constraint liquid_ledger_transaction_id_fkey foreign key (transaction_id) references transaction (id)
  ) tablespace pg_default;

  create table
  public.cart (
    id bigint generated by default as identity not null,
    visit_id bigint not null,
    constraint cart_pkey primary key (id),
    constraint cart_visit_id_fkey foreign key (visit_id) references visit (id)
  ) tablespace pg_default;

  create table
  public.cart_item (
    id bigint generated by default as identity not null,
    cart_id bigint not null,
    potion_id bigint not null,
    quantity integer not null,
    constraint cart_items_pkey primary key (potion_id, cart_id, id),
    constraint cart_items_id_key unique (id),
    constraint cart_item_cart_id_fkey foreign key (cart_id) references cart (id),
    constraint cart_item_potion_id_fkey foreign key (potion_id) references potion (id)
  ) tablespace pg_default;

  create table
  public.checkout (
    transaction_id bigint generated by default as identity not null,
    cart_item_id bigint not null,
    constraint checkout_pkey primary key (transaction_id, cart_item_id),
    constraint checkout_cart_item_id_fkey foreign key (cart_item_id) references cart_item (id),
    constraint checkout_transaction_id_fkey foreign key (transaction_id) references transaction (id)
  ) tablespace pg_default;

  create table
  public.customer (
    id bigint generated by default as identity not null,
    name text not null,
    class text not null,
    level smallint not null,
    constraint customer_pkey primary key (id),
    constraint customer_unique unique (name, class, level)
  ) tablespace pg_default;

  create table
  public.gold_ledger (
    id bigint generated by default as identity not null,
    transaction_id bigint generated by default as identity not null,
    change integer not null,
    constraint gold_ledger_pkey primary key (id),
    constraint gold_ledger_transaction_id_fkey foreign key (transaction_id) references transaction (id)
  ) tablespace pg_default;

  create table
  public.liquid_ledger (
    id bigint generated by default as identity not null,
    transaction_id bigint generated by default as identity not null,
    color text not null,
    change integer not null,
    constraint liquid_ledger_pkey primary key (id),
    constraint liquid_ledger_transaction_id_fkey foreign key (transaction_id) references transaction (id),
    constraint liquid_change_check check ((change <> 0))
  ) tablespace pg_default;

  create table
  public.parameter (
    id bigint generated by default as identity not null,
    potion_capacity_upgrade smallint not null,
    liquid_capacity_upgrade integer not null default 0,
    constraint parameter_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.potion (
    id bigint generated by default as identity not null,
    sku text not null,
    name text not null,
    red_ml integer not null,
    green_ml integer not null,
    blue_ml integer not null,
    dark_ml integer not null,
    price integer not null,
    craft boolean not null default false,
    catalog boolean not null default false,
    constraint potion_pkey primary key (id),
    constraint potion_sku_key unique (sku),
    constraint potion_sum_100 check (
      ((((red_ml + green_ml) + blue_ml) + dark_ml) = 100)
    )
  ) tablespace pg_default;

  create table
  public.potion_ledger (
    id bigint generated by default as identity not null,
    transaction_id bigint generated by default as identity not null,
    change integer not null,
    potion_id bigint not null,
    constraint potion_ledger_pkey primary key (id),
    constraint potion_ledger_potion_id_fkey foreign key (potion_id) references potion (id),
    constraint potion_ledger_transaction_id_fkey foreign key (transaction_id) references transaction (id)
  ) tablespace pg_default;

  create table
  public.transaction (
    id bigint generated by default as identity not null,
    real_timestamp timestamp with time zone not null default now(),
    description text not null,
    constraint transaction_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.visit (
    id bigint generated by default as identity not null,
    customer_id bigint not null,
    hour integer not null,
    day text not null,
    real_timestamp timestamp with time zone not null default now(),
    external_visit_id bigint not null,
    constraint visit_pkey primary key (id),
    constraint customer_unique_visit unique (customer_id, external_visit_id),
    constraint visit_customer_id_fkey foreign key (customer_id) references customer (id)
  ) tablespace pg_default;