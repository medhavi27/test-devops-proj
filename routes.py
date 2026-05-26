# routes.py
from flask import Blueprint, jsonify, request
from database import get_db_connection  # Import our connection helper
from datadog import statsd
import time


# Create a blueprint named 'api'
api = Blueprint('api', __name__)
visit_count = 0

@api.route('/', methods=['GET'])
def home():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM menu;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        menu_items = [{"id": r[0], "name": r[1], "price": float(r[2])} for r in rows]
    except Exception:
        menu_items = []

    global visit_count
    visit_count += 1
    statsd.increment("app.page.visited", tags=["page:home"])

    menu_html = ""
    for item in menu_items:
        menu_html += f'''
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <div>
                <h3 style="margin: 5px 0 5px 0; color: #1e293b;">{item['name']}</h3>
                <span style="color: #059669; font-weight: 600; font-size: 1.1rem;">${item['price']:.2f}</span>
            </div>
            <button onclick="placeOrder({item['id']})" style="background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer;">
                Order Item
            </button>
        </div>
        '''

    html_template = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><title>DevOps Bites Cafe</title></head>
    <body style="font-family: system-ui, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px;">
    <h1>Hello from my DevOps app!</h1><p>Visits: {visit_count}</p>
        <div style="max-width: 600px; margin: 0 auto;">
            <header style="text-align: center; margin-bottom: 40px;">
                <h1 style="color: #0f172a; margin-bottom: 5px;">DevOps Bites Cafe 🍔</h1>
                <p style="color: #64748b; margin-top: 0;">Connected Live to PostgreSQL Container</p>
            </header>
            <div id="menu-container">{menu_html}</div>
            <div id="receipt-box" style="display: none; margin-top: 30px; background: #ecfdf5; border: 2px solid #10b981; border-radius: 12px; padding: 20px;">
                <h3 style="color: #065f46; margin-top: 0;">🎉 Order Successful!</h3>
                <pre id="receipt-data" style="margin: 0; font-family: monospace; color: #047857; font-size: 0.95rem;"></pre>
            </div>
        </div>
        <script>
        function placeOrder(itemId) {{
            fetch('/order', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ item_id: itemId, quantity: 1 }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.status === 'success') {{
                    document.getElementById('receipt-data').textContent = JSON.stringify(data.receipt, null, 2);
                    document.getElementById('receipt-box').style.display = 'block';
                    document.getElementById('receipt-box').scrollIntoView({{ behavior: 'smooth' }});
                }} else {{ alert('Order failed: ' + data.message); }}
            }});
        }}
        </script>
    </body>
    </html>
    '''

   
    
    return html_template

@api.route('/menu', methods=['GET'])
def get_menu():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM menu;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        menu_items = [{"id": r[0], "name": r[1], "price": float(r[2])} for r in rows]
        return jsonify({"status": "success", "data": menu_items}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api.route('/order', methods=['POST'])
def place_order():
    try:
        data = request.get_json()
        if not data or 'item_id' not in data:
            return jsonify({"status": "fail", "message": "Missing 'item_id'"}), 400
            
        item_id = data['item_id']
        quantity = data.get('quantity', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, price FROM menu WHERE id = %s;", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            cursor.close()
            conn.close()
            return jsonify({"status": "fail", "message": f"Item ID {item_id} not found"}), 404
            
        item_name, price = item[0], float(item[1])
        total_cost = price * quantity
        cursor.close()
        conn.close()

        statsd.increment('restaurant.orders', tags=["button:{item}", "env:production"])
        
        return jsonify({
            "status": "success",
            "receipt": {
                "item_ordered": item_name,
                "quantity": quantity,
                "total_price": total_cost,
                "status": "cooking"
            }
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api.route('/health-check', methods=['GET'])
def health_check():
    statsd.increment("app.health.checked")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        return jsonify({"status": "healthy", "database_connected": True, "timestamp": time.time()}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
    
@api.route("/metrics-test")
def metrics_test():
    statsd.increment("app.test_route.hit", tags=["env:dev"])
    return jsonify({"message": "Metric sent!"})