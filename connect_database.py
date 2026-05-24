import psycopg2

# Database Credentials
DB_USER = "postgres"
DB_PASSWORD = "your_password_here"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "company_ai"

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )

    print(" Database Connected Successfully!")

    conn.close()

except Exception as e:
    print(" Connection Failed")
    print("Error:", e)