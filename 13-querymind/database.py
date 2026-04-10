# ──────────────────────────────────────────
# E-COMMERCE DEMO DATABASE
# 6 tables, realistic data, complex
# relationships for interesting queries.
# ──────────────────────────────────────────

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "querymind.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE,
    city        TEXT,
    country     TEXT,
    plan        TEXT,
    joined_date TEXT,
    ltv         REAL
);

CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT,
    price       REAL,
    cost        REAL,
    stock       INTEGER,
    rating      REAL
);

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY,
    customer_id     INTEGER,
    order_date      TEXT,
    status          TEXT,
    total_amount    REAL,
    shipping_city   TEXT,
    FOREIGN KEY (customer_id)
        REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id          INTEGER PRIMARY KEY,
    order_id    INTEGER,
    product_id  INTEGER,
    quantity    INTEGER,
    unit_price  REAL,
    FOREIGN KEY (order_id)
        REFERENCES orders(id),
    FOREIGN KEY (product_id)
        REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id          INTEGER PRIMARY KEY,
    product_id  INTEGER,
    customer_id INTEGER,
    rating      INTEGER,
    review_date TEXT,
    sentiment   TEXT,
    FOREIGN KEY (product_id)
        REFERENCES products(id),
    FOREIGN KEY (customer_id)
        REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS support_tickets (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER,
    created_at  TEXT,
    category    TEXT,
    status      TEXT,
    priority    TEXT,
    resolved_at TEXT,
    FOREIGN KEY (customer_id)
        REFERENCES customers(id)
);
"""

def build_database() -> None:
    """
    Build and seed the demo database.
    Idempotent — safe to call multiple times.
    """
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.executescript(SCHEMA_SQL)

    # Check if already seeded
    cur.execute(
        "SELECT COUNT(*) FROM customers"
    )
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    print("🌱 Seeding demo database...")
    random.seed(42)

    cities = [
        "New York", "London", "Tokyo",
        "Berlin", "Mumbai", "Sydney",
        "Toronto", "Paris", "Singapore",
        "Dubai"
    ]
    countries = {
        "New York": "USA",
        "London": "UK",
        "Tokyo": "Japan",
        "Berlin": "Germany",
        "Mumbai": "India",
        "Sydney": "Australia",
        "Toronto": "Canada",
        "Paris": "France",
        "Singapore": "Singapore",
        "Dubai": "UAE"
    }
    plans = [
        "Free", "Free", "Free",
        "Pro", "Pro",
        "Enterprise"
    ]
    first_names = [
        "James", "Mary", "Robert", "Patricia",
        "John", "Jennifer", "Michael", "Linda",
        "William", "Barbara", "David", "Susan",
        "Priya", "Raj", "Aisha", "Chen",
        "Yuki", "Hans", "Sophie", "Marco"
    ]
    last_names = [
        "Smith", "Johnson", "Williams",
        "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Wilson", "Taylor",
        "Sharma", "Patel", "Kumar", "Lee",
        "Tanaka", "Mueller", "Martin",
        "Rossi", "Dubois", "Santos"
    ]

    # Insert customers
    base_date = datetime.now() - \
        timedelta(days=365)
    customers = []
    for i in range(1, 201):
        city = random.choice(cities)
        name = (
            f"{random.choice(first_names)} "
            f"{random.choice(last_names)}"
        )
        joined = base_date + timedelta(
            days=random.randint(0, 300)
        )
        customers.append((
            i,
            name,
            f"user{i}@example.com",
            city,
            countries[city],
            random.choice(plans),
            joined.strftime("%Y-%m-%d"),
            round(random.uniform(0, 5000), 2)
        ))

    cur.executemany(
        "INSERT OR IGNORE INTO customers "
        "VALUES (?,?,?,?,?,?,?,?)",
        customers
    )

    # Insert products
    categories = [
        "Electronics", "Software",
        "Hardware", "Services", "Training"
    ]
    product_names = {
        "Electronics": [
            "Wireless Mouse", "Mechanical Keyboard",
            "4K Monitor", "USB Hub", "Webcam",
            "Headset", "Laptop Stand"
        ],
        "Software": [
            "Analytics Suite", "CRM Pro",
            "Security Scanner", "Dev Tools",
            "Project Manager", "API Gateway"
        ],
        "Hardware": [
            "Server Rack", "Network Switch",
            "NAS Drive", "UPS Battery",
            "Cooling System"
        ],
        "Services": [
            "Cloud Hosting", "CDN Service",
            "Support Plan", "Managed DB",
            "Monitoring Service"
        ],
        "Training": [
            "Python Course", "ML Bootcamp",
            "Cloud Certification",
            "Security Training",
            "Leadership Program"
        ]
    }

    products = []
    pid = 1
    for cat, names in product_names.items():
        for pname in names:
            price = round(
                random.uniform(29, 2999), 2
            )
            products.append((
                pid, pname, cat, price,
                round(price * 0.6, 2),
                random.randint(0, 500),
                round(random.uniform(3.0, 5.0), 1)
            ))
            pid += 1

    cur.executemany(
        "INSERT OR IGNORE INTO products "
        "VALUES (?,?,?,?,?,?,?)",
        products
    )

    # Insert orders + order_items
    statuses = [
        "completed", "completed",
        "completed", "pending",
        "refunded", "cancelled"
    ]
    order_id = 1
    item_id  = 1
    orders   = []
    items    = []

    for _ in range(500):
        cid  = random.randint(1, 200)
        date = base_date + timedelta(
            days=random.randint(0, 360)
        )
        status = random.choice(statuses)
        city   = random.choice(cities)

        # Generate 1–4 items
        num_items  = random.randint(1, 4)
        total      = 0.0
        order_prods = random.sample(
            products,
            min(num_items, len(products))
        )

        for prod in order_prods:
            qty   = random.randint(1, 5)
            price = prod[3]
            total += qty * price
            items.append((
                item_id, order_id,
                prod[0], qty, price
            ))
            item_id += 1

        orders.append((
            order_id, cid,
            date.strftime("%Y-%m-%d"),
            status,
            round(total, 2),
            city
        ))
        order_id += 1

    cur.executemany(
        "INSERT OR IGNORE INTO orders "
        "VALUES (?,?,?,?,?,?)",
        orders
    )
    cur.executemany(
        "INSERT OR IGNORE INTO order_items "
        "VALUES (?,?,?,?,?)",
        items
    )

    # Insert reviews
    sentiments = [
        "positive", "positive",
        "neutral", "negative"
    ]
    reviews = []
    for i in range(1, 301):
        reviews.append((
            i,
            random.randint(1, pid - 1),
            random.randint(1, 200),
            random.randint(1, 5),
            (base_date + timedelta(
                days=random.randint(0, 360)
            )).strftime("%Y-%m-%d"),
            random.choice(sentiments)
        ))
    cur.executemany(
        "INSERT OR IGNORE INTO reviews "
        "VALUES (?,?,?,?,?,?)",
        reviews
    )

    # Insert support tickets
    categories_t = [
        "Billing", "Technical",
        "Account", "Feature Request", "Other"
    ]
    ticket_statuses = [
        "open", "resolved",
        "resolved", "pending"
    ]
    priorities = ["low", "medium",
                  "medium", "high"]
    tickets = []
    for i in range(1, 201):
        created = base_date + timedelta(
            days=random.randint(0, 350)
        )
        status  = random.choice(ticket_statuses)
        resolved = None
        if status == "resolved":
            resolved = (
                created + timedelta(
                    days=random.randint(1, 14)
                )
            ).strftime("%Y-%m-%d")
        tickets.append((
            i,
            random.randint(1, 200),
            created.strftime("%Y-%m-%d"),
            random.choice(categories_t),
            status,
            random.choice(priorities),
            resolved
        ))
    cur.executemany(
        "INSERT OR IGNORE INTO "
        "support_tickets VALUES "
        "(?,?,?,?,?,?,?)",
        tickets
    )

    conn.commit()
    conn.close()
    print(
        f"  ✅ Database seeded: "
        f"{len(customers)} customers, "
        f"{len(products)} products, "
        f"{len(orders)} orders"
    )


def get_schema() -> str:
    """
    Return database schema as a
    formatted string for LLM context.
    """
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' "
        "ORDER BY name"
    )
    tables = [row[0] for row in cur.fetchall()]

    schema_parts = []
    for table in tables:
        cur.execute(
            f"PRAGMA table_info({table})"
        )
        cols = cur.fetchall()

        cur.execute(
            f"SELECT COUNT(*) FROM {table}"
        )
        count = cur.fetchone()[0]

        col_defs = ", ".join([
            f"{col[1]} {col[2]}"
            for col in cols
        ])
        schema_parts.append(
            f"Table: {table} ({count} rows)\n"
            f"Columns: {col_defs}"
        )

    conn.close()
    return "\n\n".join(schema_parts)


def execute_query(
    sql: str
) -> tuple:
    """
    Execute a SQL query safely.
    Returns (columns, rows, error).
    Read-only — only SELECT allowed.
    """
    sql_clean = sql.strip().rstrip(";")

    # Safety: only allow SELECT
    first_word = sql_clean.split()[0].upper() \
        if sql_clean.split() else ""

    if first_word != "SELECT":
        return (
            [], [],
            "Only SELECT queries are allowed. "
            "Write or delete operations "
            "are not permitted."
        )

    try:
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        cur.execute(sql_clean)
        rows = cur.fetchmany(100)
        cols = [
            desc[0]
            for desc in cur.description
        ] if cur.description else []
        conn.close()
        return cols, rows, None

    except sqlite3.Error as e:
        return [], [], str(e)

    except Exception as e:
        return [], [], str(e)


if __name__ == "__main__":
    build_database()
    print("\n📋 Schema:")
    print(get_schema())

    print("\n🧪 Test query:")
    cols, rows, err = execute_query(
        "SELECT COUNT(*) as total "
        "FROM customers"
    )
    if err:
        print(f"  ❌ Error: {err}")
    else:
        print(
            f"  ✅ Customers: {rows[0][0]}"
        )