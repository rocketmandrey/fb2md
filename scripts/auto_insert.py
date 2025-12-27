#!/usr/bin/env python3
"""
Автоматическая вставка картинок по номерам строк заголовков
"""

from pathlib import Path

# Маппинг: (файл, номер строки заголовка в ПЕРЕВОДЕ, картинка)
INSERTIONS = [
    # PT1 - вставляем ПЕРЕД заголовком
    ("book_ru/pt1_ru.md", 319, "![](image/bestinworld.png)"),  # Поймите, как создается богатство
    ("book_ru/pt1_ru.md", 519, "![](image/iterated_returns.png)"),  # Найдите и развивайте специфические знания
    ("book_ru/pt1_ru.md", 590, "![](image/intentions_actions.png)"),  # Играйте в долгосрочные игры
    ("book_ru/pt1_ru.md", 624, "![](image/allocation_knowledge.png)"),  # Принимайте на себя ответственность
    ("book_ru/pt1_ru.md", 648, "![](image/leverage_10000x.png)"),  # Создайте или купите долю в бизнесе
    ("book_ru/pt1_ru.md", 674, "![](image/earn_mind.png)"),  # Найдите точку приложения рычага
    ("book_ru/pt1_ru.md", 794, "![](image/iteration_repetition.png)"),  # Получайте плату за свое суждение

    # PT2
    ("book_ru/pt2_ru.md", 73, "![](image/optimist_contrarian.png)"),  # Как мыслить ясно
    ("book_ru/pt2_ru.md", 122, "![](image/tension_relaxation.png)"),  # Отбросьте свою личность
    ("book_ru/pt2_ru.md", 541, "![](image/desire_contract.png)"),  # Счастье требует покоя
    ("book_ru/pt2_ru.md", 763, "![](image/easy_choices.png)"),  # Находите счастье в принятии
    ("book_ru/pt2_ru.md", 848, "![](image/meditation_imf.png)"),  # Выбор заботиться о себе

    # PT3
    ("book_ru/pt3_ru.md", 129, "![](image/patience_results.png)"),  # Выбор строить себя
    ("book_ru/pt3_ru.md", 395, "![](image/inspiration_time.png)"),  # Настоящее — это все, что у нас есть
]

def insert_images():
    """Вставляет картинки в файлы"""

    # Группируем по файлам
    by_file = {}
    for filepath, line_num, image in INSERTIONS:
        if filepath not in by_file:
            by_file[filepath] = []
        by_file[filepath].append((line_num, image))

    # Сортируем по убыванию номеров строк (чтобы вставка не сбивала нумерацию)
    for filepath in by_file:
        by_file[filepath].sort(reverse=True, key=lambda x: x[0])

    # Вставляем
    for filepath, insertions in by_file.items():
        print(f"\n### {filepath} ###")

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, image in insertions:
            idx = line_num - 1  # 0-based index

            # Проверяем, нет ли уже картинки
            if idx > 0 and lines[idx-1].strip().startswith("!["):
                print(f"  ⊘ Line {line_num}: Image already exists, skipping")
                continue
            if idx > 1 and lines[idx-2].strip().startswith("!["):
                print(f"  ⊘ Line {line_num}: Image already exists, skipping")
                continue

            # Вставляем: пустая строка, картинка, пустая строка, затем заголовок
            lines.insert(idx, "\n")
            lines.insert(idx, image + "\n")
            lines.insert(idx, "\n")

            print(f"  ✓ Line {line_num}: Inserted {image}")

        # Сохраняем
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f"  → Saved {filepath}")

if __name__ == "__main__":
    print("=" * 60)
    print("AUTO IMAGE INSERTION")
    print("=" * 60)

    insert_images()

    print("\n" + "=" * 60)
    print("✓ DONE!")
    print("=" * 60)
    print("\nNOTE: QR codes in pt3 need manual insertion")
    print("They should go in the '# Книги' section where each book is mentioned")
