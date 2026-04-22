import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "customer.db")

_CUSTOMERS = [
    ('Alice', 'alice@example.com', 30),
    ('Bob',   'bob@example.com',   25),
    ('Carol', 'carol@example.com', 28),
    ('Ema',   'ema@example.com',   32),
]

_TICKETS = [
    (1, 'Order not received',       'closed',      '2024-11-03', 'Alice reported that her order #1021 did not arrive within the expected window. Resolved after confirming reshipment.'),
    (1, 'Wrong item shipped',        'closed',      '2025-01-15', 'Received a different product than ordered. Replacement sent and confirmed delivered.'),
    (2, 'Refund request for return', 'closed',      '2025-02-08', 'Bob requested a refund after returning a defective item. Refund processed within 5 business days.'),
    (2, 'Account login issue',       'closed',      '2025-03-20', 'Unable to log in after password reset. Resolved by support resetting 2FA.'),
    (3, 'Billing discrepancy',       'in_progress', '2025-04-01', 'Carol was charged twice for the same order. Investigation ongoing with the payments team.'),
    (4, 'Shipping delay inquiry',    'closed',      '2025-03-05', 'Ema inquired about a delayed shipment. Carrier confirmed delay due to weather; package delivered the next day.'),
    (4, 'Product quality complaint', 'open',        '2025-04-10', 'Ema reported that the product arrived damaged. Awaiting photo evidence to process replacement or refund.'),
]


def init_db():
    """Create tables and seed sample data if the database does not yet exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS customers (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            email TEXT    NOT NULL,
            age   INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS support_tickets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            subject     TEXT    NOT NULL,
            status      TEXT    NOT NULL CHECK(status IN ('open', 'in_progress', 'closed')),
            created_at  TEXT    NOT NULL,
            description TEXT    NOT NULL
        );
    ''')
    if c.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
        c.executemany("INSERT INTO customers (name, email, age) VALUES (?, ?, ?)", _CUSTOMERS)
        c.executemany(
            "INSERT INTO support_tickets (customer_id, subject, status, created_at, description) VALUES (?, ?, ?, ?, ?)",
            _TICKETS,
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
