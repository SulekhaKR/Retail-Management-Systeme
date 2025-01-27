Retail Management System

A user-friendly Streamlit-based application for managing retail operations with functionality for both managers and users. This system facilitates inventory management, sales processing, user registration, cart management, and more.

---

## Features

### Manager Functionalities:
- **Login**: Secure authentication for managers.
- **CRUD Operations**: Manage records across tables like `Products`, `Categories`, and `Sales`:
  - View records
  - Add new entries
  - Update existing entries
  - Delete records
- **Dashboard**: Intuitive interface for managing retail operations.

### User Functionalities:
- **Signup & Login**: Secure user registration and authentication.
- **Product Catalog**: Browse available products with pricing and stock details.
- **Cart Management**: Add items to the cart, view the cart, and proceed to checkout.
- **Payment**: Simulated payment functionality after calculating the total bill.

---

## Technologies Used
- **Frontend**: [Streamlit](https://streamlit.io/) for building an interactive user interface.
- **Backend**: MySQL for database management.
- **Libraries**:
  - `mysql-connector` for connecting to the MySQL database.
  - `hashlib` for secure password hashing.
  - `pandas` for data manipulation and display.

---

## Prerequisites

- Python 3.8 or above
- MySQL server with the `Store` database configured.
- Installed Python libraries:
  ```bash
  pip install streamlit mysql-connector-python pandas
