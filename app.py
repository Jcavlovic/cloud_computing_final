# app.py
from flask import Flask, render_template, request, redirect, url_for
import boto3
from boto3.dynamodb.conditions import Key
import uuid
from decimal import Decimal

app = Flask(__name__)

# DynamoDB Configuration
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('ElectronicsInventory')

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

@app.route('/')
def index():
    # Scan the table to get all items
    response = table.scan()
    items = response.get('Items', [])
    
    # Converting Decimals to floats for the template.
    for item in items:
        item['price'] = float(item['price'])
        # Ensure 'id' exists for the template to use (mapping sku to id)
        item['id'] = item['sku']
        # Map stock_quantity to quantity for template compatibility
        item['quantity'] = int(item.get('stock_quantity', 0))
        
    return render_template('index.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        # Generate a unique SKU
        category = request.form['category']
        name = request.form['name']
        short_name = name[:3].upper().replace(" ", "")
        random_suffix = str(uuid.uuid4())[:4].upper()
        generated_sku = f"{category}-{short_name}-{random_suffix}"
        
        new_item = {
            "sku": generated_sku,
            "category": category,
            "name": name,
            "stock_quantity": int(request.form['quantity']),
            "price": Decimal(request.form['price']),
            "threshold": 5 # Default threshold
        }
        
        table.put_item(Item=new_item)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/update/<string:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    # item_id is the sku
    if request.method == 'POST':
        # Update the item
        table.update_item(
            Key={'sku': item_id},
            UpdateExpression="set category=:c, #n=:n, stock_quantity=:q, price=:p",
            ExpressionAttributeNames={
                "#n": "name"
            },
            ExpressionAttributeValues={
                ':c': request.form['category'],
                ':n': request.form['name'],
                ':q': int(request.form['quantity']),
                ':p': Decimal(request.form['price'])
            }
        )
        return redirect(url_for('index'))

    # Get the item to pre-fill the form
    response = table.get_item(Key={'sku': item_id})
    item = response.get('Item')
    
    if not item:
        return "Item not found", 404
        
    item['price'] = float(item['price'])
    item['id'] = item['sku'] # For template compatibility
    item['quantity'] = int(item.get('stock_quantity', 0))
    
    return render_template('update.html', item=item)

@app.route('/delete/<string:item_id>')
def delete_item(item_id):
    table.delete_item(Key={'sku': item_id})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)