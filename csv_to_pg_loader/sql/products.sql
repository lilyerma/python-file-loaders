CREATE TABLE IF NOT EXISTS products (
    "product_id" BIGINT,
    "product_code" BIGINT,
    "product_description" TEXT,
    CONSTRAINT "pk_products_product_id" PRIMARY KEY ("product_id")
);