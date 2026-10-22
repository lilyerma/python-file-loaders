CREATE TABLE IF NOT EXISTS transactions (
    "transaction_id" TEXT,
    "transaction_date" TEXT,
    "product_id" BIGINT,
    "product_code" BIGINT,
    "product_description" TEXT,
    "quantity" BIGINT,
    "account_id" BIGINT,
    CONSTRAINT "pk_transactions_transaction_id" PRIMARY KEY ("transaction_id"),    
    CONSTRAINT "product_fk_constraint" FOREIGN KEY ("product_id") REFERENCES products ("product_id") ON DELETE CASCADE,
    CONSTRAINT "account_fk_constraint" FOREIGN KEY ("account_id") REFERENCES accounts ("customer_id") ON DELETE CASCADE
);