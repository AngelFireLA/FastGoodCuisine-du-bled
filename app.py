from flask import Flask, render_template, request, redirect, jsonify
import csv
from datetime import datetime

app = Flask(__name__)
CSV_FILE = 'food_inventory.csv'


# Utility function to read CSV
def read_csv():
    with open(CSV_FILE, mode='r', newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


# Utility function to write to CSV
def write_csv(data):
    with open(CSV_FILE, mode='a', newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=['type', 'name', 'role', 'expiration_date', 'quantity'])
        writer.writerow(data)


# Utility function to update CSV (for stacking items or updating quantity)
def update_csv(data):
    rows = read_csv()
    found = False
    with open(CSV_FILE, mode='w', newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=['type', 'name', 'role', 'role_percentage','expiration_date', 'quantity'])
        writer.writeheader()
        for row in rows:
            if row['type'] == data['type'] and row['name'] == data['name']:
                row['quantity'] = str(int(row['quantity']) + int(data['quantity']))
                found = True
            writer.writerow(row)
        if not found:
            writer.writerow(data)


# Route to add new food item
@app.route('/ajouter', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        food_type = request.form['type']
        name = request.form['name']
        role = request.form['role']
        expiration_date = request.form['expiration_date']
        quantity = int(request.form['quantity'])
        role_percentage = request.form['role_percentage']

        # Update or Add new item
        update_csv({
            'type': food_type,
            'name': name,
            'role': role,
            'role_percentage': role_percentage,
            'expiration_date': expiration_date,
            'quantity': quantity

        })
        return redirect('/inventaire')

    return render_template('ajouter.html')


@app.route("/")
# Route to view inventory
@app.route('/inventaire')
def view_inventory():
    inventory = read_csv()
    # Sort by expiration date
    inventory.sort(key=lambda x: datetime.strptime(x['expiration_date'], '%Y-%m-%d'))
    inventory = [item for item in inventory if float(item["quantity"]) > 0]
    return render_template('inventaire.html', items=inventory)


# Route to delete an item
@app.route('/supprimer/<type>/<name>')
def delete_item(type, name):
    rows = read_csv()
    with open(CSV_FILE, mode='w', newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=['type', 'name', 'role', 'role_percentag','expiration_date', 'quantity'])
        writer.writeheader()
        for row in rows:
            if not (row['type'] == type and row['name'] == name):
                writer.writerow(row)
    return redirect('/inventaire')


# Route to edit an item
@app.route('/modifier/<type>/<name>', methods=['GET', 'POST'])
def edit_item(type, name):
    if request.method == 'POST':
        updated_data = {
            'type': request.form['type'],
            'name': request.form['name'],
            'role': request.form['role'],
            'role_percentage': request.form['role_percentage'],
            'expiration_date': request.form['expiration_date'],
            'quantity': request.form['quantity']

        }
        delete_item(type, name)  # Delete the old entry
        write_csv(updated_data)  # Add the updated entry
        return redirect('/inventaire')

    # Retrieve the current item data to pre-fill the form
    items = read_csv()
    item = next((i for i in items if i['type'] == type and i['name'] == name), None)
    return render_template('modifier.html', item=item)


# Route for generating meal suggestions
@app.route('/suggestion')
def suggest_meal():
    inventory = read_csv()

    # Helper function to filter by role and expiration date
    def filter_items_by_role(inventory, role):
        today = datetime.today()
        filtered_items = [item for item in inventory if item['role'] == role]
        filtered_items.sort(key=lambda x: (datetime.strptime(x['expiration_date'], '%Y-%m-%d') - today).days)
        return filtered_items

    # Get items based on roles
    plats = filter_items_by_role(inventory, 'Plat')
    accompagnements = filter_items_by_role(inventory, 'Accompagnement')
    desserts = filter_items_by_role(inventory, 'Dessert')

    # Select the top choice from each role
    meal = {
        'plat': plats[0] if plats else None,
        'accompagnement': accompagnements[0] if accompagnements else None,
        'dessert': desserts[0] if desserts else None
    }

    return render_template('suggestion.html', meal=meal)


# Route to provide data for autocomplete fields
@app.route('/get-food-data')
def get_food_data():
    inventory = read_csv()
    types = {item['type'] for item in inventory}
    names = {item['name'] for item in inventory}

    return jsonify({
        'types': list(types),
        'names': list(names)
    })


if __name__ == '__main__':
    app.run(debug=True)
