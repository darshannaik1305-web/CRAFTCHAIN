#!/usr/bin/env python3
"""
Clean Database Creator for CraftChain
Creates a fresh database with optimal SQLite settings
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

def create_clean_database():
    """Create a completely fresh database with optimal settings."""
    print("Creating clean CraftChain database...")
    
    # Get paths
    project_dir = os.path.dirname(__file__)
    db_path = os.path.join(project_dir, 'app.db')
    
    # Remove any existing database files
    for suffix in ['', '-wal', '-shm', '-journal']:
        file_path = db_path + suffix
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Could not remove {file_path}: {e}")
    
    # Wait for file system
    import time
    time.sleep(1)
    
    # Create new database with optimal settings
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Set optimal SQLite settings
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        
        conn.commit()
        conn.close()
        
        print("Database created with optimal settings!")
        
        # Now create the tables using Flask app
        sys.path.insert(0, os.path.join(project_dir, 'backend'))
        
        # Import here to avoid path issues
        from app import app, db, ensure_category_column
        
        with app.app_context():
            db.create_all()
            ensure_category_column()
            print("Database tables created successfully!")
            
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def main():
    """Main function."""
    print("CraftChain Clean Database Creator")
    print("=" * 40)
    
    if create_clean_database():
        print("\nDatabase created successfully!")
        print("You can now start the CraftChain service.")
    else:
        print("\nFailed to create database!")
        print("Please check the error messages above.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
