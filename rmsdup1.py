import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
import pandas as pd

# Database connection
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='sulekha_02',
            database='Store',
            auth_plugin='mysql_native_password'
        )
    except Error as e:
        st.error(f"Error: '{e}'")
    return connection

# Hash the password (for user registration)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Verify manager credentials (no hashing)
def verify_manager(manager_id, password):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM Managers WHERE ManagerID = %s AND Password = %s"
    cursor.execute(query, (manager_id, password))
    manager = cursor.fetchone()
    cursor.close()
    connection.close()
    return manager is not None

# Register a new user
def register_user(email, password):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    query = "INSERT INTO Users (Email, Password) VALUES (%s, %s)"
    hashed_password = hash_password(password)
    try:
        cursor.execute(query, (email, hashed_password))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        st.error(f"Error: '{e}'")
        return False

# Verify user credentials (with hashed passwords)
def verify_user(email, password):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM Users WHERE Email = %s AND Password = %s"
    hashed_password = hash_password(password)
    cursor.execute(query, (email, hashed_password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user is not None

# Cart initialization (stored in session)
def init_cart():
    if 'cart' not in st.session_state:
        st.session_state.cart = {}

# Add item to the cart
def add_to_cart(product_id, name, price, available_qty, qty):
    if qty > available_qty:
        st.error("Not enough stock available!")
    else:
        if product_id in st.session_state.cart:
            st.session_state.cart[product_id]['qty'] += qty
        else:
            st.session_state.cart[product_id] = {
                'name': name,
                'price': price,
                'qty': qty
            }
        st.success(f"Added {qty} {name}(s) to the cart.")

# Calculate total bill (in rupees)
def calculate_total():
    total = 0
    for item in st.session_state.cart.values():
        total += item['price'] * item['qty']
    return total

# Manager Login page
def manager_login():
    st.subheader("Manager Login")
    manager_id = st.text_input("Manager ID")
    password = st.text_input("Password", type='password')
    if st.button("Log In as Manager"):
        if verify_manager(manager_id, password):
            st.session_state.current_page = "manager_dashboard"
            st.success("Manager Logged in Successfully!")
        else:
            st.error("Invalid Manager credentials")

    if st.button("Go Back"):
        st.session_state.current_page = "home"

# User Login page
def user_login():
    st.subheader("User Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type='password')
    if st.button("Log In as User"):
        if verify_user(email, password):
            st.session_state.current_page = "user_dashboard"
            st.success("User Logged in Successfully!")
        else:
            st.error("Invalid User credentials")

    if st.button("Go Back"):
        st.session_state.current_page = "home"

# User Signup page
def user_signup():
    st.subheader("User Signup")
    email = st.text_input("Email for Signup")
    create_password = st.text_input("Create Password", type='password')
    confirm_password = st.text_input("Confirm Password", type='password')
    if st.button("Sign Up"):
        if create_password == confirm_password:
            if register_user(email, create_password):
                st.success("User Registered Successfully!")
            else:
                st.error("Failed to register user.")
        else:
            st.error("Passwords do not match!")

    if st.button("Go Back"):
        st.session_state.current_page = "home"

# Manager Dashboard page
def manager_dashboard():
    st.title("Manager Dashboard")
    st.write("Manager Dashboard!")

    # Fetch all tables
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Select which table to operate on
    table_options = ["Products", "Categories", "Sales"]
    selected_table = st.selectbox("Select a table to manage:", table_options)

    # CRUD operations based on the selected table
    if selected_table:
        if st.button("View Records"):
            query = f"SELECT * FROM {selected_table}"
            cursor.execute(query)
            records = cursor.fetchall()
            st.write(pd.DataFrame(records))

        if st.button("Add Record"):
            if selected_table == "Products":
                product_name = st.text_input("Product Name")
                unit_price = st.number_input("Unit Price (in Rs)", min_value=0.0, format="%.2f")
                stock_quantity = st.number_input("Stock Quantity", min_value=0)

                if st.button("Submit"):
                    if product_name and unit_price is not None and stock_quantity is not None:
                        query = f"INSERT INTO Products (Name, UnitPrice, StockQuantity) VALUES (%s, %s, %s)"
                        cursor.execute(query, (product_name, unit_price, stock_quantity))
                        connection.commit()
                        st.success("Product added successfully!")
                    else:
                        st.error("Please fill all the fields correctly.")

            elif selected_table == "Categories":
                category_name = st.text_input("Category Name")
                if st.button("Submit"):
                    if category_name:
                        query = f"INSERT INTO Categories (Name) VALUES (%s)"
                        cursor.execute(query, (category_name,))
                        connection.commit()
                        st.success("Category added successfully!")
                    else:
                        st.error("Please enter a category name.")

            elif selected_table == "Sales":
                product_id = st.number_input("Product ID", min_value=1)
                quantity = st.number_input("Quantity", min_value=1)
                total_amount = st.number_input("Total Amount (in Rs)", min_value=0.0, format="%.2f")

                if st.button("Submit"):
                    if product_id and quantity > 0 and total_amount is not None:
                        query = f"INSERT INTO Sales (ProductID, Quantity, TotalAmount) VALUES (%s, %s, %s)"
                        cursor.execute(query, (product_id, quantity, total_amount))
                        connection.commit()
                        st.success("Sale record added successfully!")
                    else:
                        st.error("Please fill all the fields correctly.")

        if st.button("Update Record"):
            record_id = st.number_input("Enter Record ID to Update", min_value=1)
            if selected_table == "Products":
                attribute_to_update = st.selectbox("Select Attribute to Update", ["Name", "UnitPrice", "StockQuantity"])
                new_value = st.text_input("New Value")
                if st.button("Update"):
                    if attribute_to_update in ["UnitPrice", "StockQuantity"]:
                        new_value = float(new_value)  # Ensure it's a float
                    if new_value:  # Check if new_value is not empty
                        query = f"UPDATE Products SET {attribute_to_update} = %s WHERE ProductID = %s"
                        cursor.execute(query, (new_value, record_id))
                        connection.commit()
                        st.success("Record updated successfully!")
                    else:
                        st.error("Please provide a valid value.")

            elif selected_table == "Categories":
                record_id = st.number_input("Enter Category ID to Update", min_value=1)
                new_name = st.text_input("New Category Name")
                if st.button("Update"):
                    if new_name:  # Check if new_name is not empty
                        query = "UPDATE Categories SET Name = %s WHERE CategoryID = %s"
                        cursor.execute(query, (new_name, record_id))
                        connection.commit()
                        st.success("Category updated successfully!")
                    else:
                        st.error("Please provide a new category name.")

            elif selected_table == "Sales":
                record_id = st.number_input("Enter Sale ID to Update", min_value=1)
                attribute_to_update = st.selectbox("Select Attribute to Update", ["Quantity", "TotalAmount"])
                new_value = st.text_input("New Value")
                if st.button("Update"):
                    if attribute_to_update == "TotalAmount":
                        new_value = float(new_value)  # Ensure it's a float
                    if new_value:  # Check if new_value is not empty
                        query = f"UPDATE Sales SET {attribute_to_update} = %s WHERE SaleID = %s"
                        cursor.execute(query, (new_value, record_id))
                        connection.commit()
                        st.success("Sale record updated successfully!")
                    else:
                        st.error("Please provide a valid value.")

        if st.button("Delete Record"):
            record_id = st.number_input("Enter Record ID to Delete", min_value=1)
            if selected_table == "Products":
                if st.button("Delete"):
                    if record_id:  # Check if record_id is not empty
                        query = "DELETE FROM Products WHERE ProductID = %s"
                        cursor.execute(query, (record_id,))
                        connection.commit()
                        st.success("Product deleted successfully!")
                    else:
                        st.error("Please enter a valid record ID.")

            elif selected_table == "Categories":
                if st.button("Delete"):
                    if record_id:  # Check if record_id is not empty
                        query = "DELETE FROM Categories WHERE CategoryID = %s"
                        cursor.execute(query, (record_id,))
                        connection.commit()
                        st.success("Category deleted successfully!")
                    else:
                        st.error("Please enter a valid record ID.")

            elif selected_table == "Sales":
                if st.button("Delete"):
                    if record_id:  # Check if record_id is not empty
                        query = "DELETE FROM Sales WHERE SaleID = %s"
                        cursor.execute(query, (record_id,))
                        connection.commit()
                        st.success("Sale record deleted successfully!")
                    else:
                        st.error("Please enter a valid record ID.")

    cursor.close()
    connection.close()

    if st.button("Go Back"):
        st.session_state.current_page = "home"

# User Dashboard page with Cart functionality
def user_dashboard():
    st.title("User Dashboard")
    st.write("User Dashboard!")

    # Initialize the cart if not already initialized
    init_cart()

    # Fetch products from the database
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

    # Select a product and specify quantity
    st.subheader("Available Products")
    product_df = pd.DataFrame(products, columns=['ProductID', 'Name', 'UnitPrice', 'StockQuantity'])
    selected_product = st.selectbox("Select a Product to Add to Cart", product_df['Name'].values)
    selected_product_info = product_df[product_df['Name'] == selected_product].iloc[0]
    
    # Show only the price
    st.write(f"Price per unit: ₹ {selected_product_info['UnitPrice']}")
    
    # Get quantity
    qty = st.number_input("Select Quantity", min_value=1, max_value=int(selected_product_info['StockQuantity']), value=1)

    if st.button("Add to Cart"):
        add_to_cart(
            selected_product_info['ProductID'],
            selected_product_info['Name'],
            selected_product_info['UnitPrice'],
            selected_product_info['StockQuantity'],
            qty
        )

    # Show the cart with the current items
    if st.button("View Cart"):
        if not st.session_state.cart:
            st.warning("Your cart is empty.")
        else:
            st.write("Your Cart:")
            for item_id, item in st.session_state.cart.items():
                st.write(f"{item['name']} (Price: ₹ {item['price']}, Quantity: {item['qty']})")

            # Calculate total and payment button
            total_amount = calculate_total()
            st.write(f"**Total Amount (in ₹):** {total_amount}")

            if st.button("Proceed to Payment"):
                st.success("Thank you for your purchase!")
                st.session_state.cart = {}

    if st.button("Go Back"):
        st.session_state.current_page = "home"

# Main page that switches between different functionalities
def main():
    st.set_page_config(page_title="Retail Management System")

    # Display Home page by default
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"

    # Navigate between pages
    if st.session_state.current_page == "home":
        st.title("Welcome to Retail Management System")
        st.write("Please select an option to proceed.")

        # Login and signup options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("User Login"):
                st.session_state.current_page = "user_login"
        with col2:
            if st.button("Manager Login"):
                st.session_state.current_page = "manager_login"

    elif st.session_state.current_page == "user_login":
        user_login()

    elif st.session_state.current_page == "user_signup":
        user_signup()

    elif st.session_state.current_page == "manager_login":
        manager_login()

    elif st.session_state.current_page == "manager_dashboard":
        manager_dashboard()

    elif st.session_state.current_page == "user_dashboard":
        user_dashboard()

if __name__ == "__main__":
    main()
