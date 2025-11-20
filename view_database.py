#!/usr/bin/env python3
"""
Database Viewer for CraftChain
Allows viewing database contents and structure
"""

import os
import sys
import sqlite3
from datetime import datetime

def get_database_path():
    """Get the correct database path."""
    project_dir = os.path.dirname(__file__)
    
    # Check if there's a custom database path
    custom_db_path = os.path.join(project_dir, 'database_path.txt')
    if os.path.exists(custom_db_path):
        try:
            with open(custom_db_path, 'r') as f:
                return f.read().strip()
        except Exception:
            pass
    
    # Default path
    return os.path.join(project_dir, 'app.db')

def view_database():
    """View database contents."""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("CRAFTCHAIN DATABASE VIEWER")
        print(f"Database: {db_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in database.")
            return
        
        for table_name, in tables:
            print(f"\n{'=' * 40}")
            print(f"TABLE: {table_name.upper()}")
            print(f"{'=' * 40}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("COLUMNS:")
            for col in columns:
                col_id, name, col_type, not_null, default, pk = col
                print(f"  - {name} ({col_type}) {'[PK]' if pk else ''} {'[NOT NULL]' if not_null else ''}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"\nTOTAL ROWS: {row_count}")
            
            if row_count > 0:
                print(f"\nDATA (showing first 10 rows):")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
                rows = cursor.fetchall()
                
                # Print header
                col_names = [col[1] for col in columns]
                print(" | ".join(f"{name:15}" for name in col_names))
                print("-" * (len(col_names) * 18))
                
                # Print data
                for row in rows:
                    print(" | ".join(f"{str(val)[:15]:15}" for val in row))
                
                if row_count > 10:
                    print(f"\n... and {row_count - 10} more rows")
        
        print(f"\n{'=' * 60}")
        print("DATABASE SUMMARY")
        print(f"{'=' * 60}")
        
        # Summary statistics
        for table_name, in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} records")
        
        conn.close()
        
    except Exception as e:
        print(f"Error viewing database: {e}")

def main():
    """Main function."""
    view_database()
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
