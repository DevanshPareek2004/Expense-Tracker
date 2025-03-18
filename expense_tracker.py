from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file,jsonify
from database import initialize_database, add_user, get_user, add_transaction, get_transactions, Error, create_connection, update_currency, get_user_currency, get_user_theme, update_theme
import bcrypt
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from smtp_handler import send_email, generate_otp, send_welcome_email, send_password_change_email, send_dashboard_reset_email, send_otp_email, generate_transactions_pdf
import re
import os

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

def get_transactions(Email, sort_by='date_desc'):
    connection = create_connection()
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
            print(f"Error resetting monthly transactions: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=reset_monthly_transactions, trigger='cron', month='*', day=1)
scheduler.start()

app = Flask(__name__)
app.secret_key = "your_secret_key"

initialize_database()

@app.route('/')
def home():
    user_theme = session.get('theme', 'light')  # Default to light theme
    return render_template('index.html', user_theme=user_theme)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        Email = request.form['Email'].strip()
        password = request.form['password'].strip()

        user = get_user(Email, password)
        if user:
            session['user_id'] = Email  # Set the user's email in the session
            session['theme'] = get_user_theme(Email)  # Set the user's theme preference
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
    user_theme = session.get('theme', 'light')  # Default to light theme

    if request.method == 'POST':
        email = request.form.get('Email').strip()  # Get the email from the form

        # Check if the email exists in the database
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
                user = cursor.fetchone()
                cursor.close()
                connection.close()

                if user:
                    # Send OTP email
                    email_sent, otp = send_otp_email(email)  # Call the OTP function
                    if email_sent:
                        # Store OTP, email, and current time in session
                        session['otp'] = otp
                        session['otp_email'] = email  # Set otp_email in the session
                        session['otp_time'] = datetime.now().isoformat()  # Store the current time
                        return redirect(url_for('enter_otp'))  # Redirect to OTP page
                    else:
                        flash("Error sending OTP. Please try again.", "error")
                        return redirect(url_for('forgot_password'))
                else:
                    flash("Email not found. Please check your email address.", "error")
                    return redirect(url_for('forgot_password'))
            except Error as e:
                print(f"Error checking email: {e}")
                flash("An error occurred. Please try again.", "error")
                return redirect(url_for('forgot_password'))
        else:
            flash("Database connection error. Please try again.", "error")
            return redirect(url_for('forgot_password'))

    # Render the forgot password form for GET requests
    return render_template('forgot_password.html', user_theme=user_theme)

@app.route('/enter_otp', methods=['GET', 'POST'])
def enter_otp():
    user_theme = session.get('theme', 'light')  # Default to light theme

    if request.method == 'POST':
        user_otp = request.form.get('otp')  # Get the OTP entered by the user

        # Ensure session variables exist
        if 'otp' not in session or 'otp_time' not in session or 'otp_email' not in session:
            flash("Session expired. Please request a new OTP.", "error")
            return redirect(url_for('forgot_password'))

        # Convert session['otp_time'] to datetime if stored as a string
        otp_time = session['otp_time']
        if isinstance(otp_time, str):
            otp_time = datetime.fromisoformat(otp_time)

        # Ensure otp_time is timezone-naive
        if otp_time.tzinfo is not None:  # Check if otp_time is timezone-aware
            otp_time = otp_time.replace(tzinfo=None)  # Make it timezone-naive

        # Get the current time (timezone-naive)
        current_time = datetime.now()

        # Check if OTP is valid and not expired
        if str(session['otp']) == user_otp:
            if current_time - otp_time < timedelta(minutes=5):  # OTP is valid for 5 minutes
                # Set otp_email in the session for reset_password route
                session['otp_email'] = session.get('otp_email')  # Ensure otp_email is set
                return redirect(url_for('reset_password'))  # Redirect to reset password page
            else:
                flash("OTP expired. Please request a new one.", "error")
                return redirect(url_for('forgot_password'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('enter_otp'))

    # Render the OTP form for GET requests
    return render_template('enter_otp.html', user_theme=user_theme)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    user_theme = session.get('theme', 'light')  # Default to light theme

    # Check if the user is authorized (OTP verified)
    if 'otp_email' not in session:
        flash("Unauthorized access. Please request a new OTP.", "error")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')  # Get the new password

        # Validate the new password
        if not new_password:
            flash("New password is required.", "error")
            return redirect(url_for('reset_password'))

        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        # Update the password in the database
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE users SET password = %s WHERE Email = %s", (hashed_password, session['otp_email']))
                connection.commit()
                cursor.close()
                connection.close()

                # Send email to the user about the password change
                send_password_change_email(session['otp_email'])

                # Clear session variables
                session.pop('otp', None)
                session.pop('otp_email', None)
                session.pop('otp_time', None)

                flash("Password changed successfully!", "success")
                return redirect(url_for('home'))
            except Error as e:
                print(f"Error updating password: {e}")
                flash("An error occurred. Please try again.", "error")
                return redirect(url_for('reset_password'))
        else:
            flash("Database connection error. Please try again.", "error")
            return redirect(url_for('reset_password'))

    # Render the reset password form for GET requests
    return render_template('reset_password.html', user_theme=user_theme)

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('register'))

    # Get the user's email from the session
    Email = session['user_id']

    # Get the date filter from the request (default to 'all')
    date_filter = request.args.get('date_filter', 'all')

    # Get the user's theme preference from the session
    user_theme = session.get('theme', 'light')

    # Get the user's currency preference from the database
    user_currency = get_user_currency(Email)

    # Fetch transactions based on the date filter
    today = datetime.today()
    start_date = None
    end_date = None

    if date_filter == 'today':
        start_date = today
        end_date = today
    elif date_filter == 'week':
        start_date = today - timedelta(days=today.weekday())  # Start of the week
        end_date = start_date + timedelta(days=6)  # End of the week
    elif date_filter == 'month':
        start_date = today.replace(day=1)  # Start of the month
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)  # End of the month
    elif date_filter == 'last_month':
        start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)  # Start of last month
        end_date = today.replace(day=1) - timedelta(days=1)  # End of last month
    elif date_filter == 'year':
        start_date = today.replace(month=1, day=1)  # Start of the year
        end_date = today.replace(month=12, day=31)  # End of the year

    # Fetch transactions based on the date range (if applicable)
    if start_date and end_date:
        transactions = get_transactions_by_date(Email, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    else:
        transactions = get_transactions(Email)

    # Calculate totals for income, expense, and balance
    total_income = sum(t['amount'] for t in transactions if t.get('type') == 'Income')
    total_expense = sum(t['amount'] for t in transactions if t.get('type') == 'Expense')
    balance = total_income - total_expense

    # Get the last 10 transactions for the "Recent Transactions" section
    last_10_transactions = transactions[:10]

    # Render the dashboard template with all the required data
    return render_template(
        'dashboard.html',
        Email=Email,
        balance=balance,
        income=total_income,
        expense=total_expense,
        transactions=last_10_transactions,
        date_filter=date_filter,
        user_currency=user_currency,
        user_theme=user_theme  # Pass the user's theme preference to the template
    )

@app.route('/toggle_menu')
def toggle_menu():
    session['menu_open'] = not session.get('menu_open', False)
    return redirect(url_for('dashboard'))

@app.route('/change_currency', methods=['POST'])
def change_currency():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    new_currency = request.form.get('currency')  # Get selected currency from form
    update_currency(Email, new_currency)  # Update database
    session['currency'] = new_currency  # Store in session
    flash("Currency updated successfully!", "success")
    return redirect(url_for('dashboard'))  # Redirect to dashboard

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_theme = session.get('theme', 'light')  # Default to light theme

    if request.method == 'POST':
        username = session['user_id']
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')
        remark = request.form.get('remark')  # Get remark from form

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

    user_theme = session.get('theme', 'light')  # Default to light theme

    if request.method == 'POST':
        username = session['user_id']
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')
        remark = request.form.get('remark')  # Get remark from form

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

    user_theme = session.get('theme', 'light')  # Default to light theme

    username = session['user_id']
    sort_by = request.args.get('sort_by', 'date_desc')  # Default sorting by date (newest first)
    transactions = get_transactions(username, sort_by)  # Fetch all transactions

    return render_template(
        'all_transactions.html',
        username=username,
        transactions=transactions,
        sort_by=sort_by,  # Pass sort_by to template
        user_theme=user_theme
    )

@app.route('/visualization')
def visualization():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    transactions = get_transactions(Email)
    
    # Debug: Print the transactions data
    print("Transactions Data:")
    print(transactions)

    # Generate all visualizations
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

    # Generate visualizations
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

    # Get the user's theme preference
    user_theme = session.get('theme', 'light')

    # Render the visualization template with the generated visualizations and user theme
    return render_template('visualization.html', user_theme=user_theme, visualizations=visualizations)

@app.route('/get_expense_data')
def get_expense_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    transactions = get_transactions(Email)

    # Group expenses by category
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

    # Calculate total income and expenses
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

    # Generate the PDF
    pdf_filename = generate_transactions_pdf(transactions, Email)

    # Send the PDF as a download
    return send_file(pdf_filename, as_attachment=True)

@app.route('/send_transactions_pdf')
def send_transactions_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    transactions = get_transactions(Email)

    # Generate the PDF
    pdf_filename = generate_transactions_pdf(transactions, Email)

    # Send the PDF via email
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

    # Clean up the PDF file
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

                # Send email to user about password change
                send_password_change_email(Email)

                flash("Password changed successfully!", "success")
                return redirect(url_for('dashboard'))
            except Error as e:
                print(f"Error updating password: {e}")
                return "Error updating password!", 500
    else:
        return "Invalid old password!", 400

    return redirect(url_for('dashboard'))

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    Email = session['user_id']
    current_theme = get_user_theme(Email)  # Get the current theme from the database
    new_theme = 'dark' if current_theme == 'light' else 'light'  # Toggle the theme
    update_theme(Email, new_theme)  # Update the theme in the database
    session['theme'] = new_theme  # Update the session with the new theme
    return '', 204  # Return an empty response with status code 204 (No Content)

@app.route('/reset_dashboard', methods=['POST'])
def reset_dashboard():
    # Check if the user is logged in (session should contain 'user_id')
    if 'user_id' not in session:
        flash("You must be logged in to reset your dashboard.", "error")
        return redirect(url_for('login'))

    # Get the user's email from the session
    Email = session['user_id']

    # Delete all transactions for the user
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM transactions WHERE Email = %s", (Email,))
            connection.commit()
            cursor.close()
            connection.close()

            # Send email to the user about the dashboard reset
            send_dashboard_reset_email(Email)

            flash("Dashboard reset successfully!", "success")
            return redirect(url_for('dashboard'))
        except Error as e:
            print(f"Error resetting dashboard: {e}")
            flash("An error occurred while resetting your dashboard.", "error")
            return redirect(url_for('dashboard'))
    else:
        flash("Database connection error.", "error")
        return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('theme', None)  # Clear theme preference on logout
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)