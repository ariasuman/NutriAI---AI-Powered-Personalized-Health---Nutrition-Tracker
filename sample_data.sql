-- Sample Data for Health & Nutrition Tracker
-- This file shows example data structure - actual food data comes from CSV import

USE wellness_db;

-- Sample Users (passwords are hashed with bcrypt)
INSERT INTO users (username, password, name, age, gender, height_cm, weight_kg, activity_level, goal) VALUES
('testuser', '$2b$12$LQv3c1yqBwlVHpPjrh8upe5I.B9SxUvJ5FvkUvnyd.g5YGq1c/QyG', 'Test User', 30, 'male', 175.0, 75.0, 'moderate', 'maintain'),
('healthyuser', '$2b$12$LQv3c1yqBwlVHpPjrh8upe5I.B9SxUvnyd.g5YGq1c/QyG', 'Healthy User', 25, 'female', 165.0, 60.0, 'active', 'lose'),
('fitnessuser', '$2b$12$LQv3c1yqBwlVHpPjrh8upe5I.B9SxUvnyd.g5YGq1c/QyG', 'Fitness User', 35, 'male', 180.0, 85.0, 'active', 'gain');

-- Sample Food Items (these will be replaced by CSV import)
INSERT INTO food_items (dish_name, calories, carbohydrates, protein, fats, free_sugar, fibre, sodium, calcium, iron, vitamin_c, folate) VALUES
('Chapati', 104, 18.0, 3.1, 0.4, 0.0, 2.8, 2, 8, 0.6, 0, 3),
('Dal Tadka', 166, 20.0, 9.0, 5.0, 1.0, 8.0, 400, 27, 2.9, 2, 145),
('Chicken Curry', 231, 5.0, 25.0, 12.0, 2.0, 1.0, 600, 15, 1.8, 3, 8),
('Basmati Rice', 130, 28.0, 2.7, 0.3, 0.0, 0.4, 1, 10, 0.2, 0, 8),
('Mixed Vegetable Curry', 89, 12.0, 3.0, 3.5, 4.0, 4.0, 300, 45, 1.2, 25, 35),
('Paneer Butter Masala', 265, 8.0, 14.0, 20.0, 3.0, 2.0, 800, 208, 0.9, 1, 12),
('Samosa', 262, 24.0, 4.0, 17.0, 1.0, 2.0, 422, 21, 1.1, 1, 15),
('Masala Dosa', 168, 28.0, 4.0, 4.5, 1.0, 2.0, 178, 18, 1.4, 0, 18),
('Curd Rice', 97, 16.0, 3.5, 2.0, 2.0, 0.5, 120, 87, 0.3, 1, 5),
('Rajma Curry', 127, 23.0, 8.7, 0.5, 2.0, 6.4, 350, 28, 2.9, 1, 130);

-- Sample User Logs
INSERT INTO user_logs (user_id, date, meal_type, dish_id, dish_name, calories_consumed, steps, sleep_hours, water_liters, mood, weight_kg) VALUES
-- Test User logs
(1, '2024-01-15', 'breakfast', 8, 'Masala Dosa', 168, 0, 0, 0, NULL, NULL),
(1, '2024-01-15', 'lunch', 3, 'Chicken Curry', 231, 0, 0, 0, NULL, NULL),
(1, '2024-01-15', 'lunch', 4, 'Basmati Rice', 130, 0, 0, 0, NULL, NULL),
(1, '2024-01-15', 'dinner', 2, 'Dal Tadka', 166, 0, 0, 0, NULL, NULL),
(1, '2024-01-15', 'dinner', 1, 'Chapati', 208, 0, 0, 0, NULL, NULL),
(1, '2024-01-15', NULL, NULL, NULL, 0, 8500, 7.5, 2.8, 'good', 75.2),

-- Healthy User logs
(2, '2024-01-15', 'breakfast', 9, 'Curd Rice', 97, 0, 0, 0, NULL, NULL),
(2, '2024-01-15', 'lunch', 5, 'Mixed Vegetable Curry', 89, 0, 0, 0, NULL, NULL),
(2, '2024-01-15', 'lunch', 1, 'Chapati', 104, 0, 0, 0, NULL, NULL),
(2, '2024-01-15', 'dinner', 10, 'Rajma Curry', 127, 0, 0, 0, NULL, NULL),
(2, '2024-01-15', 'snack', 7, 'Samosa', 131, 0, 0, 0, NULL, NULL),
(2, '2024-01-15', NULL, NULL, NULL, 0, 12000, 8.0, 3.2, 'very_good', 59.8),

-- Previous day logs for trends
(1, '2024-01-14', 'breakfast', 1, 'Chapati', 104, 0, 0, 0, NULL, NULL),
(1, '2024-01-14', 'lunch', 6, 'Paneer Butter Masala', 265, 0, 0, 0, NULL, NULL),
(1, '2024-01-14', 'dinner', 2, 'Dal Tadka', 166, 0, 0, 0, NULL, NULL),
(1, '2024-01-14', NULL, NULL, NULL, 0, 7200, 6.5, 2.1, 'neutral', 75.5),

(2, '2024-01-14', 'breakfast', 8, 'Masala Dosa', 168, 0, 0, 0, NULL, NULL),
(2, '2024-01-14', 'lunch', 5, 'Mixed Vegetable Curry', 178, 0, 0, 0, NULL, NULL),
(2, '2024-01-14', 'dinner', 10, 'Rajma Curry', 127, 0, 0, 0, NULL, NULL),
(2, '2024-01-14', NULL, NULL, NULL, 0, 10500, 7.8, 2.9, 'good', 60.0);

-- Sample Weekly Reports
INSERT INTO weekly_reports (user_id, week_start, health_score, avg_calories, avg_water, avg_sleep, workout_days) VALUES
(1, '2024-01-08', 78.5, 1850, 2.4, 7.2, 4),
(2, '2024-01-08', 85.2, 1420, 3.0, 7.9, 6),
(3, '2024-01-08', 72.1, 2200, 2.1, 6.8, 3);

-- Sample Community Posts
INSERT INTO community_posts (user_id, title, content, post_type) VALUES
(1, 'High Protein Breakfast Recipe', 'Try this delicious protein-packed breakfast: Scrambled eggs with spinach and whole grain toast. Perfect for muscle building and weight management!', 'recipe'),
(2, '30-Minute Home Workout', 'No gym? No problem! Here is a quick 30-minute bodyweight workout you can do at home: 10 push-ups, 15 squats, 20 jumping jacks, 30-second plank. Repeat 4 times!', 'workout'),
(3, 'Staying Motivated on Your Health Journey', 'Remember that small consistent changes lead to big results. Track your progress, celebrate small wins, and do not be too hard on yourself on off days!', 'general'),
(1, 'Healthy Indian Snack Ideas', 'Replace processed snacks with these healthy alternatives: Roasted chickpeas, fruit chaat, vegetable upma, or homemade trail mix with nuts and dried fruits.', 'recipe'),
(2, 'Morning Yoga Routine', 'Start your day with 15 minutes of yoga. Try sun salutations, warrior poses, and end with child pose. Great for flexibility and mental clarity!', 'workout');

-- Note: The food_items table will be populated with 25+ records from the CSV import
-- The CSV file contains comprehensive Indian food nutrition data including:
-- - Dish names in English
-- - Calories per 100g serving
-- - Macronutrients (carbs, protein, fats)
-- - Micronutrients (vitamins, minerals)
-- - Fiber and sugar content

-- To populate the food_items table, run:
-- python import_foods.py

-- This will import data from: C:\Users\Admin\Downloads\Indian_Food_Nutrition_Processed1.csv