import sqlite3
import json
from datetime import datetime

# ============================================
# ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ
# ============================================

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
    
    # Таблица статистики (опционально)
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
    
    # Проверяем есть ли пользователь
    c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    exists = c.fetchone()
    
    if exists:
        # Обновляем существующего
        c.execute('''UPDATE users 
                     SET username = ?, first_name = ?, last_name = ?
                     WHERE user_id = ?''',
                  (username, first_name, last_name, user_id))
    else:
        # Добавляем нового
        c.execute('''INSERT INTO users 
                     (user_id, username, first_name, last_name, created_at) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, username, first_name, last_name, datetime.now()))
    
    conn.commit()
    conn.close()
    return True

def get_user(user_id):
    """Получает информацию о пользователе"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('''SELECT user_id, username, first_name, last_name, created_at 
                 FROM users WHERE user_id = ?''', (user_id,))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'user_id': result[0],
            'username': result[1],
            'first_name': result[2],
            'last_name': result[3],
            'created_at': result[4]
        }
    return None

# ============================================
# РАБОТА С РАСЧЕТАМИ (ИСТОРИЯ)
# ============================================

def save_calculation(user_id, birthdate, matrix_result):
    """Сохраняет расчет матрицы в базу данных"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    # Сохраняем пользователя если его еще нет
    save_user(user_id)
    
    # Сохраняем расчет
    c.execute('''INSERT INTO calculations 
                 (user_id, birthdate, matrix_data, created_at) 
                 VALUES (?, ?, ?, ?)''',
              (user_id, birthdate, json.dumps(matrix_result), datetime.now()))
    
    calculation_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Логируем в консоль
    print(f"💾 Расчет сохранен: ID {calculation_id}, пользователь {user_id}")
    
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

def get_calculation_by_id(calculation_id):
    """Получает расчет по ID"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('''SELECT user_id, birthdate, matrix_data, created_at 
                 FROM calculations WHERE id = ?''', (calculation_id,))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        try:
            matrix_data = json.loads(result[2])
        except:
            matrix_data = {}
        
        return {
            'user_id': result[0],
            'birthdate': result[1],
            'matrix_data': matrix_data,
            'created_at': result[3]
        }
    return None

def delete_calculation(calculation_id, user_id):
    """Удаляет расчет (только если он принадлежит пользователю)"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    c.execute('''DELETE FROM calculations 
                 WHERE id = ? AND user_id = ?''', (calculation_id, user_id))
    
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
    
    # Количество расчетов
    c.execute('SELECT COUNT(*) FROM calculations WHERE user_id = ?', (user_id,))
    total_calculations = c.fetchone()[0]
    
    # Первый расчет
    c.execute('''SELECT MIN(created_at) FROM calculations 
                 WHERE user_id = ?''', (user_id,))
    first_calculation = c.fetchone()[0]
    
    # Последний расчет
    c.execute('''SELECT MAX(created_at) FROM calculations 
                 WHERE user_id = ?''', (user_id,))
    last_calculation = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_calculations': total_calculations,
        'first_calculation': first_calculation,
        'last_calculation': last_calculation
    }

def get_global_stats():
    """Получает глобальную статистику бота"""
    conn = sqlite3.connect('matrix_bot.db')
    c = conn.cursor()
    
    # Общее количество пользователей
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    # Общее количество расчетов
    c.execute('SELECT COUNT(*) FROM calculations')
    total_calculations = c.fetchone()[0]
    
    # Самая популярная дата
    c.execute('''SELECT birthdate, COUNT(*) as count 
                 FROM calculations 
                 GROUP BY birthdate 
                 ORDER BY count DESC 
                 LIMIT 1''')
    popular_date = c.fetchone()
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_calculations': total_calculations,
        'most_popular_date': popular_date[0] if popular_date else None,
        'popular_date_count': popular_date[1] if popular_date else 0
    }

# ============================================
# УТИЛИТЫ
# ============================================

def get_database_size():
    """Возвращает размер базы данных в МБ"""
    import os
    if os.path.exists('matrix_bot.db'):
        size_bytes = os.path.getsize('matrix_bot.db')
        return round(size_bytes / (1024 * 1024), 2)  # в МБ
    return 0

def backup_database():
    """Создает резервную копию базы данных"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"matrix_bot_backup_{timestamp}.db"
    
    try:
        shutil.copy2('matrix_bot.db', backup_name)
        print(f"✅ Резервная копия создана: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return None

# ============================================
# АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ
# ============================================

# При импорте файла автоматически инициализируем базу
init_database()