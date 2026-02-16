import telebot
from telebot import types
from calculator import calculate_matrix
from database import (
    save_calculation, 
    get_user_calculations,
    get_user_stats,
    save_user,
    save_stat
)
import time
import os
import json

TOKEN = os.getenv('BOT_TOKEN', '8592056819:AAEwVyxh2MZ0kDM9Q-QnHQOxiaj0Z2Fck20')
bot = telebot.TeleBot(TOKEN, threaded=True)

print("=" * 50)
print("🤖 PSY CODE MATRIX BOT")
print("📊 Версия с детальным анализом")
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
    btn5 = types.KeyboardButton("❓ Помощь")
    
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# ============================================
# ОСНОВНЫЕ КОМАНДЫ
# ============================================

@bot.message_handler(commands=['start', 'help', 'menu'])
def start_command(message):
    """Главное меню"""
    print(f"📨 /start от {message.from_user.username or message.chat.id}")
    
    # Сохраняем пользователя
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
        # Отправляем дату в обработчик
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

@bot.message_handler(func=lambda msg: msg.text == "❓ Помощь")
def handle_help_button(message):
    """Кнопка помощи"""
    bot.send_message(
        message.chat.id,
        "🆘 *Помощь*\n\n"
        "*🧮 Рассчитать* - новый расчет\n"
        "*📜 История* - ваши расчеты\n"
        "*📊 Статистика* - ваша статистика\n"
        "*🔮 Анализ* - детальный разбор\n\n"
        "Просто отправьте дату рождения:\n"
        "📅 **ДД.ММ.ГГГГ**",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# ============================================
# ОБРАБОТКА ДАТЫ (основная функция)
# ============================================

@bot.message_handler(func=lambda msg: '.' in msg.text and len(msg.text) == 10)
def handle_date_input(message):
    """Обработка ввода даты"""
    user_text = message.text.strip()
    print(f"📨 Дата от {message.chat.id}: {user_text}")
    
    try:
        # Рассчитываем матрицу
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
        
        # Сохраняем в базу
        try:
            save_calculation(message.chat.id, user_text, result)
            save_stat(message.chat.id, 'calculation_saved')
        except Exception as e:
            print(f"⚠️ Ошибка сохранения: {e}")
        
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
    """Показывает результат расчета"""
    m = result['matrix']
    
    # Красивое отображение матрицы
    matrix_display = f"""
┌──────┬──────┬──────┐
│  {m[1]}   │  {m[4]}   │  {m[7]}   │
├──────┼──────┼──────┤
│  {m[2]}   │  {m[5]}   │  {m[8]}   │
├──────┼──────┼──────┤
│  {m[3]}   │  {m[6]}   │  {m[9]}   │
└──────┴──────┴──────┘
"""
    
    # Базовый результат
    response = f"""
✅ *Расчет готов!*

📅 *Дата:* {result['date']}

{matrix_display}
*Цифры матрицы:*
1️⃣ Характер: {m[1]} ({result.get('interpretations', {}).get(1, '')})
2️⃣ Энергия: {m[2]} ({result.get('interpretations', {}).get(2, '')})
3️⃣ Интерес: {m[3]} ({result.get('interpretations', {}).get(3, '')})
4️⃣ Здоровье: {m[4]} ({result.get('interpretations', {}).get(4, '')})
5️⃣ Логика: {m[5]} ({result.get('interpretations', {}).get(5, '')})
6️⃣ Труд: {m[6]} ({result.get('interpretations', {}).get(6, '')})
7️⃣ Удача: {m[7]} ({result.get('interpretations', {}).get(7, '')})
8️⃣ Долг: {m[8]} ({result.get('interpretations', {}).get(8, '')})
9️⃣ Память: {m[9]} ({result.get('interpretations', {}).get(9, '')})

🔢 *Рабочие числа:*
РЧ1 = {result['work_numbers'][0]}
РЧ2 = {result['work_numbers'][1]}
РЧ3 = {result['work_numbers'][2]}
РЧ4 = {result['work_numbers'][3]}

💡 Используйте кнопку *🔮 Анализ* для детального разбора!
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
        calculations = get_user_calculations(chat_id, limit=5)
        
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
                matrix_summary = f"{matrix.get(1,0)}{matrix.get(2,0)}{matrix.get(3,0)}-{matrix.get(4,0)}{matrix.get(5,0)}{matrix.get(6,0)}-{matrix.get(7,0)}{matrix.get(8,0)}{matrix.get(9,0)}"
            else:
                matrix_summary = "нет данных"
            
            history_text += f"*{i}. {calc['birthdate']}*\n"
            history_text += f"   🆔 #{calc.get('id', '?')}\n"
            history_text += f"   🧮 {matrix_summary}\n"
            
            if calc.get('created_at'):
                history_text += f"   📅 {calc['created_at'][:10]}\n"
            
            history_text += "\n"
        
        history_text += "Для повтора отправьте дату заново или нажмите *🔮 Анализ* для детального разбора."
        
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
    """Полный детальный анализ"""
    print(f"🔮 Анализ запрошен {chat_id}")
    
    try:
        # Получаем последний расчет
        calculations = get_user_calculations(chat_id, limit=1)
        
        if not calculations:
            bot.send_message(
                chat_id,
                "📭 *Сначала сделайте расчет!*\n\n"
                "У вас нет сохраненных расчетов.\n"
                "Отправьте дату рождения (например: 15.08.1994)",
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
            return
        
        # Берем последний расчет
        last_calc = calculations[0]
        matrix_data = last_calc['matrix_data']
        
        # Проверяем есть ли детальный анализ
        analysis_data = matrix_data.get('analysis')
        
        if not analysis_data:
            bot.send_message(
                chat_id,
                "🔄 *Анализ недоступен*\n\n"
                "Сделайте новый расчет для получения детального анализа.",
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
            return
        
        # Отправляем заголовок
        bot.send_message(
            chat_id,
            f"🔮 *ДЕТАЛЬНЫЙ АНАЛИЗ МАТРИЦЫ*\n"
            f"📅 Дата: {last_calc['birthdate']}\n"
            "=" * 30,
            parse_mode='Markdown'
        )
        
        # Отправляем анализ по частям
        if analysis_data.get('has_detailed_analysis') and 'report_messages' in analysis_data:
            # Детальный анализ из analysis.py
            for i, msg in enumerate(analysis_data['report_messages'], 1):
                try:
                    bot.send_message(
                        chat_id,
                        msg,
                        parse_mode='Markdown'
                    )
                    if i < len(analysis_data['report_messages']):
                        time.sleep(1)
                except Exception as e:
                    print(f"❌ Ошибка отправки части {i}: {e}")
                    continue
        else:
            # Базовый анализ
            if 'report_messages' in analysis_data:
                for msg in analysis_data['report_messages']:
                    bot.send_message(chat_id, msg, parse_mode='Markdown')
            else:
                # Резервный вариант
                matrix = matrix_data.get('matrix', {})
                strongest = max(matrix.items(), key=lambda x: x[1]) if matrix else (0, 0)
                
                analysis_text = f"""
📊 *АНАЛИЗ МАТРИЦЫ*

💪 *Самая сильная цифра:* {strongest[0]}
🔢 Встречается {strongest[1]} раз

🎯 *Что это значит:*
• Цифра 1 - сила характера
• Цифра 2 - уровень энергии  
• Цифра 3 - таланты и интересы
• Цифра 4 - здоровье
• Цифра 5 - логика
• Цифра 6 - отношение к труду
• Цифра 7 - удача
• Цифра 8 - чувство долга
• Цифра 9 - память

✨ *Совет:* Развивайте все аспекты своей личности!
"""
                bot.send_message(chat_id, analysis_text, parse_mode='Markdown')
        
        # Финальное сообщение
        bot.send_message(
            chat_id,
            "✨ *Анализ завершен!*\n\n"
            "Сохраните эти рекомендации.\n"
            "Для нового анализа сделайте расчет другой даты.",
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
# ОБРАБОТЧИК ДАННЫХ ИЗ MINI APP
# ============================================

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app(message):
    """Обработка данных из Mini App и отправка ответа"""
    try:
        data = message.web_app_data.data
        print(f"📲 WebApp data: {data}")
        
        # Пробуем распарсить JSON
        try:
            json_data = json.loads(data)
            birthdate = json_data.get('birthdate', data)
        except:
            birthdate = data
        
        print(f"📅 Дата для расчета: {birthdate}")
        
        # Рассчитываем матрицу
        result = calculate_matrix(birthdate)
        
        if result['success']:
            # Отправляем результат обратно в Mini App
            bot.send_message(
                message.chat.id,
                json.dumps(result, ensure_ascii=False),
                reply_to_message_id=message.message_id
            )
            print("✅ Результат отправлен обратно в Mini App")
        else:
            bot.send_message(
                message.chat.id,
                json.dumps({'error': 'Неверная дата'}),
                reply_to_message_id=message.message_id
            )
                
    except Exception as e:
        print(f"❌ Ошибка WebApp: {e}")
        import traceback
        traceback.print_exc()

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
    # Запускаем безопасно
    run_bot_safe()