from database import create_connection

conn = create_connection()
if conn:
    print("Database connected successfully!")
else:
    print("Failed to connect to database.")
