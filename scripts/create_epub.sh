#!/bin/bash

# Скрипт для создания EPUB из улучшенного Markdown файла

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Создание EPUB из Markdown ===${NC}\n"

# Пути к файлам
INPUT_MD="markdown/DreamFormulaRussian - Tomabechi.md"
OUTPUT_EPUB="epub/DreamFormulaRussian - Tomabechi.epub"
METADATA_FILE="metadata.yaml"

# Создаём директорию для EPUB если её нет
mkdir -p epub

# Проверяем наличие pandoc
if ! command -v pandoc &> /dev/null; then
    echo -e "${RED}Ошибка: pandoc не установлен${NC}"
    echo -e "${BLUE}Устанавливаю pandoc через Homebrew...${NC}"
    brew install pandoc
    if [ $? -ne 0 ]; then
        echo -e "${RED}Не удалось установить pandoc. Установите вручную:${NC}"
        echo "brew install pandoc"
        exit 1
    fi
fi

# Создаём файл метаданных
echo -e "${BLUE}Создаю метаданные для книги...${NC}"
cat > "$METADATA_FILE" <<EOF
---
title: "Уравнение, осуществляющее мечты"
author: "Хидэто Томабэчи"
lang: ru
rights: © Хидэто Томабэчи
description: |
  Программа TPIE (Tice Principle in Excellence) - революционная методика
  саморазвития, созданная на основе новейших исследований в нейронауке
  и когнитивной психологии.
---
EOF

# Конвертируем Markdown в EPUB
echo -e "${BLUE}Конвертирую Markdown в EPUB...${NC}"
pandoc "$INPUT_MD" \
    --metadata-file="$METADATA_FILE" \
    --from markdown \
    --to epub3 \
    --toc \
    --toc-depth=2 \
    --split-level=3 \
    --output "$OUTPUT_EPUB"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Успешно создан EPUB файл:${NC}"
    echo -e "${GREEN}  $OUTPUT_EPUB${NC}"

    # Показываем размер файла
    FILE_SIZE=$(ls -lh "$OUTPUT_EPUB" | awk '{print $5}')
    echo -e "${BLUE}  Размер: $FILE_SIZE${NC}\n"

    # Удаляем временный файл метаданных
    rm -f "$METADATA_FILE"

    echo -e "${GREEN}Готово!${NC}"
else
    echo -e "\n${RED}✗ Ошибка при создании EPUB${NC}"
    exit 1
fi
