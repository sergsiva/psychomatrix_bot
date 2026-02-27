import sqlite3
import json
from datetime import datetime

def init_database():
    """Создает базу данных и таблицы если их нет"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  created_at TIMESTAMP)''')
    
    # Таблица расчетов (история)
    c.execute('''CREATE TABLE IF NOT EXISTS calculations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  birthdate TEXT,
                  matrix_data TEXT,
                  created_at TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # НОВАЯ ТАБЛИЦА для сохранённых разборов с именами
    c.execute('''CREATE TABLE IF NOT EXISTS saved_analyses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  name TEXT,
                  birthdate TEXT,
                  matrix_data TEXT,
                  created_at TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Таблица статистики
    c.execute('''CREATE TABLE IF NOT EXISTS stats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  action TEXT,
                  details TEXT,
                  created_at TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

# ============================================
# РАБОТА С ПОЛЬЗОВАТЕЛЯМИ
# ============================================

def save_user(user_id, username=None, first_name=None, last_name=None):
    """Сохраняет или обновляет информацию о пользователе"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    exists = c.fetchone()
    
    if exists:
        c.execute('''UPDATE users 
                     SET username = ?, first_name = ?, last_name = ?
                     WHERE user_id = ?''',
                  (username, first_name, last_name, user_id))
    else:
        c.execute('''INSERT INTO users 
                     (user_id, username, first_name, last_name, created_at) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, username, first_name, last_name, datetime.now()))
    
    conn.commit()
    conn.close()
    return True

# ============================================
# РАБОТА С РАСЧЕТАМИ (ИСТОРИЯ)
# ============================================

def save_calculation(user_id, birthdate, matrix_result):
    """Сохраняет расчет матрицы в базу данных"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    save_user(user_id)
    
    c.execute('''INSERT INTO calculations 
                 (user_id, birthdate, matrix_data, created_at) 
                 VALUES (?, ?, ?, ?)''',
              (user_id, birthdate, json.dumps(matrix_result), datetime.now()))
    
    calculation_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return calculation_id

def get_user_calculations(user_id, limit=10):
    """Возвращает историю расчетов пользователя"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('''SELECT id, birthdate, matrix_data, created_at 
                 FROM calculations 
                 WHERE user_id = ? 
                 ORDER BY created_at DESC 
                 LIMIT ?''', (user_id, limit))
    
    results = c.fetchall()
    conn.close()
    
    calculations = []
    for row in results:
        try:
            matrix_data = json.loads(row[2])
        except:
            matrix_data = {}
        
        calculations.append({
            'id': row[0],
            'birthdate': row[1],
            'matrix_data': matrix_data,
            'created_at': row[3]
        })
    
    return calculations

# ============================================
# НОВЫЕ ФУНКЦИИ ДЛЯ СОХРАНЁННЫХ РАЗБОРОВ
# ============================================

def save_analysis(user_id, name, birthdate, matrix_result):
    """Сохраняет разбор с именем"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    # Проверяем, нет ли уже такого имени у пользователя
    c.execute('''SELECT id FROM saved_analyses 
                 WHERE user_id = ? AND name = ?''', (user_id, name))
    exists = c.fetchone()
    
    if exists:
        conn.close()
        return False, "У вас уже есть разбор с таким именем"
    
    c.execute('''INSERT INTO saved_analyses 
                 (user_id, name, birthdate, matrix_data, created_at) 
                 VALUES (?, ?, ?, ?, ?)''',
              (user_id, name, birthdate, json.dumps(matrix_result), datetime.now()))
    
    analysis_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return True, analysis_id

def get_user_analyses(user_id):
    """Возвращает список сохранённых разборов пользователя"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('''SELECT id, name, birthdate, created_at 
                 FROM saved_analyses 
                 WHERE user_id = ? 
                 ORDER BY created_at DESC''', (user_id,))
    
    results = c.fetchall()
    conn.close()
    
    analyses = []
    for row in results:
        analyses.append({
            'id': row[0],
            'name': row[1],
            'birthdate': row[2],
            'created_at': row[3]
        })
    
    return analyses

def get_analysis_by_name(user_id, name):
    """Получает конкретный разбор по имени"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('''SELECT birthdate, matrix_data, created_at 
                 FROM saved_analyses 
                 WHERE user_id = ? AND name = ?''', (user_id, name))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        try:
            matrix_data = json.loads(result[1])
        except:
            matrix_data = {}
        
        return {
            'birthdate': result[0],
            'matrix_data': matrix_data,
            'created_at': result[2]
        }
    return None

def delete_analysis(user_id, name):
    """Удаляет сохранённый разбор"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('''DELETE FROM saved_analyses 
                 WHERE user_id = ? AND name = ?''', (user_id, name))
    
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted

# ============================================
# СТАТИСТИКА
# ============================================

def save_stat(user_id, action, details=None):
    """Сохраняет действие пользователя для статистики"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO stats 
                 (user_id, action, details, created_at) 
                 VALUES (?, ?, ?, ?)''',
              (user_id, action, json.dumps(details) if details else None, datetime.now()))
    
    conn.commit()
    conn.close()
    return True

def get_user_stats(user_id):
    """Получает статистику пользователя"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM calculations WHERE user_id = ?', (user_id,))
    total_calculations = c.fetchone()[0]
    
    c.execute('''SELECT MIN(created_at) FROM calculations 
                 WHERE user_id = ?''', (user_id,))
    first_calculation = c.fetchone()[0]
    
    c.execute('''SELECT MAX(created_at) FROM calculations 
                 WHERE user_id = ?''', (user_id,))
    last_calculation = c.fetchone()[0]
    
    # Количество сохранённых разборов
    c.execute('SELECT COUNT(*) FROM saved_analyses WHERE user_id = ?', (user_id,))
    total_saved = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_calculations': total_calculations,
        'first_calculation': first_calculation,
        'last_calculation': last_calculation,
        'total_saved': total_saved
    }

# Инициализируем базу при импорте
init_database()