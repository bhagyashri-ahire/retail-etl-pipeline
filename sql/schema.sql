-- Star schema for retail sales. Portable across SQLite and MySQL.
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id    VARCHAR(20) PRIMARY KEY,
    customer_name  VARCHAR(100) NOT NULL,
    city           VARCHAR(50),
    segment        VARCHAR(30),
    load_timestamp DATETIME NOT NULL,
    source_file    VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id     VARCHAR(20) PRIMARY KEY,
    product_name   VARCHAR(100) NOT NULL,
    category       VARCHAR(50) NOT NULL,
    load_timestamp DATETIME NOT NULL,
    source_file    VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_sales (
    order_id       VARCHAR(20) NOT NULL,
    product_id     VARCHAR(20) NOT NULL,
    customer_id    VARCHAR(20) NOT NULL,
    order_date     DATE NOT NULL,
    quantity       INTEGER NOT NULL,
    unit_price     DECIMAL(10,2) NOT NULL,
    discount       DECIMAL(4,2) NOT NULL,
    total_amount   DECIMAL(12,2) NOT NULL,
    load_timestamp DATETIME NOT NULL,
    source_file    VARCHAR(200) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
);

CREATE TABLE IF NOT EXISTS rejected_rows (
    run_id         VARCHAR(40) NOT NULL,
    order_id       VARCHAR(20),
    product_id     VARCHAR(20),
    reject_reason  VARCHAR(100) NOT NULL,
    load_timestamp DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS etl_audit_log (
    run_id          VARCHAR(40) PRIMARY KEY,
    source_file     VARCHAR(200) NOT NULL,
    rows_extracted  INTEGER NOT NULL,
    rows_loaded     INTEGER NOT NULL,
    rows_rejected   INTEGER NOT NULL,
    reconciled      INTEGER NOT NULL,
    status          VARCHAR(20) NOT NULL,
    run_timestamp   DATETIME NOT NULL
);
