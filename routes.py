"""
Additional routes for the Health & Nutrition Tracker
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify, send_file
from app import app, get_db_connection, calculate_bmr_tdee, calculate_health_score
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date, timedelta
import calendar
import pandas as pd
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
import random

@app.route('/meal_plan')
def meal_plan():
    """Generate personalized meal plan"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    connection = get_db_connection()
    
    if not connection:
        flash('Database connection error', 'error')
        return render_template('meal_plan.html')
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Calculate TDEE
        _, tdee = calculate_bmr_tdee(user['weight_kg'], user['height_cm'], 
                                   user['age'], user['gender'], user['activity_level'])
        
        # Adjust calories based on goal
        if user['goal'] == 'lose':
            target_calories = tdee - 500  # 500 calorie deficit
        elif user['goal'] == 'gain':
            target_calories = tdee + 500  # 500 calorie surplus
        else:
            target_calories = tdee
        
        # Meal distribution: Breakfast 25%, Lunch 30%, Dinner 25%, Snacks 20%
        meal_targets = {
            'breakfast': target_calories * 0.25,
            'lunch': target_calories * 0.30,
            'dinner': target_calories * 0.25,
            'snack': target_calories * 0.20
        }
        
        # Get food items
        cursor.execute("""
            SELECT * FROM food_items 
            WHERE calories > 0 
            ORDER BY RAND() 
            LIMIT 100
        """)
        foods = cursor.fetchall()
        
        # Generate meal plan
        meal_plan = generate_meal_combinations(foods, meal_targets, user['goal'])
        
        return render_template('meal_plan.html', 
                             meal_plan=meal_plan, 
                             target_calories=round(target_calories),
                             user=user)
        
    except Error as e:
        flash(f'Error generating meal plan: {e}', 'error')
        return render_template('meal_plan.html')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_meal_combinations(foods, meal_targets, goal):
    """Generate optimal meal combinations"""
    meal_plan = {}
    
    for meal_type, target_calories in meal_targets.items():
        best_combination = []
        best_score = float('inf')
        
        # Try multiple random combinations
        for _ in range(50):
            combination = []
            total_calories = 0
            total_protein = 0
            
            # Select 1-3 foods for the meal
            num_foods = random.randint(1, 3)
            selected_foods = random.sample(foods, min(num_foods, len(foods)))
            
            for food in selected_foods:
                # Calculate portion to fit target
                if food['calories'] > 0:
                    portion = min(2.0, target_calories / (food['calories'] * num_foods))
                    combination.append({
                        'food': food,
                        'portion': round(portion, 2),
                        'calories': food['calories'] * portion,
                        'protein': food['protein'] * portion
                    })
                    total_calories += food['calories'] * portion
                    total_protein += food['protein'] * portion
            
            # Score combination (prefer high protein for weight loss)
            calorie_diff = abs(total_calories - target_calories)
            protein_bonus = total_protein * (2 if goal == 'lose' else 1)
            score = calorie_diff - protein_bonus
            
            if score < best_score and total_calories > 0:
                best_score = score
                best_combination = combination
        
        meal_plan[meal_type] = best_combination
    
    return meal_plan

@app.route('/log_food', methods=['GET', 'POST'])
def log_food():
    """Log daily food intake"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        log_date = request.form.get('date', date.today())
        meal_type = request.form['meal_type']
        dish_id = request.form['dish_id']
        portion = float(request.form.get('portion', 1.0))
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                
                # Get food info
                cursor.execute("SELECT * FROM food_items WHERE id = %s", (dish_id,))
                food = cursor.fetchone()
                
                if food:
                    calories = food['calories'] * portion
                    
                    # Insert log
                    cursor.execute("""
                        INSERT INTO user_logs (user_id, date, meal_type, dish_id, 
                                             dish_name, calories_consumed)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, log_date, meal_type, dish_id, food['dish_name'], calories))
                    
                    connection.commit()
                    flash('Food logged successfully!', 'success')
                
            except Error as e:
                flash(f'Error logging food: {e}', 'error')
            finally:
                cursor.close()
                connection.close()
        
        return redirect(url_for('log_food'))
    
    # GET request - show form
    connection = get_db_connection()
    foods = []
    recent_logs = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get all foods
            cursor.execute("SELECT * FROM food_items ORDER BY dish_name")
            foods = cursor.fetchall()
            
            # Get recent logs
            cursor.execute("""
                SELECT ul.*, fi.dish_name 
                FROM user_logs ul
                LEFT JOIN food_items fi ON ul.dish_id = fi.id
                WHERE ul.user_id = %s AND ul.date >= %s
                ORDER BY ul.created_at DESC
                LIMIT 10
            """, (session['user_id'], date.today() - timedelta(days=7)))
            recent_logs = cursor.fetchall()
            
        except Error as e:
            flash(f'Error loading foods: {e}', 'error')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('log_food.html', foods=foods, recent_logs=recent_logs, date=date)

@app.route('/health_tracking', methods=['GET', 'POST'])
def health_tracking():
    """Log sleep, mood, water, steps"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        log_date = request.form.get('date', date.today())
        sleep_hours = float(request.form.get('sleep_hours', 0))
        water_liters = float(request.form.get('water_liters', 0))
        steps = int(request.form.get('steps', 0))
        mood = request.form.get('mood')
        weight_kg = request.form.get('weight_kg')
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Check if entry exists for today
                cursor.execute("""
                    SELECT id FROM user_logs 
                    WHERE user_id = %s AND date = %s AND meal_type IS NULL
                    LIMIT 1
                """, (user_id, log_date))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing entry
                    cursor.execute("""
                        UPDATE user_logs 
                        SET sleep_hours = %s, water_liters = %s, steps = %s, 
                            mood = %s, weight_kg = %s
                        WHERE id = %s
                    """, (sleep_hours, water_liters, steps, mood, 
                          float(weight_kg) if weight_kg else None, existing[0]))
                else:
                    # Insert new entry
                    cursor.execute("""
                        INSERT INTO user_logs (user_id, date, sleep_hours, water_liters, 
                                             steps, mood, weight_kg)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, log_date, sleep_hours, water_liters, steps, mood,
                          float(weight_kg) if weight_kg else None))
                
                connection.commit()
                flash('Health data logged successfully!', 'success')
                
            except Error as e:
                flash(f'Error logging health data: {e}', 'error')
            finally:
                cursor.close()
                connection.close()
    
    return render_template('health_tracking.html', date=date)

@app.route('/reports')
def reports():
    """Reports page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('reports.html', date=date, timedelta=timedelta)

@app.route('/export_pdf')
def export_pdf():
    """Export PDF report"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    start_date = request.args.get('start_date', (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    # Generate PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"Health Report - {session['name']}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Date range
    date_range = Paragraph(f"Period: {start_date} to {end_date}", styles['Normal'])
    story.append(date_range)
    story.append(Spacer(1, 12))
    
    # Get data from database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get summary data
            cursor.execute("""
                SELECT 
                    AVG(calories_consumed) as avg_calories,
                    AVG(water_liters) as avg_water,
                    AVG(sleep_hours) as avg_sleep,
                    AVG(steps) as avg_steps
                FROM user_logs 
                WHERE user_id = %s AND date BETWEEN %s AND %s
            """, (user_id, start_date, end_date))
            
            summary = cursor.fetchone()
            
            if summary:
                # Summary table
                summary_data = [
                    ['Metric', 'Average'],
                    ['Calories', f"{summary['avg_calories']:.0f}" if summary['avg_calories'] else "0"],
                    ['Water (L)', f"{summary['avg_water']:.1f}" if summary['avg_water'] else "0"],
                    ['Sleep (hrs)', f"{summary['avg_sleep']:.1f}" if summary['avg_sleep'] else "0"],
                    ['Steps', f"{summary['avg_steps']:.0f}" if summary['avg_steps'] else "0"]
                ]
                
                table = Table(summary_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
            
        except Error as e:
            print(f"Error generating PDF: {e}")
        finally:
            cursor.close()
            connection.close()
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'health_report_{start_date}_to_{end_date}.pdf',
        mimetype='application/pdf'
    )

@app.route('/export_excel')
def export_excel():
    """Export Excel report"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    start_date = request.args.get('start_date', (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get detailed logs
            cursor.execute("""
                SELECT ul.date, ul.meal_type, ul.dish_name, ul.calories_consumed,
                       ul.water_liters, ul.sleep_hours, ul.steps, ul.mood, ul.weight_kg
                FROM user_logs ul
                WHERE ul.user_id = %s AND ul.date BETWEEN %s AND %s
                ORDER BY ul.date DESC, ul.meal_type
            """, (user_id, start_date, end_date))
            
            logs = cursor.fetchall()
            
            if logs:
                df = pd.DataFrame(logs)
                
                # Create Excel file
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Health Logs', index=False)
                
                buffer.seek(0)
                
                return send_file(
                    buffer,
                    as_attachment=True,
                    download_name=f'health_data_{start_date}_to_{end_date}.xlsx',
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            
        except Error as e:
            flash(f'Error generating Excel report: {e}', 'error')
        finally:
            cursor.close()
            connection.close()
    
    flash('No data found for the selected period', 'warning')
    return redirect(url_for('reports'))

@app.route('/community')
def community():
    """Community forum page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    posts = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT cp.*, u.name as author_name
                FROM community_posts cp
                JOIN users u ON cp.user_id = u.id
                ORDER BY cp.created_at DESC
                LIMIT 20
            """)
            posts = cursor.fetchall()
        except Error as e:
            flash(f'Error loading posts: {e}', 'error')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('community.html', posts=posts)

@app.route('/add_post', methods=['POST'])
def add_post():
    """Add community post"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    content = request.form['content']
    post_type = request.form['post_type']
    user_id = session['user_id']
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO community_posts (user_id, title, content, post_type)
                VALUES (%s, %s, %s, %s)
            """, (user_id, title, content, post_type))
            connection.commit()
            flash('Post added successfully!', 'success')
        except Error as e:
            flash(f'Error adding post: {e}', 'error')
        finally:
            cursor.close()
            connection.close()
    
    return redirect(url_for('community'))

@app.route('/api/water_reminder')
def water_reminder():
    """API endpoint for water reminder"""
    return jsonify({'message': 'Time to drink 250ml of water! 💧'})

@app.route('/calendar')
def calendar_view():
    """Calendar view of health logs"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    month = int(request.args.get('month', date.today().month))
    year = int(request.args.get('year', date.today().year))
    
    # Calculate calendar info
    import calendar
    cal = calendar.monthcalendar(year, month)
    first_day = calendar.monthrange(year, month)[0]  # 0=Monday, 6=Sunday
    days_in_month = calendar.monthrange(year, month)[1]
    
    # Adjust for Sunday start (HTML calendar starts with Sunday)
    first_day = (first_day + 1) % 7
    
    # Month navigation
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    connection = get_db_connection()
    calendar_data = {}
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get month's data
            cursor.execute("""
                SELECT date, 
                       SUM(calories_consumed) as daily_calories,
                       AVG(water_liters) as daily_water,
                       AVG(sleep_hours) as daily_sleep
                FROM user_logs 
                WHERE user_id = %s AND MONTH(date) = %s AND YEAR(date) = %s
                GROUP BY date
            """, (user_id, month, year))
            
            logs = cursor.fetchall()
            
            for log in logs:
                day = log['date'].day
                # Simple health score calculation
                score = 0
                if log['daily_calories']: score += 25
                if log['daily_water'] and log['daily_water'] >= 2: score += 25
                if log['daily_sleep'] and log['daily_sleep'] >= 7: score += 25
                score += 25  # Base score
                
                calendar_data[day] = {
                    'score': score,
                    'calories': log['daily_calories'] or 0,
                    'water': log['daily_water'] or 0,
                    'sleep': log['daily_sleep'] or 0
                }
                
        except Error as e:
            flash(f'Error loading calendar: {e}', 'error')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('calendar.html', 
                         calendar_data=calendar_data, 
                         month=month, 
                         year=year,
                         first_day_of_month=first_day,
                         days_in_month=days_in_month,
                         month_names=month_names,
                         prev_month=prev_month,
                         prev_year=prev_year,
                         next_month=next_month,
                         next_year=next_year)