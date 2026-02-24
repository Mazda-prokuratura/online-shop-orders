from flask import Flask, render_template, request, redirect, url_for, flash
from models.client import get_all_clients, create_client, delete_client_by_id
from models.product import get_all_products, create_product, delete_product_by_id
from models.order import (
    create_order,
    add_item_to_order,
    get_all_orders,
    set_order_status,
    delete_order_by_id,
    get_order_details
)
import psycopg2
from psycopg2.errors import UniqueViolation, ForeignKeyViolation

app = Flask(__name__)
app.secret_key = 'secret_key_for_coursework'

# === Главная страница ===
@app.route('/')
def index():
    return render_template('index.html')

# === Clients ===
@app.route('/clients')
def clients():
    return render_template('clients.html', clients=get_all_clients())

@app.route('/clients/new', methods=['GET', 'POST'])
def new_client():
    if request.method == 'POST':
        try:
            create_client(
                request.form['full_name'],
                request.form['email'].lower().strip(),
                request.form.get('phone') or None,
                request.form.get('address') or None
            )
            flash("Клиент добавлен", "success")
            return redirect(url_for('clients'))
        except UniqueViolation:
            flash("Клиент с таким email уже существует", "error")
        except Exception as e:
            flash(f"Ошибка при добавлении клиента: {str(e)}", "error")
    return render_template('new_client.html')

@app.route('/clients/<int:client_id>/delete', methods=['POST'])
def delete_client(client_id):
    try:
        delete_client_by_id(client_id)
        flash("Клиент удалён", "success")
    except Exception as e:
        flash(f"Ошибка при удалении: {e}", "error")
    return redirect(url_for('clients'))

# === Products ===
@app.route('/products')
def products():
    return render_template('products.html', products=get_all_products())

@app.route('/products/new', methods=['GET', 'POST'])
def new_product():
    if request.method == 'POST':
        try:
            create_product(
                request.form['name'],
                request.form.get('description', ''),
                float(request.form['price']),
                int(request.form['stock_quantity'])
            )
            flash("Товар добавлен", "success")
            return redirect(url_for('products'))
        except Exception as e:
            flash(f"Ошибка при добавлении товара: {e}", "error")
    return render_template('new_product.html')

@app.route('/products/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    try:
        delete_product_by_id(product_id)
        flash("Товар удалён", "success")
    except ForeignKeyViolation:
        flash("Нельзя удалить товар: он используется в заказах.", "error")
    except Exception as e:
        flash(f"Ошибка при удалении: {e}", "error")
    return redirect(url_for('products'))

# === Orders ===
@app.route('/orders')
def orders():
    return render_template('orders.html', orders=get_all_orders())

@app.route('/orders/new', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        try:
            client_id = int(request.form['client_id'])
            order_id = create_order(client_id)
            product_ids = request.form.getlist('product_id')
            quantities = request.form.getlist('quantity')
            for pid, qty in zip(product_ids, quantities):
                qty_int = int(qty)
                if qty_int > 0:
                    add_item_to_order(order_id, int(pid), qty_int)
            flash("Заказ создан", "success")
            return redirect(url_for('orders'))
        except ValueError as e:
            flash(f"Ошибка: {str(e)}", "error")
        except Exception as e:
            flash(f"Системная ошибка: {str(e)}", "error")
    return render_template('create_order.html',
                           clients=get_all_clients(),
                           products=get_all_products())

@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    try:
        set_order_status(order_id, request.form['status'])
        flash("Статус обновлён", "success")
    except Exception as e:
        flash(f"Ошибка при обновлении статуса: {e}", "error")
    return redirect(url_for('orders'))

@app.route('/orders/<int:order_id>/delete', methods=['POST'])
def delete_order(order_id):
    try:
        delete_order_by_id(order_id)
        flash("Заказ удалён", "success")
    except Exception as e:
        flash(f"Ошибка при удалении заказа: {e}", "error")
    return redirect(url_for('orders'))

# === Просмотр заказа ===
@app.route('/orders/<int:order_id>')
def view_order(order_id):
    details = get_order_details(order_id)
    if not details:
        flash("Заказ не найден", "error")
        return redirect(url_for('orders'))
    return render_template('view_order.html', details=details)

# === Запуск приложения ===
if __name__ == '__main__':
    app.run(debug=True)