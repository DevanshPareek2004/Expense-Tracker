import mysql.connector
from mysql.connector import Error
import bcrypt
from decimal import Decimal

def create_connection():
    """
    Establishes a connection to the MySQL database.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='dev123',  # Replace with your MySQL password
            database='expense_tracker'  # Replace with your database name
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def initialize_database():
    """
    Creates the `users` and `transactions` tables if they do not exist.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    Email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    currency VARCHAR(10) DEFAULT '₹ (INR)',
                    theme VARCHAR(10) DEFAULT 'light'  -- New column for theme preference
                )
            """)
            
            # Create transactions table with remark column
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    Email VARCHAR(255) NOT NULL,
                    type ENUM('Income', 'Expense') NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    date DATE NOT NULL,
                    remark VARCHAR(255)  -- New column for remarks
                )
            """)
            connection.commit()
            cursor.close()
            connection.close()
        except Error as e:
            print(f"Error initializing database: {e}")

def add_user(Email, password):
    """
    Registers a new user with a hashed password, default currency (INR), and default theme (light).
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            # Check if the user already exists
            cursor.execute("SELECT * FROM users WHERE Email = %s", (Email,))
            existing_user = cursor.fetchone()
            if existing_user:
                print("User already exists!")
                return False  # User already exists

            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insert new user with default currency (INR) and theme (light)
            cursor.execute("INSERT INTO users (Email, password, currency, theme) VALUES (%s, %s, %s, %s)", 
                           (Email, hashed_password, '₹ (INR)', 'light'))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error adding user: {e}")
            return False

def get_user(Email, password):
    """
    Retrieves user details including currency and theme preference.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE Email = %s", (Email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return user  # Return full user data, including currency and theme
            return None  # Invalid credentials
        except Error as e:
            print(f"Error fetching user: {e}")
            return None

def add_transaction(Email, trans_type, category, amount, date, remark=None):
    """
    Adds a transaction for the user with an optional remark.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO transactions (Email, type, category, amount, date, remark)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (Email, trans_type, category, amount, date, remark))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error adding transaction: {e}")
            return False

def get_transactions(Email, sort_by='date_desc'):
    connection = create_connection()
    transactions = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM transactions WHERE Email = %s", (Email,))
            transactions = cursor.fetchall()
            cursor.close()
            connection.close()

            # Apply sorting based on the sort_by parameter
            if sort_by == 'date_asc':
                transactions.sort(key=lambda x: x['date'])
            elif sort_by == 'date_desc':
                transactions.sort(key=lambda x: x['date'], reverse=True)
            elif sort_by == 'category_asc':
                transactions.sort(key=lambda x: x['category'].lower())
            elif sort_by == 'category_desc':
                transactions.sort(key=lambda x: x['category'].lower(), reverse=True)
            elif sort_by == 'remark_asc':
                transactions.sort(key=lambda x: x['remark'].lower() if x['remark'] else '')
            elif sort_by == 'remark_desc':
                transactions.sort(key=lambda x: x['remark'].lower() if x['remark'] else '', reverse=True)
            elif sort_by == 'type_asc':
                transactions.sort(key=lambda x: x['type'].lower())
            elif sort_by == 'type_desc':
                transactions.sort(key=lambda x: x['type'].lower(), reverse=True)
            elif sort_by == 'amount_asc':
                transactions.sort(key=lambda x: float(x['amount']))
            elif sort_by == 'amount_desc':
                transactions.sort(key=lambda x: float(x['amount']), reverse=True)

            return transactions
        except Error as e:
            print(f"Error fetching transactions: {e}")
            return []

def get_transactions_by_date(Email, start_date, end_date, sort_by='date_desc'):
    """
    Fetches transactions within a date range and sorts them.
    """
    connection = create_connection()
    transactions = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT * FROM transactions 
                WHERE Email = %s AND date BETWEEN %s AND %s
            """
            cursor.execute(query, (Email, start_date, end_date))
            transactions = cursor.fetchall()
            cursor.close()
            connection.close()

            # Apply sorting based on the sort_by parameter
            if sort_by == 'date_asc':
                transactions.sort(key=lambda x: x['date'])
            elif sort_by == 'date_desc':
                transactions.sort(key=lambda x: x['date'], reverse=True)
            elif sort_by == 'category_asc':
                transactions.sort(key=lambda x: x['category'].lower())
            elif sort_by == 'category_desc':
                transactions.sort(key=lambda x: x['category'].lower(), reverse=True)
            elif sort_by == 'remark_asc':
                transactions.sort(key=lambda x: x['remark'].lower() if x['remark'] else '')
            elif sort_by == 'remark_desc':
                transactions.sort(key=lambda x: x['remark'].lower() if x['remark'] else '', reverse=True)
            elif sort_by == 'type_asc':
                transactions.sort(key=lambda x: x['type'].lower())
            elif sort_by == 'type_desc':
                transactions.sort(key=lambda x: x['type'].lower(), reverse=True)
            elif sort_by == 'amount_asc':
                transactions.sort(key=lambda x: float(x['amount']))
            elif sort_by == 'amount_desc':
                transactions.sort(key=lambda x: float(x['amount']), reverse=True)

            return transactions
        except Error as e:
            print(f"Error fetching transactions by date: {e}")
            return []

def update_currency(Email, currency):
    """
    Updates the preferred currency for the user.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET currency = %s WHERE Email = %s", (currency, Email))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error updating currency: {e}")
            return False

def get_user_currency(Email):
    """
    Fetches the user's preferred currency from the database.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT currency FROM users WHERE Email = %s", (Email,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result['currency'] if result else '₹ (INR)'  # Default to INR if not set
        except Error as e:
            print(f"Error fetching currency: {e}")
            return '₹ (INR)'  # Return INR if an error occurs

def update_theme(Email, theme):
    """
    Updates the preferred theme for the user.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET theme = %s WHERE Email = %s", (theme, Email))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error updating theme: {e}")
            return False

def get_user_theme(Email):
    """
    Fetches the user's preferred theme from the database.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT theme FROM users WHERE Email = %s", (Email,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result['theme'] if result else 'light'  # Default to light theme
        except Error as e:
            print(f"Error fetching theme: {e}")
            return 'light'  # Default to light theme