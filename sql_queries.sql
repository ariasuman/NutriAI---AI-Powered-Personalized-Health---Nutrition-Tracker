-- 10+ Meaningful SQL Queries for Health & Nutrition Tracker

-- 1. List all users with their basic info
SELECT id, username, name, age, gender, height_cm, weight_kg, activity_level, goal 
FROM users 
ORDER BY created_at DESC;

-- 2. Daily calories consumed for a specific user
SELECT date, SUM(calories_consumed) as total_calories
FROM user_logs 
WHERE user_id = 1 AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY date 
ORDER BY date DESC;

-- 3. Weekly average sleep hours for all users
SELECT u.username, AVG(ul.sleep_hours) as avg_sleep_hours
FROM users u
JOIN user_logs ul ON u.id = ul.user_id
WHERE ul.date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY u.id, u.username
HAVING avg_sleep_hours > 0
ORDER BY avg_sleep_hours DESC;

-- 4. Top 5 protein-rich dishes
SELECT dish_name, protein, calories, protein/calories*100 as protein_percentage
FROM food_items 
WHERE calories > 0
ORDER BY protein DESC 
LIMIT 5;

-- 5. Users who exceeded sodium limit this week (>2300mg daily)
SELECT DISTINCT u.username, ul.date, SUM(fi.sodium) as daily_sodium
FROM users u
JOIN user_logs ul ON u.id = ul.user_id
JOIN food_items fi ON ul.dish_id = fi.id
WHERE ul.date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY u.id, ul.date
HAVING daily_sodium > 2300
ORDER BY daily_sodium DESC;

-- 6. Average calories per meal type
SELECT meal_type, AVG(calories_consumed) as avg_calories, COUNT(*) as meal_count
FROM user_logs 
WHERE meal_type IS NOT NULL AND calories_consumed > 0
GROUP BY meal_type 
ORDER BY avg_calories DESC;

-- 7. Top 3 most energy-dense dishes (calories per 100g)
SELECT dish_name, calories, protein, fats, carbohydrates
FROM food_items 
WHERE calories > 0
ORDER BY calories DESC 
LIMIT 3;

-- 8. Users needing iron-rich diet (low iron intake < 10mg daily average)
SELECT u.username, AVG(fi.iron) as avg_daily_iron
FROM users u
JOIN user_logs ul ON u.id = ul.user_id
JOIN food_items fi ON ul.dish_id = fi.id
WHERE ul.date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY u.id, u.username
HAVING avg_daily_iron < 10
ORDER BY avg_daily_iron ASC;

-- 9. Monthly calories trend for a user
SELECT 
    YEAR(date) as year,
    MONTH(date) as month,
    AVG(calories_consumed) as avg_daily_calories,
    SUM(calories_consumed) as total_calories
FROM user_logs 
WHERE user_id = 1 AND date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY YEAR(date), MONTH(date)
ORDER BY year DESC, month DESC;

-- 10. Meal type-wise calorie distribution for last week
SELECT 
    meal_type,
    SUM(calories_consumed) as total_calories,
    COUNT(*) as meal_count,
    AVG(calories_consumed) as avg_calories_per_meal
FROM user_logs 
WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) 
    AND meal_type IS NOT NULL
GROUP BY meal_type
ORDER BY total_calories DESC;

-- 11. Users with best weekly health scores
SELECT u.username, wr.week_start, wr.health_score, wr.avg_calories, wr.avg_water, wr.avg_sleep
FROM users u
JOIN weekly_reports wr ON u.id = wr.user_id
WHERE wr.week_start >= DATE_SUB(CURDATE(), INTERVAL 4 WEEK)
ORDER BY wr.health_score DESC
LIMIT 10;

-- 12. Food items with highest vitamin C content
SELECT dish_name, vitamin_c, calories, protein
FROM food_items 
WHERE vitamin_c > 0
ORDER BY vitamin_c DESC 
LIMIT 10;

-- 13. Daily water intake vs target for users
SELECT 
    u.username,
    ul.date,
    SUM(ul.water_liters) as daily_water,
    CASE 
        WHEN SUM(ul.water_liters) >= 2.5 THEN 'Adequate'
        WHEN SUM(ul.water_liters) >= 2.0 THEN 'Moderate'
        ELSE 'Low'
    END as hydration_status
FROM users u
JOIN user_logs ul ON u.id = ul.user_id
WHERE ul.date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY u.id, ul.date
ORDER BY u.username, ul.date DESC;

-- 14. Most logged foods by users
SELECT fi.dish_name, COUNT(*) as log_count, AVG(fi.calories) as avg_calories
FROM food_items fi
JOIN user_logs ul ON fi.id = ul.dish_id
GROUP BY fi.id, fi.dish_name
ORDER BY log_count DESC
LIMIT 15;

-- 15. Users mood trends over last month
SELECT 
    u.username,
    ul.mood,
    COUNT(*) as mood_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY u.id), 2) as mood_percentage
FROM users u
JOIN user_logs ul ON u.id = ul.user_id
WHERE ul.date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) 
    AND ul.mood IS NOT NULL
GROUP BY u.id, u.username, ul.mood
ORDER BY u.username, mood_count DESC;