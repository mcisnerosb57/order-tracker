from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id')
    item_name = data.get('item_name')
    quantity = data.get('quantity')
    customer_id = data.get('customer_id')
    if not all([order_id, item_name, quantity is not None, customer_id]):
        return jsonify({"error": "order_id, item_name, quantity and customer_id are required"}), 400
    status = data.get('status', 'pending')
    order_tracker.add_order(order_id, item_name, quantity, customer_id, status)
    return jsonify(order_tracker.get_order_by_id(order_id)), 201

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get('new_status')
    try:
        order_tracker.update_order_status(order_id, new_status)
    except ValueError:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order_tracker.get_order_by_id(order_id)), 200

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get('status')
    if status:
        orders = order_tracker.list_orders_by_status(status)
    else:
        orders = order_tracker.list_all_orders()
    return jsonify(orders), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
