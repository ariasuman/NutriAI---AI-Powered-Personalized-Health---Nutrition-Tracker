#!/usr/bin/env python3
"""
Food CSV Importer for Wellness DB
Imports Indian food nutrition data from CSV to MySQL database
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': 'wellness_db'
}

CSV_PATH = r'C:\Users\Admin\Downloads\Indian_Food_Nutrition_Processed1.csv'

def clean_numeric_value(value):
    """Clean and convert numeric values"""
    if pd.isna(value) or value == '' or value == 'N/A':
        return 0.0
    try:
        # Remove any non-numeric characters except decimal point
        cleaned = str(value).strip().replace(',', '')
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0

def import_foods():
    """Import food data from CSV to MySQL database"""
    connection = None
    try:
        # Read CSV with Latin-1 encoding
        print(f"Reading CSV file: {CSV_PATH}")
        df = pd.read_csv(CSV_PATH, encoding='latin-1')
        
        # Remove BOM if present
        if df.columns[0].startswith('\ufeff'):
            df.columns = [col.replace('\ufeff', '') for col in df.columns]
        
        print(f"Loaded {len(df)} records from CSV")
        print(f"Columns: {list(df.columns)}")
        
        # Clean column names (remove spaces, convert to lowercase)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Map CSV columns to database columns
        column_mapping = {
            'dish_name': 'dish_name',
            'food_name': 'dish_name',
            'name': 'dish_name',
            'calories': 'calories',
            'carbohydrates': 'carbohydrates',
            'carbs': 'carbohydrates',
            'protein': 'protein',
            'fats': 'fats',
            'fat': 'fats',
            'free_sugar': 'free_sugar',
            'sugar': 'free_sugar',
            'fibre': 'fibre',
            'fiber': 'fibre',
            'sodium': 'sodium',
            'calcium': 'calcium',
            'iron': 'iron',
            'vitamin_c': 'vitamin_c',
            'folate': 'folate'
        }
        
        # Rename columns based on mapping
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Ensure required columns exist
        required_columns = ['dish_name', 'calories', 'carbohydrates', 'protein', 'fats', 
                          'free_sugar', 'fibre', 'sodium', 'calcium', 'iron', 'vitamin_c', 'folate']
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0.0
        
        # Clean numeric columns
        numeric_columns = ['calories', 'carbohydrates', 'protein', 'fats', 'free_sugar', 
                          'fibre', 'sodium', 'calcium', 'iron', 'vitamin_c', 'folate']
        
        for col in numeric_columns:
            df[col] = df[col].apply(clean_numeric_value)
        
        # Clean dish names
        df['dish_name'] = df['dish_name'].astype(str).str.strip()
        df = df[df['dish_name'] != '']  # Remove empty dish names
        df = df.drop_duplicates(subset=['dish_name'])  # Remove duplicates
        
        # Connect to MySQL
        print("Connecting to MySQL database...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Clear existing food items
        cursor.execute("DELETE FROM food_items")
        print("Cleared existing food items")
        
        # Insert food items
        insert_query = """
        INSERT INTO food_items (dish_name, calories, carbohydrates, protein, fats, 
                               free_sugar, fibre, sodium, calcium, iron, vitamin_c, folate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        records_inserted = 0
        for _, row in df.iterrows():
            try:
                values = (
                    row['dish_name'],
                    row['calories'],
                    row['carbohydrates'],
                    row['protein'],
                    row['fats'],
                    row['free_sugar'],
                    row['fibre'],
                    row['sodium'],
                    row['calcium'],
                    row['iron'],
                    row['vitamin_c'],
                    row['folate']
                )
                cursor.execute(insert_query, values)
                records_inserted += 1
            except Exception as e:
                print(f"Error inserting row: {row['dish_name']} - {e}")
        
        connection.commit()
        print(f"Successfully imported {records_inserted} food items to database")
        
        # Verify import
        cursor.execute("SELECT COUNT(*) FROM food_items")
        count = cursor.fetchone()[0]
        print(f"Total food items in database: {count}")
        
    except FileNotFoundError:
        print(f"Error: CSV file not found at {CSV_PATH}")
        print("Please ensure the file exists and the path is correct")
    except Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    import_foods()