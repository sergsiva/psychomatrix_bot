"""Модуль детального анализа психоматрицы"""

def generate_telegram_report(matrix, birthdate):
    """Генерирует отчет для Telegram"""
    # Пока упрощенная версия
    total_digits = sum(matrix.values())
    strongest = max(matrix.items(), key=lambda x: x[1]) if matrix else (0, 0)
    
    reports = [
        f"🔮 *ДЕТАЛЬНЫЙ АНАЛИЗ МАТРИЦЫ*\n📅 Дата: {birthdate}\n",
        f"📊 *СТАТИСТИКА:*\n• Всего цифр: {total_digits}\n• Сильнейшая цифра: {strongest[0]} (встречается {strongest[1]} раз)",
        f"🎭 *ХАРАКТЕР (цифра 1):* {matrix.get(1, 0)}\nЭта цифра показывает силу вашего характера и лидерские качества.",
        f"⚡ *ЭНЕРГИЯ (цифра 2):* {matrix.get(2, 0)}\nУровень вашей жизненной энергии и эмоциональной силы.",
        f"💡 *СОВЕТ:* Работайте над своими слабыми сторонами и развивайте сильные!"
    ]
    
    return reports