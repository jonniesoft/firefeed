#!/bin/bash
################################################################################
# Скрипт проверки качества кода для FireFeed проекта
# Генерирует структурированные отчеты в папку report/
################################################################################

# Не используем set -e, т.к. скрипт должен продолжать работу при ошибках проверок

# Константы
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="$PROJECT_ROOT/report"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_STR=$(date +"%Y-%m-%d %H:%M:%S")

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода заголовков
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Функция для вывода статуса
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Функция анализа детальных ошибок
analyze_errors() {
    local tool_name=$1
    local output_file=$2
    local tool_command=$3

    echo ""
    echo "================================================================================"
    echo "ДЕТАЛЬНЫЙ АНАЛИЗ ОШИБОК:"
    echo "================================================================================"
    echo ""

    case $tool_name in
        "Ruff")
            if grep -q "Found" "$output_file"; then
                local total=$(grep "Found" "$output_file" | grep -oE '[0-9]+' | head -1)
                echo "📊 Найдено ошибок: $total"
                echo ""
                echo "📄 Детальный список: ruff_errors_${TIMESTAMP}.txt"
            else
                echo "✅ Ошибок не найдено"
            fi
            ;;
        "Pyrefly")
            if grep -qi "errors" "$output_file" && ! grep -qi "0 errors" "$output_file"; then
                local error_count=$(grep -oE '[0-9]+ errors?' "$output_file" | head -1 | grep -oE '[0-9]+' || echo "0")
                echo "📊 Найдено ошибок: $error_count"
                echo ""
                echo "📄 Детальный список: pyrefly_errors_${TIMESTAMP}.txt"
            else
                echo "✅ Ошибок типов не найдено"
            fi
            ;;
        "Pytest")
            if grep -qi "failed" "$output_file"; then
                local passed=$(grep -oE '[0-9]+ passed' "$output_file" | head -1 || echo "0")
                local failed=$(grep -oE '[0-9]+ failed' "$output_file" | head -1 || echo "0")
                local skipped=$(grep -oE '[0-9]+ skipped' "$output_file" | head -1 || echo "0")

                echo "📊 Результаты: $passed прошло, $failed провалено, $skipped пропущено"

                # Список неудачных тестов
                echo "📋 Неудачные тесты:"
                grep -E "^FAILED\s+" "$output_file" | head -10 | while read -r line; do
                    echo "  - $line"
                done
            else
                echo "✅ Все тесты прошли успешно"
            fi
            ;;
        "Usort")
            if grep -qi "would" "$output_file"; then
                local file_count=$(grep -c "would" "$output_file" || echo "0")
                echo "📊 Найдено файлов с проблемами: $file_count"
                echo ""
                echo "📋 Список файлов:"
                grep "would" "$output_file" | sed 's/^Would re-sort: /  /' | head -10
            else
                echo "✅ Импорты корректно отсортированы"
            fi
            ;;
    esac
}

# Функция запуска инструмента
run_tool() {
    local tool_name=$1
    local command=$2
    local output_file=$3
    local error_pattern=$4

    print_header "🔍 Проверка: $tool_name"

    echo "Команда: $command"
    echo "Файл отчета: $output_file"
    echo ""

    # Запускаем команду и сохраняем вывод
    mkdir -p "$REPORT_DIR"
    {
        echo "================================================================================"
        echo "$tool_name - Отчет о проверке"
        echo "Дата и время: $DATE_STR"
        echo "================================================================================"
        echo ""
        echo "Команда: $command"
        echo ""
        echo "================================================================================"
        echo "ВЫВОД:"
        echo "================================================================================"
        echo ""

        # Выполняем команду
        cd "$PROJECT_ROOT"
        eval "$command" 2>&1 || true

        # Добавляем детальный анализ ошибок
        analyze_errors "$tool_name" "$output_file" "$command"

        echo "================================================================================"
        echo "Конец отчета"
        echo "================================================================================"
    } > "$output_file" 2>&1

    # Анализируем результат
    local exit_code=0
    local error_count=0

    # Подсчитываем ошибки
    error_count=$(grep -ic "$error_pattern" "$output_file" || true)

    # Особая логика для разных инструментов
    case $tool_name in
        "Ruff")
            # Проверяем наличие ошибок в статистике
            if grep -q "Found" "$output_file"; then
                error_count=$(grep "Found" "$output_file" | grep -oE '[0-9]+' | head -1 || echo "0")
            fi
            ;;
        "Pytest")
            # Извлекаем количество passed/failed из summary
            local passed=$(grep -oE '[0-9]+ passed' "$output_file" | grep -oE '[0-9]+' | head -1 || echo "0")
            local failed=$(grep -oE '[0-9]+ failed' "$output_file" | grep -oE '[0-9]+' | head -1 || echo "0")
            echo ""
            echo "Результаты: $passed прошло, $failed не прошло"

            if [ "$failed" -gt 0 ]; then
                exit_code=1
            fi
            ;;
    esac

    # Выводим результаты
    echo ""
    if [ $exit_code -eq 0 ] && [ "$error_count" -eq 0 ]; then
        print_status 0 "Успешно: ошибок не найдено"
    else
        print_status 1 "Найдено ошибок: $error_count"
    fi

    echo ""
    echo "Полный отчет сохранен: $output_file"
    echo ""

    return $exit_code
}

# Генерация итогового отчета
generate_summary() {
    local summary_file="$REPORT_DIR/summary_${TIMESTAMP}.txt"
    local tools_count=0
    local success_count=0
    local failed_count=0

    print_header "📊 Генерация итогового отчета"

    {
        echo "================================================================================"
        echo "ИТОГОВЫЙ ОТЧЕТ О КАЧЕСТВЕ КОДА"
        echo "================================================================================"
        echo ""
        echo "Дата и время проверки: $DATE_STR"
        echo "Папка отчетов: $REPORT_DIR"
        echo ""

        echo "--------------------------------------------------------------------------------"
        echo "СТАТУС ПО ИНСТРУМЕНТАМ:"
        echo "--------------------------------------------------------------------------------"
        echo ""

        # Проверяем каждый отчет
        for report_file in "$REPORT_DIR"/{ruff,pyrefly,pytest,usort}_${TIMESTAMP}.txt; do
            if [ -f "$report_file" ]; then
                local tool_name=$(head -1 "$report_file" | sed 's/ - Отчет о проверке//')
                local status="УСПЕШНО"

                # Определяем статус по содержимому
                if grep -qi "error" "$report_file" | head -1; then
                    status="ОШИБКИ"
                fi

                if grep -qi "passed" "$report_file"; then
                    local passed=$(grep -oE '[0-9]+ passed' "$report_file" | head -1)
                    local failed=$(grep -oE '[0-9]+ failed' "$report_file" | head -1)

                    if [ -n "$failed" ]; then
                        status="ОШИБКИ"
                        echo "❌ $tool_name: $failed не прошло, $passed прошло"
                        ((failed_count++))
                    else
                        echo "✅ $tool_name: $passed прошло"
                        ((success_count++))
                    fi
                else
                    if echo "$status" | grep -qi "ошибки"; then
                        echo "❌ $tool_name: найдены ошибки"
                        ((failed_count++))
                    else
                        echo "✅ $tool_name: успешно"
                        ((success_count++))
                    fi
                fi

                echo "   Файл: $(basename "$report_file")"
                echo ""
                ((tools_count++))
            fi
        done

        echo "--------------------------------------------------------------------------------"
        echo "ОБЩАЯ СТАТИСТИКА:"
        echo "--------------------------------------------------------------------------------"
        echo ""
        echo "Всего проверено инструментов: $tools_count"
        echo "Успешных проверок: $success_count"
        echo "Неудачных проверок: $failed_count"

        if [ $tools_count -gt 0 ]; then
            local success_percent=$((success_count * 100 / tools_count))
            echo "Процент успеха: $success_percent%"
        fi

        echo ""

        if [ $failed_count -gt 0 ]; then
            echo "--------------------------------------------------------------------------------"
            echo "ТРЕБУЕТСЯ ВНИМАНИЕ:"
            echo "--------------------------------------------------------------------------------"
            echo ""
            echo "Следующие инструменты обнаружили проблемы:"
            echo "Детальная информация в соответствующих отчетах."
            echo ""
        fi

        echo "================================================================================"
        echo "Конец отчета"
        echo "================================================================================"
    } > "$summary_file"

    echo "✅ Итоговый отчет: $summary_file"
    echo ""

    # Выводим краткую сводку
    print_header "📊 КРАТКАЯ СВОДКА"

    for report_file in "$REPORT_DIR"/{ruff,pyrefly,pytest,usort}_${TIMESTAMP}.txt; do
        if [ -f "$report_file" ]; then
            local tool_name=$(head -1 "$report_file" | sed 's/ - Отчет о проверке//')

            if grep -qi "error" "$report_file" | head -1; then
                echo -e "${RED}❌ $tool_name${NC}"
            else
                echo -e "${GREEN}✅ $tool_name${NC}"
            fi
        fi
    done

    echo ""
    echo -e "${GREEN}✅ Успешно: $success_count/$tools_count${NC}"
    echo -e "${BLUE}📁 Отчеты в: $REPORT_DIR${NC}"
    echo -e "${BLUE}📄 Итоговый отчет: $(basename "$summary_file")${NC}"
    echo ""

    return $failed_count
}

# Функция помощи
show_help() {
    cat << EOF
Скрипт проверки качества кода для FireFeed

Использование:
    $0 [опции]

Опции:
    --tools LIST     Список инструментов через запятую (ruff,pyrefly,pytest,usort)
                     По умолчанию: ruff,pyrefly,pytest,usort
    --output-dir DIR Папка для сохранения отчетов (по умолчанию: report)
    --help          Показать эту справку

Примеры:
    $0                           # Запуск всех проверок
    $0 --tools ruff,pyrefly     # Только linting и типизация
    $0 --output-dir my_reports  # Другой каталог для отчетов

Отчеты:
    Все отчеты сохраняются в папку report/ с префиксом по типу инструмента
    и временной меткой. Итоговый отчет содержит общую сводку по всем проверкам.
EOF
}

################################################################################
# Основная логика
################################################################################

# Парсим аргументы
TOOLS_LIST="ruff,pyrefly,pytest,usort"
OUTPUT_DIR="$REPORT_DIR"

while [[ $# -gt 0 ]]; do
    case $1 in
        --tools)
            TOOLS_LIST="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Неизвестная опция: $1"
            echo "Используйте --help для справки"
            exit 1
            ;;
    esac
done

# Заголовок
echo ""
print_header "🔍 ПРОВЕРКА КАЧЕСТВА КОДА - FireFeed"
echo "Дата и время: $DATE_STR"
echo "Инструменты: $TOOLS_LIST"
echo "Папка отчетов: $OUTPUT_DIR"
echo ""

# Проверяем наличие uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ Ошибка: uv не установлен${NC}"
    exit 1
fi

# Проверяем что мы в правильной директории
if [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
    echo -e "${RED}❌ Ошибка: файл pyproject.toml не найден в $PROJECT_ROOT${NC}"
    exit 1
fi

# Создаем папку для отчетов
mkdir -p "$OUTPUT_DIR"

# Счетчики
overall_exit_code=0
success_count=0
failed_count=0

# Запускаем проверки
IFS=',' read -ra TOOLS <<< "$TOOLS_LIST"
for tool in "${TOOLS[@]}"; do
    case $tool in
        ruff)
            run_tool "Ruff" \
                     "uv run ruff check . --statistics" \
                     "$OUTPUT_DIR/ruff_${TIMESTAMP}.txt" \
                     "error" || ((overall_exit_code++))

            # Создаем отдельный файл с чистым выводом ошибок
            echo "# Ruff - Список ошибок" > "$OUTPUT_DIR/ruff_errors_${TIMESTAMP}.txt"
            echo "# Формат: файл:строка:колонка - код ошибки - описание" >> "$OUTPUT_DIR/ruff_errors_${TIMESTAMP}.txt"
            echo "" >> "$OUTPUT_DIR/ruff_errors_${TIMESTAMP}.txt"
            uv run ruff check . 2>&1 | tee -a "$OUTPUT_DIR/ruff_errors_${TIMESTAMP}.txt" > /dev/null || true

            ((overall_exit_code > 0)) && ((failed_count++)) || ((success_count++))
            ;;
        pyrefly)
            run_tool "Pyrefly" \
                     "uv run pyrefly check" \
                     "$OUTPUT_DIR/pyrefly_${TIMESTAMP}.txt" \
                     "ERROR" || ((overall_exit_code++))

            # Создаем отдельный файл с чистым выводом ошибок
            echo "# Pyrefly - Список ошибок типов" > "$OUTPUT_DIR/pyrefly_errors_${TIMESTAMP}.txt"
            echo "# Формат: файл:строка - тип ошибки - описание" >> "$OUTPUT_DIR/pyrefly_errors_${TIMESTAMP}.txt"
            echo "" >> "$OUTPUT_DIR/pyrefly_errors_${TIMESTAMP}.txt"
            uv run pyrefly check 2>&1 | grep -E "^\s*\d+:\d+:" | sed 's/^\s*/  /' >> "$OUTPUT_DIR/pyrefly_errors_${TIMESTAMP}.txt" || echo "  Ошибок нет" >> "$OUTPUT_DIR/pyrefly_errors_${TIMESTAMP}.txt"

            ((overall_exit_code > 0)) && ((failed_count++)) || ((success_count++))
            ;;
        pytest)
            run_tool "Pytest" \
                     "uv run pytest -v --tb=short" \
                     "$OUTPUT_DIR/pytest_${TIMESTAMP}.txt" \
                     "FAILED" || ((overall_exit_code++))
            ((overall_exit_code > 0)) && ((failed_count++)) || ((success_count++))
            ;;
        usort)
            run_tool "Usort" \
                     "uv run usort check ." \
                     "$OUTPUT_DIR/usort_${TIMESTAMP}.txt" \
                     "Would" || ((overall_exit_code++))
            ((overall_exit_code > 0)) && ((failed_count++)) || ((success_count++))
            ;;
        *)
            echo -e "${YELLOW}⚠️  Неизвестный инструмент: $tool${NC}"
            ;;
    esac
done

# Генерируем итоговый отчет
generate_summary

# Финальный статус
if [ $overall_exit_code -eq 0 ]; then
    print_header "✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО"
    exit 0
else
    print_header "❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ"
    echo "Количество проверок с ошибками: $failed_count"
    echo "Подробности в отчетах: $OUTPUT_DIR"
    exit 1
fi
