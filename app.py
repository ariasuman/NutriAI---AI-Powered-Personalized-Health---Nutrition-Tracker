#!/usr/bin/env python3
"""
AI-Based Personalized Health & Nutrition Tracker
Flask Web Application
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import mysql.connector
from mysql.connector import Error
import bcrypt
import os
from datetime import datetime, date, timedelta
import pandas as pd
from dotenv import load_dotenv
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.utils
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')

@app.context_processor
def inject_date():
    """Make date and timedelta available in all templates"""
    return {'date': date, 'timedelta': timedelta}

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'wellness_db')
}

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def calculate_bmr_tdee(weight, height, age, gender, activity_level):
    """Calculate BMR and TDEE using Mifflin-St Jeor equation"""
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725
    }
    
    tdee = bmr * activity_factors.get(activity_level, 1.2)
    return bmr, tdee

def calculate_health_score(user_id, week_start):
    """Calculate weekly health score (0-100)"""
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        cursor = connection.cursor(dictionary=True)
        week_end = week_start + timedelta(days=6)
        
        # Get user's TDEE for calorie accuracy
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return 0
        
        _, tdee = calculate_bmr_tdee(user['weight_kg'], user['height_cm'], 
                                   user['age'], user['gender'], user['activity_level'])
        
        # Get weekly logs
        cursor.execute("""
            SELECT date, SUM(calories_consumed) as daily_calories, 
                   AVG(water_liters) as daily_water, AVG(sleep_hours) as daily_sleep,
                   MAX(steps) as daily_steps
            FROM user_logs 
            WHERE user_id = %s AND date BETWEEN %s AND %s
            GROUP BY date
        """, (user_id, week_start, week_end))
        
        daily_logs = cursor.fetchall()
        
        if not daily_logs:
            return 0
        
        # Calculate scores
        calorie_score = 0
        water_score = 0
        sleep_score = 0
        workout_score = 0
        
        for log in daily_logs:
            # Calorie accuracy (40%)
            if log['daily_calories']:
                calorie_diff = abs(log['daily_calories'] - tdee) / tdee
                calorie_score += max(0, 100 - (calorie_diff * 100))
            
            # Water intake (20%) - target 2.5L
            if log['daily_water']:
                water_score += min(100, (log['daily_water'] / 2.5) * 100)
            
            # Sleep (20%) - target 7-9 hours
            if log['daily_sleep']:
                if 7 <= log['daily_sleep'] <= 9:
                    sleep_score += 100
                elif log['daily_sleep'] < 7:
                    sleep_score += max(0, (log['daily_sleep'] / 7) * 100)
                else:
                    sleep_score += max(0, 100 - ((log['daily_sleep'] - 9) * 10))
            
            # Workout consistency (20%) - target 8000+ steps
            if log['daily_steps'] and log['daily_steps'] >= 8000:
                workout_score += 100
        
        days_count = len(daily_logs)
        total_score = (
            (calorie_score / days_count) * 0.4 +
            (water_score / days_count) * 0.2 +
            (sleep_score / days_count) * 0.2 +
            (workout_score / days_count) * 0.2
        )
        
        return round(total_score, 1)
        
    except Error as e:
        print(f"Error calculating health score: {e}")
        return 0
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        age = int(request.form['age'])
        gender = request.form['gender']
        height_cm = float(request.form['height_cm'])
        weight_kg = float(request.form['weight_kg'])
        activity_level = request.form['activity_level']
        goal = request.form['goal']
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password, name, age, gender, height_cm, 
                                     weight_kg, activity_level, goal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (username, hashed_password, name, age, gender, height_cm, 
                      weight_kg, activity_level, goal))
                connection.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except Error as e:
                flash(f'Registration failed: {e}', 'error')
            finally:
                cursor.close()
                connection.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                
                if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['name'] = user['name']
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'error')
            except Error as e:
                flash(f'Login failed: {e}', 'error')
            finally:
                cursor.close()
                connection.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    connection = get_db_connection()
    
    if not connection:
        flash('Database connection error', 'error')
        return render_template('dashboard.html')
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Calculate BMR/TDEE
        bmr, tdee = calculate_bmr_tdee(user['weight_kg'], user['height_cm'], 
                                      user['age'], user['gender'], user['activity_level'])
        
        # Get today's logs
        today = date.today()
        cursor.execute("""
            SELECT SUM(calories_consumed) as calories, AVG(water_liters) as water,
                   AVG(sleep_hours) as sleep, MAX(steps) as steps
            FROM user_logs WHERE user_id = %s AND date = %s
        """, (user_id, today))
        today_stats = cursor.fetchone()
        
        # Get weekly data for charts
        week_start = today - timedelta(days=6)
        cursor.execute("""
            SELECT date, SUM(calories_consumed) as calories, AVG(water_liters) as water,
                   AVG(sleep_hours) as sleep
            FROM user_logs 
            WHERE user_id = %s AND date BETWEEN %s AND %s
            GROUP BY date ORDER BY date
        """, (user_id, week_start, today))
        weekly_data = cursor.fetchall()
        
        # Create charts
        charts = create_dashboard_charts(weekly_data, tdee)
        
        return render_template('dashboard.html', 
                             user=user, 
                             bmr=round(bmr), 
                             tdee=round(tdee),
                             today_stats=today_stats,
                             charts=charts)
        
    except Error as e:
        flash(f'Error loading dashboard: {e}', 'error')
        return render_template('dashboard.html')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_dashboard_charts(weekly_data, tdee):
    """Create dashboard charts"""
    if not weekly_data:
        return {}
    
    dates = [item['date'].strftime('%m/%d') for item in weekly_data]
    calories = [item['calories'] or 0 for item in weekly_data]
    water = [item['water'] or 0 for item in weekly_data]
    sleep = [item['sleep'] or 0 for item in weekly_data]
    
    charts = {}
    
    # Calories chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, calories, marker='o', label='Consumed')
    ax.axhline(y=tdee, color='r', linestyle='--', label='Target')
    ax.set_title('Weekly Calories')
    ax.set_ylabel('Calories')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    charts['calories'] = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    # Water chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(dates, water, alpha=0.7)
    ax.axhline(y=2.5, color='r', linestyle='--', label='Target (2.5L)')
    ax.set_title('Weekly Water Intake')
    ax.set_ylabel('Liters')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    charts['water'] = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return charts

# Import additional routes
from routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)