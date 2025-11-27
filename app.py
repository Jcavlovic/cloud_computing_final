# app.py
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory "database" – a simple list
inventory = [
    {"id": 1, "category": "GPU", "name": "RTX 4090", "quantity": 5, "price": 1599.99},
    {"id": 2, "category": "CPU", "name": "Ryzen 9 7950X", "quantity": 8, "price": 589.00},
    {"id": 3, "category": "RAM", "name": "32GB DDR5 6000MHz", "quantity": 15, "price": 189.99},
]

# Helper to get next ID
def get_next_id():
    return max([item["id"] for item in inventory], default=0) + 1

@app.route('/')
def index():
    return render_template('index.html', items=inventory)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        new_item = {
            "id": get_next_id(),
            "category": request.form['category'],
            "name": request.form['name'],
            "quantity": int(request.form['quantity']),
            "price": float(request.form['price'])
        }
        inventory.append(new_item)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/update/<int:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return "Item not found", 404

    if request.method == 'POST':
        item["category"] = request.form['category']
        item["name"] = request.form['name']
        item["quantity"] = int(request.form['quantity'])
        item["price"] = float(request.form['price'])
        return redirect(url_for('index'))

    return render_template('update.html', item=item)

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    global inventory
    inventory = [i for i in inventory if i["id"] != item_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)