#!/usr/bin/env python3
"""
Health & Nutrition Tracker - Setup Script
Helps with initial project setup and configuration
"""

import os
import sys
import subprocess
import mysql.connector
from mysql.connector import Error

def check_python_version():
    """Check if Python version is 3.10+"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]} (Compatible)")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    if not os.path.exists('.env.example'):
        print("❌ .env.example template not found")
        return False
    
    print("\n📝 Creating .env file...")
    
    # Get database credentials from user
    print("Please enter your MySQL database credentials:")
    db_host = input("Database Host (default: localhost): ").strip() or "localhost"
    db_user = input("Database User (default: root): ").strip() or "root"
    db_password = input("Database Password: ").strip()
    
    # Generate a secret key
    import secrets
    secret_key = secrets.token_hex(32)
    
    # Create .env file
    with open('.env.example', 'r') as template:
        content = template.read()
    
    content = content.replace('localhost', db_host)
    content = content.replace('root', db_user)
    content = content.replace('your_mysql_password', db_password)
    content = content.replace('your_secret_key_here', secret_key)
    
    with open('.env', 'w') as env_file:
        env_file.write(content)
    
    print("✅ .env file created successfully")
    return True

def test_database_connection():
    """Test MySQL database connection"""
    print("\n🔌 Testing database connection...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        if connection.is_connected():
            print("✅ Database connection successful")
            connection.close()
            return True
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_database():
    """Create the wellness_db database"""
    print("\n🗄️  Creating database...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS wellness_db")
        cursor.execute("USE wellness_db")
        
        # Execute create_tables.sql
        with open('create_tables.sql', 'r') as sql_file:
            sql_commands = sql_file.read().split(';')
            
        for command in sql_commands:
            if command.strip():
                cursor.execute(command)
        
        connection.commit()
        print("✅ Database and tables created successfully")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Database creation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ create_tables.sql file not found")
        return False

def check_csv_file():
    """Check if the CSV file exists"""
    csv_path = r'C:\Users\Admin\Downloads\Indian_Food_Nutrition_Processed1.csv'
    if os.path.exists(csv_path):
        print("✅ CSV file found")
        return True
    else:
        print(f"⚠️  CSV file not found at: {csv_path}")
        print("   Please download the Indian Food Nutrition dataset")
        print("   and place it at the specified location")
        return False

def main():
    """Main setup function"""
    print("🏥 Health & Nutrition Tracker - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create .env file
    if not create_env_file():
        return
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Setup failed at database connection")
        print("   Please check your MySQL installation and credentials")
        return
    
    # Create database and tables
    if not create_database():
        return
    
    # Check CSV file
    csv_exists = check_csv_file()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. If CSV file exists, run: python import_foods.py")
    print("2. Start the application: python run.py")
    print("3. Open browser to: http://localhost:5000")
    
    if not csv_exists:
        print("\n⚠️  Note: Food database will be empty until CSV is imported")

if __name__ == "__main__":
    main()