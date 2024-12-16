from flask import Flask, render_template, request, redirect, url_for
import qrcode
import mysql.connector
import os

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Plz add here your password ",  # Make sure this is secure for production
    database="MenuSystem"
)
cursor = db.cursor()

# Admin route to add menu items
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Add menu items to the database
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        cursor.execute("INSERT INTO menu_items (name, description, price) VALUES (%s, %s, %s)", 
                       (name, description, price))
        db.commit()

        # Generate updated QR Code after adding menu
        generate_qr_code()

        # Redirect to the QR code display page
        return redirect('/qr-code')

    # Fetch all menu items to display in the admin page
    cursor.execute("SELECT * FROM menu_items")
    menu = cursor.fetchall()
    return render_template('admin.html', menu=menu)

# QR Code Display Route
@app.route('/qr-code', methods=['GET'])
def qr_code():
    # Render the QR code image for user scanning
    qr_code_path = os.path.join('static', 'qr_code.png')
    return render_template('qr_code.html', qr_code_path=qr_code_path)

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    # Fetch menu items from the database
    cursor.execute("SELECT * FROM menu_items")
    menu_items = cursor.fetchall()

    if request.method == 'POST':
        # Process order
        user_name = request.form['user_name']
        order_details = request.form.getlist('order')  # This will be a list of selected item IDs
        cursor.execute("INSERT INTO orders (user_name, order_details) VALUES (%s, %s)",
                       (user_name, ', '.join(order_details)))  # Save order in the database
        db.commit()
        return "<h1>Order Placed Successfully!</h1>"

    return render_template('menu.html', menu_items=menu_items)  # Pass menu items to the template

# Function to generate QR Code
def generate_qr_code():
    # Replace 'localhost' with your server's public IP or domain when deployed
    base_url = "http://localhost:5000"  # Change 'localhost' to your deployment URL
    menu_url = f"{base_url}/menu"  # URL for the menu page

    # Generate QR Code for the menu URL
    qr = qrcode.make(menu_url)
    qr.save(os.path.join('static', 'qr_code.png'))  # Save QR Code in the static folder

if __name__ == '__main__':
    app.run(debug=True)
