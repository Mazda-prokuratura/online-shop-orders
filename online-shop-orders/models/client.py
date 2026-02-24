# models/client.py
from config import DATABASE_URL
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_all_clients():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients ORDER BY id;")
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def create_client(full_name, email, phone=None, address=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clients (full_name, email, phone, address)
        VALUES (%s, %s, %s, %s) RETURNING id;
    """, (full_name, email, phone, address))
    client_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return client_id  # ← ОБЯЗАТЕЛЬНО вернуть 

def delete_client_by_id(client_id):
    conn = get_db()
    cur = conn.cursor()
    # Каскадное удаление заказов и order_items уже настроено в БД
    cur.execute("DELETE FROM clients WHERE id = %s;", (client_id,))
    conn.commit()
    cur.close()
    conn.close()