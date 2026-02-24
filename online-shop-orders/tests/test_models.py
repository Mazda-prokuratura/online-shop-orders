# tests/test_models.py
import pytest
import uuid
from models.client import create_client, get_all_clients
from models.product import create_product, get_all_products
from models.order import create_order, add_item_to_order, get_all_orders

def test_full_workflow():
    # Генерируем уникальный email для каждого запуска
    unique_email = f"test_{uuid.uuid4().hex[:8]}@shop.ru"

    cid = create_client("Тест Клиент", unique_email)
    pid = create_product("Тестовый товар", "Описание", 99.99, 5)

    oid = create_order(cid)
    add_item_to_order(oid, pid, 2)

    orders = get_all_orders()
    assert len(orders) >= 1
    assert orders[0]['id'] == oid
    assert orders[0]['status'] == 'created'