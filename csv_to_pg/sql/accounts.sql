CREATE TABLE IF NOT EXISTS accounts (
    "customer_id" BIGINT,
    "first_name" TEXT,
    "last_name" TEXT,
    "address_1" TEXT,
    "address_2" TEXT,
    "city" TEXT,
    "state" TEXT,
    "zip_code" BIGINT,
    "join_date" TEXT,
    CONSTRAINT "pk_accounts_customer_id" PRIMARY KEY ("customer_id")
);