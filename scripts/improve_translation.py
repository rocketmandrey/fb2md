#!/usr/bin/env python3
"""
Скрипт для улучшения перевода книги по блокам с использованием AI.
"""

import anthropic
import os
from pathlib import Path

# Настройка клиента Anthropic
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def improve_text_block(text: str) -> str:
    """Улучшает блок текста с помощью Claude."""

    prompt = f"""Ты профессиональный литературный переводчик и редактор. Перед тобой русский перевод книги о коучинге и саморазвитии. Перевод сделан машинно и имеет много проблем.

ТВОЯ ЗАДАЧА: Улучшить перевод, сделать его естественным, живым и профессиональным.

ПРОБЛЕМЫ ТЕКУЩЕГО ПЕРЕВОДА:
- Кальки с японского/английского ("линия продолжения прошлого", "комфортная зона")
- Неестественные конструкции
- Грамматические ошибки
- Плохая читабельность

ЧТО НУЖНО СДЕЛАТЬ:
1. Исправить все грамматические и стилистические ошибки
2. Заменить кальки на естественные русские выражения
3. Улучшить структуру предложений для лучшей читабельности
4. Сохранить все технические термины (RAS, скотома, аффирмация, гештальт и т.д.)
5. Сохранить структуру markdown (заголовки ##, жирный текст **текст**)
6. НЕ добавлять ничего от себя - только улучшать то, что есть

ВАЖНО:
- Сохраняй смысл и содержание
- Делай текст живым и кайфовым для чтения
- Используй современный русский язык

ТЕКСТ ДЛЯ УЛУЧШЕНИЯ:

{text}

---

Верни ТОЛЬКО улучшенный текст, без комментариев и пояснений."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def process_file(input_file: str, output_file: str, start_line: int = 188, chunk_size: int = 50):
    """Обрабатывает файл блоками."""

    print(f"Читаю файл: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Всего строк: {total_lines}")
    print(f"Начинаю с строки: {start_line}")

    # Копируем начало файла (уже обработанное)
    improved_lines = lines[:start_line]

    # Обрабатываем остаток файла блоками
    current_line = start_line

    while current_line < total_lines:
        end_line = min(current_line + chunk_size, total_lines)
        block = ''.join(lines[current_line:end_line])

        print(f"\nОбрабатываю строки {current_line+1}-{end_line}/{total_lines}...")

        try:
            improved_block = improve_text_block(block)
            improved_lines.append(improved_block)
            if not improved_block.endswith('\n'):
                improved_lines.append('\n')

            print(f"✓ Блок улучшен")
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            print("Оставляю оригинальный текст")
            improved_lines.extend(lines[current_line:end_line])

        current_line = end_line

    # Записываем результат
    print(f"\nЗаписываю результат в: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(improved_lines)

    print("✓ Готово!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Improve translation using Claude')
    parser.add_argument('file', nargs='?', default='markdown/DreamFormulaRussian - Tomabechi.md', help='Input file path')
    parser.add_argument('--start', type=int, default=188, help='Start line number')
    args = parser.parse_args()

    input_file = args.file
    output_file = input_file  # Overwrite same file

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        exit(1)

    # Начинаем со строки args.start
    process_file(input_file, output_file, start_line=args.start, chunk_size=50)
