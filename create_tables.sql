-- Create wellness_db database and tables
CREATE DATABASE IF NOT EXISTS wellness_db;
USE wellness_db;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('male', 'female', 'other') NOT NULL,
    height_cm FLOAT NOT NULL,
    weight_kg FLOAT NOT NULL,
    activity_level ENUM('sedentary', 'light', 'moderate', 'active') NOT NULL,
    goal ENUM('lose', 'gain', 'maintain') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
);

-- Food items table (from CSV)
CREATE TABLE food_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dish_name VARCHAR(255) NOT NULL,
    calories FLOAT DEFAULT 0,
    carbohydrates FLOAT DEFAULT 0,
    protein FLOAT DEFAULT 0,
    fats FLOAT DEFAULT 0,
    free_sugar FLOAT DEFAULT 0,
    fibre FLOAT DEFAULT 0,
    sodium FLOAT DEFAULT 0,
    calcium FLOAT DEFAULT 0,
    iron FLOAT DEFAULT 0,
    vitamin_c FLOAT DEFAULT 0,
    folate FLOAT DEFAULT 0,
    INDEX idx_dish_name (dish_name),
    INDEX idx_calories (calories),
    INDEX idx_protein (protein)
);

-- User logs table
CREATE TABLE user_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    meal_type ENUM('breakfast', 'lunch', 'dinner', 'snack') DEFAULT NULL,
    dish_id INT DEFAULT NULL,
    dish_name VARCHAR(255) DEFAULT NULL,
    calories_consumed FLOAT DEFAULT 0,
    steps INT DEFAULT 0,
    sleep_hours FLOAT DEFAULT 0,
    water_liters FLOAT DEFAULT 0,
    mood ENUM('very_bad', 'bad', 'neutral', 'good', 'very_good') DEFAULT NULL,
    weight_kg FLOAT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (dish_id) REFERENCES food_items(id) ON DELETE SET NULL,
    INDEX idx_user_date (user_id, date),
    INDEX idx_date (date)
);

-- Weekly reports table
CREATE TABLE weekly_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    week_start DATE NOT NULL,
    health_score FLOAT DEFAULT 0,
    avg_calories FLOAT DEFAULT 0,
    avg_water FLOAT DEFAULT 0,
    avg_sleep FLOAT DEFAULT 0,
    workout_days INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_week (user_id, week_start)
);

-- Community posts table
CREATE TABLE community_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    post_type ENUM('recipe', 'workout', 'general') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_post_type (post_type),
    INDEX idx_created_at (created_at)
);