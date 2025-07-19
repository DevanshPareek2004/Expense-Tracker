from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from database import initialize_database, add_user, get_user, add_transaction, get_transactions, Error, create_connection, update_currency, get_user_currency, get_user_theme, update_theme, get_transaction_by_id, update_transaction, delete_transaction
import bcrypt
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from smtp_handler import send_email, generate_otp, send_welcome_email, send_password_change_email, send_dashboard_reset_email, send_otp_email, generate_transactions_pdf
import re
import os
from werkzeug.utils import secure_filename
from gemini_api import extract_data_from_image

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def reset_monthly_transactions():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE transactions SET amount = 0 WHERE type IN ('Income', 'Expense')")
            connection.commit()
            cursor.close()
            connection.close()
        except Error as e:
            pass

scheduler = BackgroundScheduler()
scheduler.add_job(func=reset_monthly_transactions, trigger='cron', month='*', day=1)
scheduler.start()

initialize_database()

@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_theme = session.get('theme', 'light')

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            extracted_data = extract_data_from_image(file_path)

            if extracted_data:
                return render_template('edit_extracted_data.html', 
                                      extracted_data=extracted_data, 
                                      user_theme=user_theme)
            else:
                flash('Failed to extract data from the image. Please enter the details manually.', 'error')
                return render_template('edit_extracted_data.html', 
                                      extracted_data={"price": "", "date": "", "category": ""}, 
                                      user_theme=user_theme)

    return render_template('upload_image.html', user_theme=user_theme)

@app.route('/add_expense_from_image', methods=['POST'])
def add_expense_from_image():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    category = request.form.get('category')
    amount = request.form.get('amount')
    date = request.form.get('date')
    remark = request.form.get('remark')

    if not category or not amount or not date:
        return "Missing required fields!", 400

    try:
        amount = float(amount)
    except ValueError:
        return "Invalid amount!", 400

    if add_transaction(Email, 'Expense', category, amount, date, remark):
        flash('Expense added successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        return "Error adding transaction!", 500

def get_transactions_by_date(Email, start_date, end_date, sort_by='date_desc'):
    connection = create_connection()
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

def get_transactions(Email, sort_by='date_desc'):
    connection = create_connection()
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

@app.route('/')
def home():
    user_theme = session.get('theme', 'light')
    return render_template('index.html', user_theme=user_theme)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        Email = request.form['Email'].strip()
        password = request.form['password'].strip()

        user = get_user(Email, password)
        if user:
            session['user_id'] = Email
            session['theme'] = get_user_theme(Email)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Email or Password!", "error")
            return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        Email = request.form['Email'].strip()
        password = request.form['password'].strip()

        if add_user(Email, password):
            send_welcome_email(Email)
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('home'))
        else:
            flash("Email already exists!", "error")
            return redirect(url_for('home'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    user_theme = session.get('theme', 'light')

    if request.method == 'POST':
        email = request.form.get('Email').strip()

        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
                user = cursor.fetchone()
                cursor.close()
                connection.close()

                if user:
                    email_sent, otp = send_otp_email(email)
                    if email_sent:
                        session['otp'] = otp
                        session['otp_email'] = email
                        session['otp_time'] = datetime.now().isoformat()
                        return redirect(url_for('enter_otp'))
                    else:
                        flash("Error sending OTP. Please try again.", "error")
                        return redirect(url_for('forgot_password'))
                else:
                    flash("Email not found. Please check your email address.", "error")
                    return redirect(url_for('forgot_password'))
            except Error as e:
                flash("An error occurred. Please try again.", "error")
                return redirect(url_for('forgot_password'))
        else:
            flash("Database connection error. Please try again.", "error")
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html', user_theme=user_theme)

@app.route('/enter_otp', methods=['GET', 'POST'])
def enter_otp():
    user_theme = session.get('theme', 'light')

    if request.method == 'POST':
        user_otp = request.form.get('otp')

        if 'otp' not in session or 'otp_time' not in session or 'otp_email' not in session:
            flash("Session expired. Please request a new OTP.", "error")
            return redirect(url_for('forgot_password'))

        otp_time = session['otp_time']
        if isinstance(otp_time, str):
            otp_time = datetime.fromisoformat(otp_time)

        if otp_time.tzinfo is not None:
            otp_time = otp_time.replace(tzinfo=None)

        current_time = datetime.now()

        if str(session['otp']) == user_otp:
            if current_time - otp_time < timedelta(minutes=5):
                session['otp_email'] = session.get('otp_email')
                return redirect(url_for('reset_password'))
            else:
                flash("OTP expired. Please request a new one.", "error")
                return redirect(url_for('forgot_password'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('enter_otp'))

    return render_template('enter_otp.html', user_theme=user_theme)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    user_theme = session.get('theme', 'light')

    if 'otp_email' not in session:
        flash("Unauthorized access. Please request a new OTP.", "error")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')

        if not new_password:
            flash("New password is required.", "error")
            return redirect(url_for('reset_password'))

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE users SET password = %s WHERE Email = %s", (hashed_password, session['otp_email']))
                connection.commit()
                cursor.close()
                connection.close()

                send_password_change_email(session['otp_email'])

                session.pop('otp', None)
                session.pop('otp_email', None)
                session.pop('otp_time', None)

                flash("Password changed successfully!", "success")
                return redirect(url_for('home'))
            except Error as e:
                flash("An error occurred. Please try again.", "error")
                return redirect(url_for('reset_password'))
        else:
            flash("Database connection error. Please try again.", "error")
            return redirect(url_for('reset_password'))

    return render_template('reset_password.html', user_theme=user_theme)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('register'))

    Email = session['user_id']
    date_filter = request.args.get('date_filter', 'all')
    user_theme = session.get('theme', 'light')
    user_currency = get_user_currency(Email)

    today = datetime.today()
    start_date = None
    end_date = None

    if date_filter == 'today':
        start_date = today
        end_date = today
    elif date_filter == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif date_filter == 'month':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif date_filter == 'last_month':
        start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        end_date = today.replace(day=1) - timedelta(days=1)
    elif date_filter == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)

    if start_date and end_date:
        transactions = get_transactions_by_date(Email, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    else:
        transactions = get_transactions(Email)

    total_income = sum(t['amount'] for t in transactions if t.get('type') == 'Income')
    total_expense = sum(t['amount'] for t in transactions if t.get('type') == 'Expense')
    balance = total_income - total_expense

    last_10_transactions = transactions[:10]

    return render_template(
        'dashboard.html',
        Email=Email,
        balance=balance,
        income=total_income,
        expense=total_expense,
        transactions=last_10_transactions,
        date_filter=date_filter,
        user_currency=user_currency,
        user_theme=user_theme
    )
@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    transaction = get_transaction_by_id(transaction_id, Email)
    
    if not transaction:
        flash("Transaction not found or you don't have permission to edit it", "error")
        return redirect(url_for('all_transactions'))

    user_theme = session.get('theme', 'light')

    if request.method == 'POST':
        trans_type = request.form.get('type')
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')
        remark = request.form.get('remark')

        if not trans_type or not category or not amount or not date:
            flash("Missing required fields!", "error")
            return redirect(url_for('edit_transaction', transaction_id=transaction_id))

        try:
            amount = float(amount)
        except ValueError:
            flash("Invalid amount!", "error")
            return redirect(url_for('edit_transaction', transaction_id=transaction_id))

        if update_transaction(transaction_id, Email, trans_type, category, amount, date, remark):
            flash("Transaction updated successfully!", "success")
            return redirect(url_for('all_transactions'))
        else:
            flash("Error updating transaction!", "error")
            return redirect(url_for('edit_transaction', transaction_id=transaction_id))

    return render_template('edit_transaction.html', 
                         transaction=transaction, 
                         user_theme=user_theme)

@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction_route(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    
    if delete_transaction(transaction_id, Email):
        flash("Transaction deleted successfully!", "success")
    else:
        flash("Error deleting transaction!", "error")
    
    return redirect(url_for('all_transactions'))

@app.route('/toggle_menu')
def toggle_menu():
    session['menu_open'] = not session.get('menu_open', False)
    return redirect(url_for('dashboard'))

@app.route('/change_currency', methods=['POST'])
def change_currency():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    new_currency = request.form.get('currency')
    update_currency(Email, new_currency)
    session['currency'] = new_currency
    flash("Currency updated successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_theme = session.get('theme', 'light')

    if request.method == 'POST':
        username = session['user_id']
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')
        remark = request.form.get('remark')

        if not category or not amount or not date:
            return "Missing required fields!", 400

        try:
            amount = float(amount)
        except ValueError:
            return "Invalid amount!", 400

        if add_transaction(username, 'Expense', category, amount, date, remark):
            return redirect(url_for('dashboard'))
        else:
            return "Error adding transaction!", 500

    return render_template('add_expense.html', user_theme=user_theme)

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_theme = session.get('theme', 'light')

    if request.method == 'POST':
        username = session['user_id']
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')
        remark = request.form.get('remark')

        if not category or not amount or not date:
            return "Missing required fields!", 400

        try:
            amount = float(amount)
        except ValueError:
            return "Invalid amount!", 400

        if add_transaction(username, 'Income', category, amount, date, remark):
            return redirect(url_for('dashboard'))
        else:
            return "Error adding transaction!", 500

    return render_template('add_income.html', user_theme=user_theme)

@app.route('/all_transactions')
def all_transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_theme = session.get('theme', 'light')

    username = session['user_id']
    sort_by = request.args.get('sort_by', 'date_desc')
    transactions = get_transactions(username, sort_by)

    return render_template(
        'all_transactions.html',
        username=username,
        transactions=transactions,
        sort_by=sort_by,
        user_theme=user_theme
    )

@app.route('/visualization')
def visualization():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    transactions = get_transactions(Email)

    from visualizations import (
        generate_monthly_expense_vs_income,
        generate_expense_breakdown_by_category,
        generate_expense_trend_over_time,
        generate_category_wise_spending_over_time,
        generate_income_vs_expense_distribution,
        generate_savings_over_time,
        generate_monthly_category_spending,
        generate_expense_vs_income_ratio,
        generate_weekly_spending_pattern,
        generate_word_cloud_for_expense_remarks
    )

    visualizations = {
        'monthly_expense_vs_income': generate_monthly_expense_vs_income(transactions),
        'expense_breakdown_by_category': generate_expense_breakdown_by_category(transactions),
        'expense_trend_over_time': generate_expense_trend_over_time(transactions),
        'category_wise_spending_over_time': generate_category_wise_spending_over_time(transactions),
        'income_vs_expense_distribution': generate_income_vs_expense_distribution(transactions),
        'savings_over_time': generate_savings_over_time(transactions),
        'monthly_category_spending': generate_monthly_category_spending(transactions),
        'expense_vs_income_ratio': generate_expense_vs_income_ratio(transactions),
        'weekly_spending_pattern': generate_weekly_spending_pattern(transactions),
        'word_cloud_for_expense_remarks': generate_word_cloud_for_expense_remarks(transactions)
    }

    user_theme = session.get('theme', 'light')

    return render_template('visualization.html', user_theme=user_theme, visualizations=visualizations)

@app.route('/get_expense_data')
def get_expense_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    transactions = get_transactions(Email)

    expense_data = {}
    for transaction in transactions:
        if transaction['type'] == 'Expense':
            category = transaction['category']
            amount = float(transaction['amount'])
            if category in expense_data:
                expense_data[category] += amount
            else:
                expense_data[category] = amount

    labels = list(expense_data.keys())
    values = list(expense_data.values())

    return jsonify({
        'labels': labels,
        'values': values
    })

@app.route('/get_balance_data')
def get_balance_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    transactions = get_transactions(Email)

    total_income = sum(t['amount'] for t in transactions if t.get('type') == 'Income')
    total_expense = sum(t['amount'] for t in transactions if t.get('type') == 'Expense')
    balance = total_income - total_expense

    return jsonify({
        'balance': balance
    })

@app.route('/download_transactions_pdf')
def download_transactions_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    transactions = get_transactions(Email)

    pdf_filename = generate_transactions_pdf(transactions, Email)

    return send_file(pdf_filename, as_attachment=True)

@app.route('/send_transactions_pdf')
def send_transactions_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    transactions = get_transactions(Email)

    pdf_filename = generate_transactions_pdf(transactions, Email)

    subject = "Your ExpenseFlow Transactions Report"
    body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .container { max-width: 600px; margin: auto; padding: 20px; }
            h2 { color: #2c3e50; }
            p { color: #555; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Your Transactions Report</h2>
            <p>Hi there,</p>
            <p>Please find your attached ExpenseFlow transactions report. If you have any questions, feel free to contact us.</p>
            <p>Best regards,<br><strong>The ExpenseFlow Team</strong></p>
        </div>
    </body>
    </html>
    """
    send_email(Email, subject, body, pdf_filename)

    os.remove(pdf_filename)

    flash("Transactions report sent to your email!", "success")
    return redirect(url_for('all_transactions'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')

    user = get_user(Email, old_password)
    if user:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE users SET password = %s WHERE Email = %s", (hashed_password, Email))
                connection.commit()
                cursor.close()
                connection.close()

                send_password_change_email(Email)

                flash("Password changed successfully!", "success")
                return redirect(url_for('dashboard'))
            except Error as e:
                return "Error updating password!", 500
    else:
        return "Invalid old password!", 400

    return redirect(url_for('dashboard'))

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    current_theme = get_user_theme(Email)
    new_theme = 'dark' if current_theme == 'light' else 'light'
    update_theme(Email, new_theme)
    session['theme'] = new_theme
    return '', 204

@app.route('/reset_dashboard', methods=['POST'])
def reset_dashboard():
    if 'user_id' not in session:
        flash("You must be logged in to reset your dashboard.", "error")
        return redirect(url_for('login'))

    Email = session['user_id']

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM transactions WHERE Email = %s", (Email,))
            connection.commit()
            cursor.close()
            connection.close()

            send_dashboard_reset_email(Email)

            flash("Dashboard reset successfully!", "success")
            return redirect(url_for('dashboard'))
        except Error as e:
            flash("An error occurred while resetting your dashboard.", "error")
            return redirect(url_for('dashboard'))
    else:
        flash("Database connection error.", "error")
        return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('theme', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)