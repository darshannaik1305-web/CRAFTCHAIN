#!/usr/bin/env python3
"""
Force Database Fix Script for CraftChain
This script forcefully fixes database locking issues by recreating the database.
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
import time

def force_unlock_database():
    """Forcefully unlock the database by removing WAL and SHM files."""
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    wal_path = db_path + '-wal'
    shm_path = db_path + '-shm'
    
    print("Force unlocking database...")
    
    # Remove WAL and SHM files that might be causing locks
    for file_path in [wal_path, shm_path]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Could not remove {file_path}: {e}")
    
    # Try to open and close the database to clear any remaining locks
    try:
        conn = sqlite3.connect(db_path, timeout=1.0)
        conn.execute("SELECT 1")
        conn.close()
        print("Database unlocked successfully!")
        return True
    except Exception as e:
        print(f"Database still locked: {e}")
        return False

def recreate_database():
    """Recreate the database from scratch."""
    print("Recreating database from scratch...")
    
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Backup existing database if possible
    if os.path.exists(db_path):
        try:
            shutil.copy2(db_path, backup_path)
            print(f"Backup created: {backup_path}")
        except Exception as e:
            print(f"Could not backup database: {e}")
    
    # Remove all database files
    for suffix in ['', '-wal', '-shm']:
        file_path = db_path + suffix
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Could not remove {file_path}: {e}")
    
    # Wait a moment for file system to catch up
    time.sleep(2)
    
    # Create new database
    try:
        # Add the backend directory to the path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        from app import app, db, ensure_category_column
        
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Ensure category column exists
            ensure_category_column()
            
            print("Database recreated successfully!")
            return True
            
    except Exception as e:
        print(f"Error recreating database: {e}")
        return False

def main():
    """Main function to force fix database issues."""
    print("CraftChain Force Database Fix Tool")
    print("=" * 50)
    
    # First try to unlock
    if force_unlock_database():
        print("Database unlocked! You can now restart the service.")
        return True
    
    # If unlock fails, recreate the database
    print("\nUnlock failed. Recreating database...")
    if recreate_database():
        print("\nDatabase recreated successfully!")
        print("You can now restart the CraftChain service.")
        return True
    else:
        print("\nFailed to recreate database. Please check for errors above.")
        return False

if __name__ == "__main__":
    main()
    input("\nPress Enter to continue...")
