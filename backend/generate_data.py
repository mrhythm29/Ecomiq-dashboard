import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

np.random.seed(42)
random.seed(42)

NUM_RECORDS = 5000
NUM_CUSTOMERS = 800
DAYS_HISTORY = 180

end_date = datetime.now()
start_date = end_date - timedelta(days=DAYS_HISTORY)

categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Toys']

products_dict = {
    'Electronics': [('Wireless Earbuds', 49.99), ('Smartwatch', 149.99), ('4K Monitor', 299.99), ('Mechanical Keyboard', 89.99)],
    'Clothing': [('T-Shirt', 19.99), ('Jeans', 49.99), ('Jacket', 89.99), ('Sneakers', 79.99)],
    'Home & Garden': [('Coffee Maker', 69.99), ('Blender', 49.99), ('Tool Set', 129.99), ('Planter', 24.99)],
    'Sports': [('Yoga Mat', 29.99), ('Dumbbells', 59.99), ('Tennis Racket', 119.99), ('Running Shoes', 99.99)],
    'Toys': [('Action Figure', 14.99), ('Board Game', 39.99), ('Puzzle', 19.99), ('RC Car', 49.99)]
}

all_products = []
for cat, items in products_dict.items():
    for name, price in items:
        all_products.append({'category': cat, 'product_name': name, 'unit_price': price})

data = []

for i in range(NUM_RECORDS):
    order_id = f"ORD-{10000 + i}"
    customer_id = f"CUST-{random.randint(100, 100 + NUM_CUSTOMERS - 1)}"

    days_offset = np.random.triangular(0, DAYS_HISTORY, DAYS_HISTORY)
    order_date = start_date + timedelta(days=days_offset)

    product = random.choice(all_products)

    quantity = random.choices([1, 2, 3, 4, 5], weights=[0.6, 0.2, 0.1, 0.05, 0.05])[0]

    data.append({
        'order_id': order_id,
        'customer_id': customer_id,
        'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
        'product_name': product['product_name'],
        'category': product['category'],
        'quantity': quantity,
        'unit_price': product['unit_price']
    })

df = pd.DataFrame(data)

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

csv_path = os.path.join(data_dir, 'ecommerce_data.csv')

df.to_csv(csv_path, index=False)

print(f"Generated {NUM_RECORDS} records at {csv_path}")