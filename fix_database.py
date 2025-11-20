#!/usr/bin/env python3
"""
Database Fix Script for CraftChain
This script fixes database locking issues and reinitializes the database if needed.
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def backup_database(db_path):
    """Create a backup of the current database."""
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
        return backup_path
    return None

def fix_database_locks(db_path):
    """Fix database locking issues by optimizing SQLite settings."""
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist.")
        return False
    
    try:
        # Connect directly to SQLite and fix settings with longer timeout
        conn = sqlite3.connect(db_path, timeout=60.0)
        cursor = conn.cursor()
        
        # Try to acquire an exclusive lock first
        cursor.execute("BEGIN EXCLUSIVE")
        
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Set busy timeout
        cursor.execute("PRAGMA busy_timeout=30000")
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        
        # Optimize performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        
        # Commit the transaction
        conn.commit()
        
        # Try to vacuum in a separate transaction
        try:
            cursor.execute("VACUUM")
            print("Database vacuum completed.")
        except Exception as vacuum_error:
            print(f"Vacuum failed (this is often okay): {vacuum_error}")
        
        conn.close()
        
        print("Database optimization completed successfully!")
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("Database is currently locked by another process.")
            print("Please stop the CraftChain service first, then run this script again.")
            return False
        else:
            print(f"SQLite error: {e}")
            return False
    except Exception as e:
        print(f"Error fixing database: {e}")
        return False

def reinitialize_database():
    """Reinitialize the database using Flask app context."""
    try:
        from app import app, db, ensure_category_column
        
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Ensure category column exists
            ensure_category_column()
            
            print("Database reinitialized successfully!")
            return True
            
    except Exception as e:
        print(f"Error reinitializing database: {e}")
        return False

def main():
    """Main function to fix database issues."""
    print("CraftChain Database Fix Tool")
    print("=" * 40)
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    
    # Create backup
    backup_path = backup_database(db_path)
    
    # Try to fix database locks
    if fix_database_locks(db_path):
        print("Database locks fixed successfully!")
    else:
        print("Failed to fix database locks. Reinitializing...")
        
        # Remove corrupted database
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Reinitialize database
        if reinitialize_database():
            print("Database reinitialized successfully!")
        else:
            print("Failed to reinitialize database!")
            return False
    
    print("\nDatabase fix completed!")
    print("You can now restart the CraftChain service.")
    return True

if __name__ == "__main__":
    main()
