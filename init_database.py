"""Database Setup Script

This script initializes the PostgreSQL database with all required schemas and tables.
Run this once after setting up PostgreSQL.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'kunalranjan')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = 'edtech_mvp'

def create_database():
    """Create the main database if it doesn't exist"""
    try:
        # Connect to PostgreSQL default database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        if cursor.fetchone():
            print(f"✅ Database '{DB_NAME}' already exists")
        else:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"✅ Database '{DB_NAME}' created")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True


def create_schemas():
    """Create the three main schemas"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        schemas = ['users', 'curriculum', 'analytics']
        
        for schema in schemas:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            print(f"✅ Schema '{schema}' created/verified")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating schemas: {e}")
        return False
    
    return True


def create_tables():
    """Create all tables using SQLAlchemy"""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from database import init_db
        
        init_db()
        print("✅ All tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def main():
    """Run complete database setup"""
    print("=" * 60)
    print("📊 EdTech MVP Database Setup")
    print("=" * 60)
    print()
    
    steps = [
        ("Creating database...", create_database),
        ("Creating schemas...", create_schemas),
        ("Creating tables...", create_tables),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}")
        print("-" * 40)
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ Database setup completed successfully!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Seed initial curriculum data: python init_curriculum.py")
    print("   2. Run the backend: source venv/bin/activate && python app_refactored.py")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
