# CraftChain Database Fix Instructions

## Problem
You're experiencing database locking errors when trying to add products, register users, or login. This happens when multiple processes try to access the SQLite database simultaneously.

## Solution Steps

### Step 1: Stop the CraftChain Service
1. Right-click on the CraftChain system tray icon (if visible)
2. Select "Stop Server" from the menu
3. OR run this command in Command Prompt:
   ```
   taskkill /F /IM python.exe
   ```

### Step 2: Fix the Database
1. Open Command Prompt as Administrator
2. Navigate to your project folder:
   ```
   cd "C:\Users\darsh\OneDrive\Desktop\CRAFTCHAIN"
   ```
3. Run the database fix script:
   ```
   python fix_database.py
   ```

### Step 3: Restart the Service
1. Double-click `Start-Service.bat` to restart the CraftChain service
2. OR run:
   ```
   restart_service.bat
   ```

## What Was Fixed

1. **Enhanced Database Configuration**: Added better SQLite settings for concurrency
2. **Retry Logic**: Added automatic retry with exponential backoff for database operations
3. **WAL Mode**: Enabled Write-Ahead Logging for better concurrent access
4. **Timeout Settings**: Increased database timeout to 30 seconds

## Files Modified

- `backend/app.py`: Enhanced database configuration and retry logic
- `fix_database.py`: Database repair script
- `restart_service.bat`: Service restart script

## Testing

After following these steps:
1. Try registering a new user
2. Try logging in
3. Try adding a product as a seller

All operations should now work without database locking errors.

## If Problems Persist

If you still see database errors:
1. Make sure no other instances of the app are running
2. Check Windows Task Manager for multiple python.exe processes
3. Restart your computer to clear all locks
4. Run the fix script again

## Prevention

To prevent future database locks:
- Always use the system tray icon to stop the service properly
- Don't run multiple instances of the Flask app
- The enhanced code now handles most locking scenarios automatically
