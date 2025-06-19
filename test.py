from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()

# Get the connection string
DATABASE_URL = os.getenv("DATABASE_URL")
# DATABASE_URL = "mssql+pyodbc://5909:L0g!n@5909@10.0.0.8/peoplechat_agentic_rag_db?driver=ODBC+Driver+17+for+SQL+Server"
print(f"Using DATABASE_URL: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")