import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from io import BytesIO
import base64
from wordcloud import WordCloud

def generate_monthly_expense_vs_income(transactions):
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    monthly_data = df.groupby(['month', 'type']).sum(numeric_only=True).unstack().fillna(0)
    
    plt.figure(figsize=(6, 3))
    monthly_data.plot(kind='bar', stacked=True)
    plt.title('Monthly Expense vs. Income')
    plt.xlabel('Month')
    plt.ylabel('Amount')
    plt.legend(['Expense', 'Income'])
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_expense_breakdown_by_category(transactions):
    df = pd.DataFrame(transactions)
    expense_data = df[df['type'] == 'Expense']
    category_data = expense_data.groupby('category')['amount'].sum().reset_index()
    
    plt.figure(figsize=(5, 5))
    plt.pie(category_data['amount'], labels=category_data['category'], autopct='%1.1f%%')
    plt.title('Expense Breakdown by Category')
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_expense_trend_over_time(transactions):
    df = pd.DataFrame(transactions)
    expense_data = df[df['type'] == 'Expense']
    
    if 'amount' not in expense_data.columns:
        raise ValueError("The 'amount' column is missing in the expense data.")
    
    plt.figure(figsize=(6, 3)) 
    sns.lineplot(data=expense_data, x='date', y='amount')
    plt.title('Expense Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_category_wise_spending_over_time(transactions):
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    expense_data = df[df['type'] == 'Expense']
    category_data = expense_data.groupby(['date', 'category']).sum(numeric_only=True).unstack().fillna(0)
    
    plt.figure(figsize=(6, 3))
    category_data.plot(kind='area', stacked=True)
    plt.title('Category-wise Spending Over Time')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_income_vs_expense_distribution(transactions):
    df = pd.DataFrame(transactions)
    income_data = df[df['type'] == 'Income']['amount']
    expense_data = df[df['type'] == 'Expense']['amount']
    
    plt.figure(figsize=(6, 3))
    sns.histplot(income_data, color='green', label='Income', kde=True)
    sns.histplot(expense_data, color='red', label='Expense', kde=True)
    plt.title('Income vs. Expense Distribution')
    plt.xlabel('Amount')
    plt.ylabel('Frequency')
    plt.legend()
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_savings_over_time(transactions):
    df = pd.DataFrame(transactions)
    income_data = df[df['type'] == 'Income']
    expense_data = df[df['type'] == 'Expense']
    income_by_date = income_data.groupby('date')['amount'].sum()
    expense_by_date = expense_data.groupby('date')['amount'].sum()
    savings_data = income_by_date - expense_by_date
    savings_data = savings_data.reset_index()
    savings_data.columns = ['date', 'amount']
    
    plt.figure(figsize=(6, 3))
    sns.lineplot(data=savings_data, x='date', y='amount')
    plt.title('Savings Over Time')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_monthly_category_spending(transactions):
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    expense_data = df[df['type'] == 'Expense']
    category_data = expense_data.groupby(['month', 'category']).sum(numeric_only=True).unstack()
    
    plt.figure(figsize=(6, 3))
    category_data.plot(kind='bar', stacked=False)
    plt.title('Monthly Category Spending')
    plt.xlabel('Month')
    plt.ylabel('Amount')
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_expense_vs_income_ratio(transactions):
    df = pd.DataFrame(transactions)
    total_income = df[df['type'] == 'Income']['amount'].sum()
    total_expense = df[df['type'] == 'Expense']['amount'].sum()
    ratio = total_expense / total_income if total_income != 0 else 0
    
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_title('Expense vs. Income Ratio')
    ax.set_ylim(0, 1)
    ax.barh(0, ratio, color='red' if ratio > 0.5 else 'green')
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(0.5, 0.1, f'{ratio:.2f}', ha='center', va='center', fontsize=20)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_weekly_spending_pattern(transactions):
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    df['week'] = df['date'].dt.isocalendar().week
    expense_data = df[df['type'] == 'Expense']
    weekly_data = expense_data.groupby(['week', 'day_of_week']).sum(numeric_only=True).unstack()
    
    plt.figure(figsize=(6, 3))
    sns.heatmap(weekly_data, cmap='YlOrRd')
    plt.title('Weekly Spending Pattern')
    plt.xlabel('Day of Week')
    plt.ylabel('Week')
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_word_cloud_for_expense_remarks(transactions):
    df = pd.DataFrame(transactions)
    remarks = ' '.join(df[df['type'] == 'Expense']['remark'].dropna())
    
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(remarks)
    plt.figure(figsize=(6, 3))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud for Expense Remarks')
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

