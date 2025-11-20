#!/usr/bin/env python3
"""
Simple database fix script
"""
import os
import sys
import sqlite3
from datetime import datetime

def main():
    print("Creating fresh database...")
    
    # Add backend to path
    backend_path = os.path.join(os.getcwd(), 'backend')
    sys.path.insert(0, backend_path)
    
    # Create timestamped database in temp folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_db_path = os.path.join(os.environ.get('TEMP', '.'), f'craftchain_{timestamp}.db')
    
    print(f"New database: {new_db_path}")
    
    try:
        # Create database with optimal settings
        conn = sqlite3.connect(new_db_path)
        cursor = conn.cursor()
        
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA busy_timeout=30000')
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.execute('PRAGMA cache_size=10000')
        cursor.execute('PRAGMA temp_store=MEMORY')
        conn.commit()
        conn.close()
        
        print("Database file created successfully")
        
        # Import Flask app and create tables
        from app import app, db, ensure_category_column
        
        # Configure app to use new database
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{new_db_path}'
        
        with app.app_context():
            db.create_all()
            ensure_category_column()
        
        print("Database tables created successfully")
        
        # Save the path
        with open('database_path.txt', 'w') as f:
            f.write(new_db_path)
        
        print("Database path saved to database_path.txt")
        print("SUCCESS: Database created and configured!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("Press Enter to exit...")
        sys.exit(1)
    else:
        print("Database fix completed successfully!")
