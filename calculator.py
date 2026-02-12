"""Модуль расчета психоматрицы Пифагора"""

def calculate_matrix(birthdate):
    """Рассчитывает психоматрицу Пифагора по дате рождения"""
    try:
        # Разбиваем дату на части
        day, month, year = map(int, birthdate.split('.'))
        
        # Собираем все цифры даты
        digits = []
        for number in [day, month, year]:
            for digit in str(number):
                digits.append(int(digit))
        
        # Рабочие числа
        work1 = sum(digits)
        work2 = sum(int(d) for d in str(work1))
        first_digit_of_day = int(str(day)[0])
        work3 = work1 - 2 * first_digit_of_day
        work4 = sum(int(d) for d in str(work3))
        
        # Все цифры для подсчета
        all_digits = digits.copy()  # Используем .copy() чтобы не менять оригинал
        for num in [work1, work2, work3, work4]:
            for d in str(num):
                all_digits.append(int(d))
        
        # МАТРИЦА ВЕРТИКАЛЬНО (как нужно):
        # 1 4 7
        # 2 5 8
        # 3 6 9
        
        # Создаем матрицу с правильной нумерацией
        matrix = {}
        
        # Первый столбец: 1, 2, 3
        matrix[1] = all_digits.count(1)  # Характер
        matrix[2] = all_digits.count(2)  # Энергия
        matrix[3] = all_digits.count(3)  # Интерес
        
        # Второй столбец: 4, 5, 6
        matrix[4] = all_digits.count(4)  # Здоровье
        matrix[5] = all_digits.count(5)  # Логика
        matrix[6] = all_digits.count(6)  # Труд
        
        # Третий столбец: 7, 8, 9
        matrix[7] = all_digits.count(7)  # Удача
        matrix[8] = all_digits.count(8)  # Долг
        matrix[9] = all_digits.count(9)  # Память
        
        # Описания для цифр
        descriptions = {
            1: ["Слабый характер", "Эгоист", "Мягкий характер", "Уравновешенный", "Сильный характер", "Тиран"],
            2: ["Мало энергии", "Нормальная энергия", "Много энергии", "Очень много энергии"],
            3: ["Нет интересов", "1-2 интереса", "Разносторонний", "Очень разносторонний"],
            4: ["Слабое здоровье", "Нормальное", "Хорошее", "Отличное"],
            5: ["Интуиция", "Логика+интуиция", "Логика", "Сильная логика"],
            6: ["Не любит труд", "Нормально", "Трудолюбив", "Очень трудолюбив"],
            7: ["Невезучий", "Нормальная удача", "Везучий", "Очень везучий"],
            8: ["Безответственный", "Нормальный", "Ответственный", "Очень ответственный"],
            9: ["Слабая память", "Нормальная", "Хорошая", "Отличная"]
        }
        
        # Получаем описания для каждой цифры
        interpretations = {}
        for digit in range(1, 10):
            count = matrix[digit]
            if digit in descriptions and count < len(descriptions[digit]):
                interpretations[digit] = descriptions[digit][count]
            else:
                interpretations[digit] = "Особое значение"
        
        # Детальный анализ
        analysis_result = get_detailed_analysis(matrix, f"{day:02d}.{month:02d}.{year}")
        
        return {
            'success': True,
            'date': f"{day:02d}.{month:02d}.{year}",
            'work_numbers': [work1, work2, work3, work4],
            'matrix': matrix,
            'interpretations': interpretations,
            'analysis': analysis_result if analysis_result['success'] else None
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Неверный формат даты: {str(e)}'}


def get_detailed_analysis(matrix, birthdate):
    """Возвращает детальный анализ матрицы"""
    try:
        # Пробуем импортировать из analysis.py
        from analysis import generate_telegram_report
        
        # Генерируем отчет
        report_messages = generate_telegram_report(matrix, birthdate)
        
        return {
            'success': True,
            'report_messages': report_messages,
            'has_detailed_analysis': True
        }
    except ImportError:
        # Если analysis.py нет, используем упрощенную версию
        return get_basic_analysis(matrix)
    except Exception as e:
        print(f"❌ Ошибка в анализе: {e}")
        return get_basic_analysis(matrix)


def get_basic_analysis(matrix):
    """Базовая версия анализа (если нет analysis.py)"""
    # Определяем самые сильные и слабые цифры
    strongest_digit = max(matrix.items(), key=lambda x: x[1]) if matrix else (0, 0)
    weakest_digit = min(matrix.items(), key=lambda x: x[1]) if matrix else (0, 0)
    
    # Базовая интерпретация
    basic_interpretations = {
        1: "Характер и воля",
        2: "Энергия и эмоции", 
        3: "Интересы и таланты",
        4: "Здоровье и физика",
        5: "Логика и интуиция",
        6: "Труд и мастерство",
        7: "Удача и везение",
        8: "Долг и ответственность",
        9: "Память и интеллект"
    }
    
    strongest = basic_interpretations.get(strongest_digit[0], "Не определено")
    weakest = basic_interpretations.get(weakest_digit[0], "Не определено")
    
    return {
        'success': True,
        'report_messages': [
            f"📊 *БАЗОВЫЙ АНАЛИЗ МАТРИЦЫ*\n\n"
            f"💪 *Самая сильная цифра:* {strongest_digit[0]} ({strongest})\n"
            f"🔢 Количество: {strongest_digit[1]}\n\n"
            f"🌱 *Самая слабая цифра:* {weakest_digit[0]} ({weakest})\n"
            f"🔢 Количество: {weakest_digit[1]}\n\n"
            f"🎯 *Рекомендация:* Развивайте аспект '{weakest}'"
        ],
        'has_detailed_analysis': False,
        'basic_analysis': True
    }