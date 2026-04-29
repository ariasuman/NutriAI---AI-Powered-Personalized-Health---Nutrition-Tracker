# AI-Based Personalized Health & Nutrition Tracker

A comprehensive web application built with Flask that provides personalized health and nutrition tracking with AI-powered meal planning, health analytics, and comprehensive reporting.

## Features

### Core Functionality
- **User Registration & Profiles** - Complete user management with health goals
- **Personalized Meal Planning** - AI-generated meal plans using BMR/TDEE calculations
- **Food Logging** - Comprehensive nutrition tracking with Indian food database
- **Health Tracking** - Sleep, mood, water intake, and activity monitoring
- **Weekly Health Score** - 0-100 scoring system based on multiple health metrics
- **Calendar View** - Visual representation of daily health scores
- **Community Forum** - Share recipes, workouts, and health tips
- **Export Reports** - PDF and Excel reports with charts and analytics

### Technical Features
- **Database Integration** - MySQL with 25+ records across 5 tables
- **Data Visualization** - Matplotlib charts embedded in web UI
- **Report Generation** - PDF (ReportLab) and Excel (pandas/openpyxl) exports
- **Responsive Design** - Bootstrap-based mobile-friendly interface
- **Water Reminders** - JavaScript-based hydration notifications
- **Nutrition Alerts** - Warnings for excessive/deficient nutrients

## Technology Stack

- **Backend**: Python 3.10+, Flask
- **Database**: MySQL (wellness_db)
- **ORM**: mysql-connector-python
- **Frontend**: Jinja2 templates + Bootstrap 5
- **Charts**: Matplotlib
- **PDF Generation**: ReportLab
- **Excel Export**: pandas + openpyxl
- **Security**: bcrypt password hashing

## Installation & Setup

### Prerequisites
- Python 3.10+ (tested with 3.11.9)
- MySQL Server 8.0+
- Git (optional)

### Step 1: Clone/Download Project
```bash
# If using Git
git clone <repository-url>
cd python-project3

# Or download and extract the ZIP file
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Database Setup
1. **Create MySQL Database**:
   ```sql
   CREATE DATABASE wellness_db;
   ```

2. **Create Tables**:
   ```bash
   mysql -u root -p wellness_db < create_tables.sql
   ```

3. **Configure Database Connection**:
   - Copy `.env.example` to `.env`
   - Update database credentials:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=wellness_db
   FLASK_SECRET_KEY=your_secret_key_here
   ```

### Step 4: Import Food Data
1. **Download the Indian Food Nutrition Dataset**:
   - Ensure the file `Indian_Food_Nutrition_Processed1.csv` is located at:
   - `C:\Users\Admin\Downloads\Indian_Food_Nutrition_Processed1.csv`

2. **Run the Import Script**:
   ```bash
   python import_foods.py
   ```
   
   This will populate the `food_items` table with nutrition data for Indian foods.

### Step 5: Start the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Usage Guide

### Getting Started
1. **Register**: Create a new account with your health profile
2. **Set Goals**: Choose weight loss, maintenance, or gain
3. **Generate Meal Plan**: Get AI-powered meal recommendations
4. **Log Food**: Track daily nutrition intake
5. **Monitor Health**: Log sleep, mood, water, and activity
6. **View Progress**: Check dashboard charts and calendar view
7. **Export Reports**: Generate PDF/Excel reports for analysis

### Test User Credentials
For testing purposes, you can create a user with these sample details:
- **Username**: testuser
- **Password**: password123
- **Name**: Test User
- **Age**: 30
- **Gender**: Male/Female
- **Height**: 170 cm
- **Weight**: 70 kg
- **Activity Level**: Moderate
- **Goal**: Maintain Weight

## Meal Plan Algorithm

The meal planning system uses the following approach:

### 1. Calorie Calculation
- **BMR Calculation**: Uses Mifflin-St Jeor equation
  - Male: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5
  - Female: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161

- **TDEE Calculation**: BMR × Activity Factor
  - Sedentary: 1.2
  - Light: 1.375
  - Moderate: 1.55
  - Active: 1.725

### 2. Goal Adjustment
- **Weight Loss**: TDEE - 500 calories (1 lb/week loss)
- **Weight Gain**: TDEE + 500 calories (1 lb/week gain)
- **Maintenance**: TDEE calories

### 3. Meal Distribution
- **Breakfast**: 25% of daily calories
- **Lunch**: 30% of daily calories
- **Dinner**: 25% of daily calories
- **Snacks**: 20% of daily calories

### 4. Food Selection Algorithm
- Randomly selects 1-3 foods per meal from database
- Calculates optimal portions to meet calorie targets
- Prioritizes high-protein foods for weight loss goals
- Considers nutritional balance and variety

## Database Schema

### Tables Overview
1. **users** - User profiles and goals
2. **food_items** - Nutrition database (from CSV)
3. **user_logs** - Daily food and health logs
4. **weekly_reports** - Calculated health scores
5. **community_posts** - Forum posts and discussions

### Key SQL Queries
The application includes 15+ optimized SQL queries for:
- User analytics and trends
- Nutrition analysis and alerts
- Health score calculations
- Community features
- Report generation

See `sql_queries.sql` for complete query documentation.

## Health Score Calculation

Weekly health score (0-100) based on:
- **Calorie Accuracy (40%)**: How close daily intake is to TDEE target
- **Water Intake (20%)**: Daily hydration vs 2.5L target
- **Sleep Quality (20%)**: 7-9 hours optimal range
- **Activity Level (20%)**: 8000+ steps daily target

## File Structure
```
python-project3/
├── app.py                 # Main Flask application
├── routes.py             # Additional route handlers
├── import_foods.py       # CSV data importer
├── create_tables.sql     # Database schema
├── sql_queries.sql       # Sample SQL queries
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── meal_plan.html
│   ├── log_food.html
│   ├── health_tracking.html
│   ├── reports.html
│   ├── community.html
│   ├── calendar.html
│   ├── login.html
│   └── register.html
└── static/             # CSS, JS, images (auto-created)
```

## Security Features
- Password hashing with bcrypt
- Session management
- SQL injection prevention
- Environment variable configuration
- Input validation and sanitization

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Verify MySQL is running
   - Check credentials in `.env` file
   - Ensure `wellness_db` database exists

2. **CSV Import Fails**:
   - Verify file path: `C:\Users\Admin\Downloads\Indian_Food_Nutrition_Processed1.csv`
   - Check file encoding (should be Latin-1)
   - Ensure database tables exist

3. **Charts Not Displaying**:
   - Verify matplotlib installation
   - Check if data exists for chart generation
   - Ensure proper file permissions

4. **PDF/Excel Export Issues**:
   - Verify ReportLab and openpyxl installation
   - Check write permissions in temp directory
   - Ensure sufficient data for report generation

### Performance Optimization
- Use database indexes for faster queries
- Implement query result caching for frequently accessed data
- Optimize image sizes for faster loading
- Use pagination for large datasets

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
This project is for educational purposes. Please ensure compliance with any applicable licenses for the datasets used.

## Support
For issues or questions:
1. Check the troubleshooting section
2. Review the SQL queries documentation
3. Verify all dependencies are installed correctly
4. Ensure database setup is complete

## Screenshots
- Dashboard with health metrics and charts
- Meal plan generator with AI recommendations
- Food logging interface with nutrition calculations
- Calendar view with color-coded health scores
- PDF and Excel report samples (generated after use)

---

**Note**: This application is designed for educational and personal use. Always consult healthcare professionals for medical advice and dietary recommendations.