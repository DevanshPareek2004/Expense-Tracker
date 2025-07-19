import mysql.connector
from mysql.connector import Error
import bcrypt
from decimal import Decimal

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='expense_tracker'
        )
        return connection
    except Error as e:
        return None

def initialize_database():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    Email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    currency VARCHAR(10) DEFAULT '₹ (INR)',
                    theme VARCHAR(10) DEFAULT 'light'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    Email VARCHAR(255) NOT NULL,
                    type ENUM('Income', 'Expense') NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    date DATE NOT NULL,
                    remark VARCHAR(255)
                )
            """)
            connection.commit()
            cursor.close()
            connection.close()
        except Error as e:
            pass

def add_user(Email, password):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE Email = %s", (Email,))
            existing_user = cursor.fetchone()
            if existing_user:
                return False

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            cursor.execute("INSERT INTO users (Email, password, currency, theme) VALUES (%s, %s, %s, %s)", 
                           (Email, hashed_password, '₹ (INR)', 'light'))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            return False

def get_user(Email, password):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE Email = %s", (Email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return user
            return None
        except Error as e:
            return None

def add_transaction(Email, trans_type, category, amount, date, remark=None):
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
            return []

def get_transactions_by_date(Email, start_date, end_date, sort_by='date_desc'):
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
            return []

def update_transaction(transaction_id, Email, trans_type, category, amount, date, remark=None):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE transactions 
                SET type = %s, category = %s, amount = %s, date = %s, remark = %s
                WHERE id = %s AND Email = %s
            """, (trans_type, category, amount, date, remark, transaction_id, Email))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            return False

def delete_transaction(transaction_id, Email):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = %s AND Email = %s", (transaction_id, Email))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            return False

def get_transaction_by_id(transaction_id, Email):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM transactions WHERE id = %s AND Email = %s", (transaction_id, Email))
            transaction = cursor.fetchone()
            cursor.close()
            connection.close()
            return transaction
        except Error as e:
            return None

def update_currency(Email, currency):
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
            return False

def get_user_currency(Email):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT currency FROM users WHERE Email = %s", (Email,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result['currency'] if result else '₹ (INR)'
        except Error as e:
            return '₹ (INR)'

def update_theme(Email, theme):
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
            return False

def get_user_theme(Email):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT theme FROM users WHERE Email = %s", (Email,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result['theme'] if result else 'light'
        except Error as e:
            return 'light'