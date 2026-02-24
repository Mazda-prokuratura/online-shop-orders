# models/order.py
from config import DATABASE_URL
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def create_order(client_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (client_id) VALUES (%s) RETURNING id;", (client_id,))
    oid = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return oid

def add_item_to_order(order_id, product_id, quantity):
    if quantity <= 0:
        raise ValueError("Количество должно быть больше нуля")

    conn = get_db()
    cur = conn.cursor()

    try:
        # Получаем текущий остаток
        cur.execute("SELECT stock_quantity FROM products WHERE id = %s;", (product_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Товар не найден")
        
        stock = row['stock_quantity']
        if stock < quantity:
            raise ValueError(f"Недостаточно товара на складе. Доступно: {stock}")

        # Уменьшаем остаток НА УКАЗАННОЕ КОЛИЧЕСТВО
        cur.execute(
            "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s;",
            (quantity, product_id)
        )

        # Добавляем позицию в заказ
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s);",
            (order_id, product_id, quantity)
        )

        conn.commit()
    except Exception as e:
        conn.rollback()  # ← ВАЖНО: откатываем при ошибке!
        raise e
    finally:
        cur.close()
        conn.close()

def get_all_orders():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.id, o.status, o.created_at, c.full_name as client_name
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        ORDER BY o.id DESC;
    """)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def set_order_status(order_id, status):
    valid = ['created', 'paid', 'shipped', 'completed', 'cancelled']
    if status not in valid:
        raise ValueError("Неверный статус")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = %s WHERE id = %s;", (status, order_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_order_by_id(order_id):
    """
    Удаляет заказ и все его позиции (order_items).
    PostgreSQL автоматически удаляет order_items благодаря ON DELETE CASCADE.
    """
    conn = get_db()
    cur = conn.cursor()
    try:
        # Удаляем заказ → каскадно удалятся все order_items
        cur.execute("DELETE FROM orders WHERE id = %s;", (order_id,))
        if cur.rowcount == 0:
            raise ValueError("Заказ не найден")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_order_details(order_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT o.id, o.status, o.created_at, 
                   c.full_name AS client_name, c.email
            FROM orders o
            JOIN clients c ON o.client_id = c.id
            WHERE o.id = %s;
        """, (order_id,))
        order_row = cur.fetchone()
        if not order_row:
            return None

        cur.execute("""
            SELECT p.name, oi.quantity, p.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s;
        """, (order_id,))
        item_rows = cur.fetchall()

        # Преобразуем в обычные словари
        order = dict(order_row)
        order_items = [dict(row) for row in item_rows]

        return {
            'order': order,
            'order_items': order_items  # ← ИЗМЕНЕНО: не 'items', а 'order_items'
        }
    finally:
        cur.close()
        conn.close()