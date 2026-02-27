import telebot
from telebot import types
from calculator import calculate_matrix, get_total_number_description
from database import (
    save_calculation, 
    get_user_calculations,
    get_user_stats,
    save_user,
    save_stat,
    save_analysis,
    get_user_analyses,
    get_analysis_by_name,
    delete_analysis
)
from formatter import format_pretty_matrix, format_matrix_with_headers, format_short_matrix
import time
import os
import json

TOKEN = os.getenv('BOT_TOKEN', '8592056819:AAFO7bstGsvwEr1OIlqS_4vhT0ehQGkiZL4')
bot = telebot.TeleBot(TOKEN, threaded=True)

print("=" * 50)
print("🤖 PSY CODE MATRIX BOT")
print("📊 Версия с сохранением разборов")
print("=" * 50)

# ============================================
# КЛАВИАТУРЫ
# ============================================

def get_main_keyboard():
    """Основная клавиатура"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton("🧮 Рассчитать")
    btn2 = types.KeyboardButton("📜 История")
    btn3 = types.KeyboardButton("📊 Статистика")
    btn4 = types.KeyboardButton("🔮 Анализ")
    btn5 = types.KeyboardButton("💾 Мои разборы")
    btn6 = types.KeyboardButton("❓ Помощь")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

# ============================================
# ОСНОВНЫЕ КОМАНДЫ
# ============================================

@bot.message_handler(commands=['start', 'help', 'menu'])
def start_command(message):
    """Главное меню"""
    print(f"📨 /start от {message.from_user.username or message.chat.id}")
    
    try:
        save_user(
            message.chat.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        save_stat(message.chat.id, 'start_command')
    except:
        pass
    
    welcome_text = """
🌟 *Психоматрица Пифагора* 🌟

Я рассчитаю вашу матрицу судьбы по дате рождения!

*✨ Возможности:*
• 🧮 Рассчитать психоматрицу
• 📜 Просмотреть историю расчетов  
• 📊 Узнать свою статистику
• 🔮 Получить детальный анализ
• 💾 Сохранять разборы с именами

*📅 Формат даты:* **ДД.ММ.ГГГГ**
*✨ Пример:* **15.08.1994**

Выберите действие ниже 👇
"""
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

    # Если команда пришла с параметром (датой)
    if len(message.text.split()) > 1:
        birthdate = message.text.split()[1]
        message.text = birthdate
        handle_date_input(message)

@bot.message_handler(commands=['history'])
def history_command(message):
    """Показывает историю расчетов"""
    show_history(message.chat.id)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Показывает статистику"""
    show_stats(message.chat.id)

@bot.message_handler(commands=['analysis', 'анализ', 'full'])
def analysis_command(message):
    """Полный детальный анализ"""
    full_analysis(message.chat.id)

@bot.message_handler(commands=['save'])
def save_command(message):
    """Сохранить последний расчет с именем"""
    msg = bot.send_message(
        message.chat.id,
        "📝 *Введите имя для этого разбора:*\n\n"
        "Например: *Мама*, *Папа*, *2025 год*",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_save_name)

@bot.message_handler(commands=['list'])
def list_command(message):
    """Показать список сохраненных разборов"""
    show_saved_analyses(message.chat.id)

@bot.message_handler(commands=['get'])
def get_command(message):
    """Показать конкретный разбор"""
    msg = bot.send_message(
        message.chat.id,
        "📝 *Введите имя разбора, который хотите увидеть:*",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_get_name)

@bot.message_handler(commands=['delete'])
def delete_command(message):
    """Удалить разбор"""
    msg = bot.send_message(
        message.chat.id,
        "📝 *Введите имя разбора, который хотите удалить:*",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_delete_name)

# ============================================
# ОБРАБОТЧИКИ КНОПОК
# ============================================

@bot.message_handler(func=lambda msg: msg.text == "🧮 Рассчитать")
def ask_for_date(message):
    """Запрос даты для расчета"""
    bot.send_message(
        message.chat.id,
        "📅 *Введите дату рождения:*\n\n"
        "Формат: **ДД.ММ.ГГГГ**\n"
        "Пример: **15.08.1994**",
        parse_mode='Markdown'
    )
    save_stat(message.chat.id, 'calculate_button')

@bot.message_handler(func=lambda msg: msg.text == "📜 История")
def handle_history_button(message):
    """Кнопка истории"""
    show_history(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "📊 Статистика")
def handle_stats_button(message):
    """Кнопка статистики"""
    show_stats(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "🔮 Анализ")
def handle_analysis_button(message):
    """Кнопка анализа"""
    full_analysis(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "💾 Мои разборы")
def handle_saved_button(message):
    """Кнопка сохраненных разборов"""
    show_saved_analyses(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "❓ Помощь")
def handle_help_button(message):
    """Кнопка помощи"""
    help_text = """
🆘 *Помощь*

*🧮 Рассчитать* - новый расчет
*📜 История* - последние 10 расчетов
*📊 Статистика* - ваша статистика
*🔮 Анализ* - детальный разбор последнего
*💾 Мои разборы* - сохраненные с именами

*Команды:*
/save ИМЯ - сохранить последний расчет
/list - список сохраненных
/get ИМЯ - показать разбор
/delete ИМЯ - удалить разбор

*📅 Формат даты:* **ДД.ММ.ГГГГ**
"""
    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# ============================================
# ОБРАБОТКА ДАТЫ
# ============================================

@bot.message_handler(func=lambda msg: '.' in msg.text and len(msg.text) == 10)
def handle_date_input(message):
    """Обработка ввода даты"""
    user_text = message.text.strip()
    print(f"📨 Дата от {message.chat.id}: {user_text}")
    
    try:
        result = calculate_matrix(user_text)
        
        if not result['success']:
            bot.send_message(
                message.chat.id,
                "❌ *Неверный формат!*\n\n"
                "Используйте: **ДД.ММ.ГГГГ**\n"
                "Пример: **15.08.1994**",
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
            return
        
        # Сохраняем в базу (историю)
        try:
            calc_id = save_calculation(message.chat.id, user_text, result)
            save_stat(message.chat.id, 'calculation_saved', {'calc_id': calc_id})
        except Exception as e:
            print(f"⚠️ Ошибка сохранения в историю: {e}")
        
        # Сохраняем результат в user_data для последующего сохранения
        if not hasattr(bot, 'user_data'):
            bot.user_data = {}
        bot.user_data[message.chat.id] = {'last_result': result}
        
        # Показываем результат
        show_calculation_result(message.chat.id, result)
        
        print(f"✅ Расчет готов для {message.chat.id}")
        
    except Exception as e:
        print(f"❌ Ошибка обработки даты: {e}")
        bot.send_message(
            message.chat.id,
            "⚠️ *Внутренняя ошибка*\nПопробуйте еще раз.",
            parse_mode='Markdown'
        )

# ============================================
# ФУНКЦИИ ПОКАЗА РЕЗУЛЬТАТОВ
# ============================================

def show_calculation_result(chat_id, result):
    """Показывает результат расчета (краткий)"""
    m = result['matrix']
    
    # Используем красивый формат
    matrix_display = format_pretty_matrix(m)
    
    response = f"""
✅ *Расчет готов!*

📅 *Дата:* {result['date']}

{matrix_display}
*Цифры матрицы:*
1️⃣ Характер: {m.get(1, 0)}
2️⃣ Энергия: {m.get(2, 0)}
3️⃣ Интерес: {m.get(3, 0)}
4️⃣ Здоровье: {m.get(4, 0)}
5️⃣ Логика: {m.get(5, 0)}
6️⃣ Труд: {m.get(6, 0)}
7️⃣ Удача: {m.get(7, 0)}
8️⃣ Долг: {m.get(8, 0)}
9️⃣ Память: {m.get(9, 0)}

🔢 *Рабочие числа:*
РЧ1 = {result['work_numbers'][0]}
РЧ2 = {result['work_numbers'][1]}
РЧ3 = {result['work_numbers'][2]}
РЧ4 = {result['work_numbers'][3]}

✨ *Общее число:* {result['total_number']}
{result['total_description']}

💡 Используйте */save имя* чтобы сохранить этот разбор
"""
    
    bot.send_message(
        chat_id,
        response,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

def show_history(chat_id):
    """Показывает историю расчетов"""
    try:
        calculations = get_user_calculations(chat_id, limit=10)
        
        if not calculations:
            bot.send_message(
                chat_id,
                "📭 *История пуста*\n\n"
                "У вас еще нет сохраненных расчетов.\n"
                "Нажмите *🧮 Рассчитать* чтобы начать!",
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
            return
        
        history_text = "📜 *Последние расчеты:*\n\n"
        
        for i, calc in enumerate(calculations, 1):
            matrix_data = calc.get('matrix_data', {})
            matrix = matrix_data.get('matrix', {})
            
            if matrix:
                matrix_summary = format_short_matrix(matrix)
            else:
                matrix_summary = "нет данных"
            
            history_text += f"*{i}. {calc['birthdate']}*\n"
            history_text += f"   🧮 {matrix_summary}\n"
            if calc.get('created_at'):
                history_text += f"   📅 {calc['created_at'][:10]}\n"
            history_text += "\n"
        
        history_text += "Для повтора отправьте дату заново."
        
        bot.send_message(
            chat_id,
            history_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
        save_stat(chat_id, 'history_viewed')
        
    except Exception as e:
        print(f"❌ Ошибка показа истории: {e}")
        bot.send_message(
            chat_id,
            "⚠️ *Ошибка загрузки истории*\nПопробуйте позже.",
            parse_mode='Markdown'
        )

def show_stats(chat_id):
    """Показывает статистику"""
    try:
        stats = get_user_stats(chat_id)
        
        stats_text = f"""
📊 *Ваша статистика:*

• 📈 Всего расчетов: *{stats['total_calculations']}*
• 💾 Сохраненных разборов: *{stats['total_saved']}*
• 🕐 Первый расчет: *{stats['first_calculation'][:10] if stats['first_calculation'] else 'нет данных'}*
• 🕐 Последний расчет: *{stats['last_calculation'][:10] if stats['last_calculation'] else 'нет данных'}*

✨ Продолжайте изучать свою матрицу!
"""
        
        bot.send_message(
            chat_id,
            stats_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
        save_stat(chat_id, 'stats_viewed')
        
    except Exception as e:
        print(f"❌ Ошибка показа статистики: {e}")
        bot.send_message(
            chat_id,
            "📊 *Статистика:*\n\nПока нет данных.",
            parse_mode='Markdown'
        )

def full_analysis(chat_id):
    """Полный детальный анализ (ОДНО сообщение)"""
    print(f"🔮 Анализ запрошен {chat_id}")
    
    try:
        calculations = get_user_calculations(chat_id, limit=1)
        
        if not calculations:
            bot.send_message(
                chat_id,
                "📭 *Сначала сделайте расчет!*\n\n"
                "Отправьте дату рождения (например: 15.08.1994)",
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
            return
        
        last_calc = calculations[0]
        matrix_data = last_calc['matrix_data']
        matrix = matrix_data.get('matrix', {})
        birthdate = last_calc['birthdate']
        
        # Собираем всё в одно сообщение
        analysis_text = f"""
🔮 *ДЕТАЛЬНЫЙ АНАЛИЗ МАТРИЦЫ*
📅 Дата: {birthdate}

{format_matrix_with_headers(matrix)}

*Цифры матрицы:*
1️⃣ *Характер* ({matrix.get(1,0)}): {"Слабый" if matrix.get(1,0)<=1 else "Средний" if matrix.get(1,0)<=2 else "Сильный"}
2️⃣ *Энергия* ({matrix.get(2,0)}): {"Низкая" if matrix.get(2,0)<=1 else "Средняя" if matrix.get(2,0)<=2 else "Высокая"}
3️⃣ *Интерес* ({matrix.get(3,0)}): {"Узкий" if matrix.get(3,0)<=1 else "Разносторонний" if matrix.get(3,0)<=2 else "Очень разносторонний"}
4️⃣ *Здоровье* ({matrix.get(4,0)}): {"Слабое" if matrix.get(4,0)<=1 else "Нормальное" if matrix.get(4,0)<=2 else "Крепкое"}
5️⃣ *Логика* ({matrix.get(5,0)}): {"Интуиция" if matrix.get(5,0)<=1 else "Логика" if matrix.get(5,0)<=2 else "Гениальность"}
6️⃣ *Труд* ({matrix.get(6,0)}): {"Не любит" if matrix.get(6,0)<=1 else "Нормально" if matrix.get(6,0)<=2 else "Трудоголик"}
7️⃣ *Удача* ({matrix.get(7,0)}): {"Невезучий" if matrix.get(7,0)<=1 else "Везучий" if matrix.get(7,0)<=2 else "Баловень судьбы"}
8️⃣ *Долг* ({matrix.get(8,0)}): {"Безответственный" if matrix.get(8,0)<=1 else "Ответственный" if matrix.get(8,0)<=2 else "Гиперответственный"}
9️⃣ *Память* ({matrix.get(9,0)}): {"Слабая" if matrix.get(9,0)<=1 else "Хорошая" if matrix.get(9,0)<=2 else "Феноменальная"}

🔢 *Рабочие числа:*
РЧ1 = {matrix_data.get('work_numbers', [0,0,0,0])[0]}
РЧ2 = {matrix_data.get('work_numbers', [0,0,0,0])[1]}
РЧ3 = {matrix_data.get('work_numbers', [0,0,0,0])[2]}
РЧ4 = {matrix_data.get('work_numbers', [0,0,0,0])[3]}

✨ *Общее число:* {matrix_data.get('total_number', 0)}
{matrix_data.get('total_description', '')}

💡 *Совет:* Развивайте слабые стороны и укрепляйте сильные!
"""
        
        bot.send_message(
            chat_id,
            analysis_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
        save_stat(chat_id, 'analysis_viewed')
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        bot.send_message(
            chat_id,
            "⚠️ *Ошибка при анализе*\nПопробуйте позже.",
            parse_mode='Markdown'
        )

# ============================================
# ФУНКЦИИ ДЛЯ СОХРАНЕНИЯ РАЗБОРОВ
# ============================================

def process_save_name(message):
    """Обрабатывает ввод имени для сохранения"""
    name = message.text.strip()
    chat_id = message.chat.id
    
    if not name:
        bot.send_message(chat_id, "❌ Имя не может быть пустым")
        return
    
    # Проверяем, есть ли последний результат
    if not hasattr(bot, 'user_data') or chat_id not in bot.user_data:
        bot.send_message(
            chat_id,
            "❌ *Нет последнего расчета*\n\n"
            "Сначала сделайте расчет даты.",
            parse_mode='Markdown'
        )
        return
    
    last_result = bot.user_data[chat_id].get('last_result')
    if not last_result:
        bot.send_message(
            chat_id,
            "❌ *Нет последнего расчета*\n\n"
            "Сначала сделайте расчет даты.",
            parse_mode='Markdown'
        )
        return
    
    # Сохраняем
    success, result = save_analysis(
        chat_id, 
        name, 
        last_result['date'], 
        last_result
    )
    
    if success:
        bot.send_message(
            chat_id,
            f"✅ *Разбор сохранен!*\n\n"
            f"📝 Имя: *{name}*\n"
            f"📅 Дата: {last_result['date']}\n\n"
            f"Используйте /get {name} чтобы увидеть его снова.",
            parse_mode='Markdown'
        )
        save_stat(chat_id, 'analysis_saved', {'name': name})
    else:
        bot.send_message(
            chat_id,
            f"❌ *Ошибка*\n\n{result}",
            parse_mode='Markdown'
        )

def show_saved_analyses(chat_id):
    """Показывает список сохраненных разборов"""
    try:
        analyses = get_user_analyses(chat_id)
        
        if not analyses:
            bot.send_message(
                chat_id,
                "📭 *У вас нет сохраненных разборов*\n\n"
                "Сделайте расчет и используйте */save имя* чтобы сохранить.",
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
            return
        
        text = "📚 *Ваши сохраненные разборы:*\n\n"
        
        for a in analyses:
            text += f"📝 *{a['name']}*\n"
            text += f"   📅 {a['birthdate']}\n"
            text += f"   🕐 {a['created_at'][:10]}\n"
            text += f"   👉 /get {a['name']}\n\n"
        
        text += "Используйте */get имя* чтобы увидеть полный разбор."
        
        bot.send_message(
            chat_id,
            text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
        save_stat(chat_id, 'list_viewed')
        
    except Exception as e:
        print(f"❌ Ошибка показа списка: {e}")
        bot.send_message(
            chat_id,
            "⚠️ *Ошибка загрузки списка*",
            parse_mode='Markdown'
        )

def process_get_name(message):
    """Показывает сохраненный разбор по имени"""
    name = message.text.strip()
    chat_id = message.chat.id
    
    analysis = get_analysis_by_name(chat_id, name)
    
    if not analysis:
        bot.send_message(
            chat_id,
            f"❌ *Разбор '{name}' не найден*",
            parse_mode='Markdown'
        )
        return
    
    result = analysis['matrix_data']
    matrix = result.get('matrix', {})
    
    analysis_text = f"""
📝 *Сохраненный разбор: {name}*
📅 Дата: {analysis['birthdate']}

{format_pretty_matrix(matrix)}

*Цифры матрицы:*
1️⃣ Характер: {matrix.get(1,0)}
2️⃣ Энергия: {matrix.get(2,0)}
3️⃣ Интерес: {matrix.get(3,0)}
4️⃣ Здоровье: {matrix.get(4,0)}
5️⃣ Логика: {matrix.get(5,0)}
6️⃣ Труд: {matrix.get(6,0)}
7️⃣ Удача: {matrix.get(7,0)}
8️⃣ Долг: {matrix.get(8,0)}
9️⃣ Память: {matrix.get(9,0)}

🔢 *Рабочие числа:*
РЧ1 = {result.get('work_numbers', [0,0,0,0])[0]}
РЧ2 = {result.get('work_numbers', [0,0,0,0])[1]}
РЧ3 = {result.get('work_numbers', [0,0,0,0])[2]}
РЧ4 = {result.get('work_numbers', [0,0,0,0])[3]}

✨ *Общее число:* {result.get('total_number', 0)}
{result.get('total_description', '')}
"""
    
    bot.send_message(
        chat_id,
        analysis_text,
        parse_mode='Markdown'
    )
    save_stat(chat_id, 'analysis_retrieved', {'name': name})

def process_delete_name(message):
    """Удаляет сохраненный разбор"""
    name = message.text.strip()
    chat_id = message.chat.id
    
    if delete_analysis(chat_id, name):
        bot.send_message(
            chat_id,
            f"✅ *Разбор '{name}' удален*",
            parse_mode='Markdown'
        )
        save_stat(chat_id, 'analysis_deleted', {'name': name})
    else:
        bot.send_message(
            chat_id,
            f"❌ *Разбор '{name}' не найден*",
            parse_mode='Markdown'
        )

# ============================================
# ОБРАБОТЧИК НЕИЗВЕСТНЫХ СООБЩЕНИЙ
# ============================================

@bot.message_handler(func=lambda msg: True)
def handle_unknown(message):
    """Обработчик всего остального"""
    if message.text:
        print(f"❓ Неизвестное сообщение от {message.chat.id}: {message.text[:50]}")
    
    bot.send_message(
        message.chat.id,
        "🤔 *Не понимаю*\n\n"
        "Используйте кнопки меню или отправьте дату:\n"
        "📅 **ДД.ММ.ГГГГ**",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# ============================================
# ЗАПУСК БОТА
# ============================================

def run_bot_safe():
    """Запуск бота с обработкой ошибок"""
    while True:
        try:
            print("=" * 50)
            print(f"🚀 Запускаю бота... {time.strftime('%H:%M:%S')}")
            print("=" * 50)
            
            bot.polling(none_stop=True, interval=1, timeout=30)
            
        except Exception as e:
            print(f"⚠️ Ошибка бота: {type(e).__name__}")
            print(f"   Сообщение: {str(e)}")
            print(f"🔄 Перезапуск через 5 секунд...")
            time.sleep(5)

if __name__ == "__main__":
    # Инициализируем хранилище для последних результатов
    bot.user_data = {}
    run_bot_safe()