# models/product.py
from config import DATABASE_URL
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_all_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY id;")
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def create_product(name, description, price, stock_quantity):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (name, description, price, stock_quantity)
        VALUES (%s, %s, %s, %s) RETURNING id;
    """, (name, description, price, stock_quantity))
    product_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return product_id  # ← ОБЯЗАТЕЛЬНО вернуть ID!

def delete_product_by_id(product_id):
    conn = get_db()
    cur = conn.cursor()
    # Проверка: нельзя удалить, если есть активные заказы (опционально)
    # Но в нашем случае — RESTRICT на order_items → PostgreSQL не даст удалить
    cur.execute("DELETE FROM products WHERE id = %s;", (product_id,))
    conn.commit()
    cur.close()
    conn.close()