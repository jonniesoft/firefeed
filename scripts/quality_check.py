#!/usr/bin/env python3
"""
Скрипт проверки качества кода для FireFeed проекта.
Генерирует структурированные отчеты в папку report/.

Использование:
    python scripts/quality_check.py
    python scripts/quality_check.py --tools ruff,pyrefly,pytest
"""

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

# Константы
REPORT_DIR = Path("report")
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
DATE_STR = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Инструменты для проверки
TOOLS_CONFIG = {
    "ruff": {
        "name": "Ruff",
        "command": ["uv", "run", "ruff", "check", ".", "--statistics"],
        "output_file": REPORT_DIR / f"ruff_{TIMESTAMP}.txt",
        "success_marker": "Found",
        "error_patterns": ["ERROR", "error"],
    },
    "pyrefly": {
        "name": "Pyrefly",
        "command": ["uv", "run", "pyrefly", "check"],
        "output_file": REPORT_DIR / f"pyrefly_{TIMESTAMP}.txt",
        "success_marker": "INFO",
        "error_patterns": ["ERROR", "error"],
    },
    "pytest": {
        "name": "Pytest",
        "command": ["uv", "run", "pytest", "-v", "--tb=short"],
        "output_file": REPORT_DIR / f"pytest_{TIMESTAMP}.txt",
        "success_marker": "passed",
        "error_patterns": ["FAILED", "ERROR", "error"],
    },
    "usort": {
        "name": "Usort",
        "command": ["uv", "run", "usort", "check", "."],
        "output_file": REPORT_DIR / f"usort_{TIMESTAMP}.txt",
        "success_marker": "All",
        "error_patterns": ["Would", "ERROR", "error"],
    },
}


def run_tool(tool_key: str) -> tuple[int, str, str]:
    """Запускает инструмент и возвращает код возврата, stdout, stderr."""
    config = TOOLS_CONFIG[tool_key]
    print(f"🔍 Запуск {config['name']}...")

    try:
        result = subprocess.run(
            config["command"],
            capture_output=True,
            text=True,
            timeout=300,  # 5 минут таймаут
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Таймаут выполнения"
    except Exception as e:
        return 1, "", str(e)


def analyze_output(tool_key: str, stdout: str, stderr: str) -> dict:
    """Анализирует вывод инструмента и возвращает метрики."""
    config = TOOLS_CONFIG[tool_key]
    full_output = stdout + stderr

    # Подсчет ошибок
    error_count = 0
    warnings_count = 0

    for pattern in config.get("error_patterns", ["ERROR"]):
        error_count += full_output.lower().count(pattern.lower())

    # Для pytest считаем passed/failed
    if tool_key == "pytest":
        failed_match = re.search(r"(\d+)\s+failed", full_output, re.I)
        failed = int(failed_match.group(1)) if failed_match else 0
        error_count = failed

    # Для ruff статистика
    if tool_key == "ruff":
        stats_match = re.search(r"(\d+)\s+[A-Z0-9]+", full_output)
        if stats_match:
            error_count = int(stats_match.group(1))

    # Определяем статус
    is_success = error_count == 0 and tool_key not in ["pytest"]

    return {
        "tool": tool_key,
        "name": config["name"],
        "status": "SUCCESS" if is_success else "FAILED",
        "error_count": error_count,
        "warnings_count": warnings_count,
        "timestamp": DATE_STR,
    }


def save_report(tool_key: str, output: str, error: str, metrics: dict):
    """Сохраняет отчет в файл."""
    config = TOOLS_CONFIG[tool_key]
    report_file = config["output_file"]

    with report_file.open("w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"{config['name']} - Отчет о проверке\n")
        f.write(f"Дата и время: {DATE_STR}\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Статус: {metrics['status']}\n")
        f.write(f"Найдено ошибок: {metrics['error_count']}\n")
        f.write(f"Предупреждений: {metrics['warnings_count']}\n")
        f.write("\n" + "=" * 80 + "\n\n")

        if output:
            f.write("STDOUT:\n")
            f.write("-" * 80 + "\n")
            f.write(output)
            f.write("\n\n")

        if error:
            f.write("STDERR:\n")
            f.write("-" * 80 + "\n")
            f.write(error)
            f.write("\n\n")

        f.write("=" * 80 + "\n")
        f.write("Конец отчета\n")

    print(f"✅ Отчет сохранен: {report_file}")


def generate_summary(reports: list[dict]) -> Path:
    """Генерирует итоговый отчет."""
    summary_file = REPORT_DIR / f"summary_{TIMESTAMP}.txt"

    with summary_file.open("w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("ИТОГОВЫЙ ОТЧЕТ О КАЧЕСТВЕ КОДА\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Дата и время проверки: {DATE_STR}\n")
        f.write(f"Количество проверенных инструментов: {len(reports)}\n\n")

        f.write("-" * 80 + "\n")
        f.write("СТАТУС ПО ИНСТРУМЕНТАМ:\n")
        f.write("-" * 80 + "\n\n")

        for report in reports:
            status_icon = "✅" if report["status"] == "SUCCESS" else "❌"
            f.write(f"{status_icon} {report['name']}\n")
            f.write(f"   Статус: {report['status']}\n")
            f.write(f"   Ошибок: {report['error_count']}\n")
            f.write(f"   Файл отчета: {TOOLS_CONFIG[report['tool']]['output_file'].name}\n")
            f.write("\n")

        f.write("-" * 80 + "\n")
        f.write("ОБЩАЯ СТАТИСТИКА:\n")
        f.write("-" * 80 + "\n\n")

        success_count = sum(1 for r in reports if r["status"] == "SUCCESS")
        failed_count = len(reports) - success_count

        f.write(f"Успешных проверок: {success_count}/{len(reports)}\n")
        f.write(f"Неудачных проверок: {failed_count}/{len(reports)}\n")
        f.write(f"Процент успеха: {(success_count/len(reports)*100):.1f}%\n")
        f.write("\n")

        if failed_count > 0:
            f.write("-" * 80 + "\n")
            f.write("ТРЕБУЕТСЯ ВНИМАНИЕ:\n")
            f.write("-" * 80 + "\n\n")

            for report in reports:
                if report["status"] != "SUCCESS":
                    tool_config = TOOLS_CONFIG[report["tool"]]
                    f.write(f"❌ {report['name']}: {report['error_count']} ошибок\n")
                    f.write(f"   Детали: {tool_config['output_file'].name}\n")
                    f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("Конец отчета\n")

    print(f"✅ Итоговый отчет: {summary_file}")
    return summary_file


def main():
    parser = argparse.ArgumentParser(
        description="Проверка качества кода с генерацией отчетов"
    )
    parser.add_argument(
        "--tools",
        help="Список инструментов через запятую (ruff,pyrefly,pytest,usort)",
        default="ruff,pyrefly,pytest",
    )
    parser.add_argument(
        "--output-dir",
        help="Папка для сохранения отчетов",
        default="report",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Создать только итоговый отчет",
    )

    args = parser.parse_args()

    # Создаем папку для отчетов
    global REPORT_DIR
    REPORT_DIR = Path(args.output_dir)
    REPORT_DIR.mkdir(exist_ok=True)

    # Парсим список инструментов
    tools = [t.strip() for t in args.tools.split(",")]

    print("\n" + "=" * 80)
    print("🔍 ПРОВЕРКА КАЧЕСТВА КОДА - FireFeed")
    print("=" * 80)
    print(f"Дата и время: {DATE_STR}")
    print(f"Инструменты: {', '.join(tools)}")
    print(f"Папка отчетов: {REPORT_DIR}")
    print("=" * 80 + "\n")

    reports = []

    for tool_key in tools:
        if tool_key not in TOOLS_CONFIG:
            print(f"⚠️  Неизвестный инструмент: {tool_key}")
            continue

        # Запускаем инструмент
        _, stdout, stderr = run_tool(tool_key)

        # Анализируем результат
        metrics = analyze_output(tool_key, stdout, stderr)

        # Сохраняем отчет
        save_report(tool_key, stdout, stderr, metrics)

        # Добавляем в итоговый отчет
        reports.append(metrics)

        print()

    # Генерируем итоговый отчет
    summary_file = generate_summary(reports)

    # Выводим краткую сводку
    print("\n" + "=" * 80)
    print("📊 КРАТКАЯ СВОДКА")
    print("=" * 80)

    for report in reports:
        status_icon = "✅" if report["status"] == "SUCCESS" else "❌"
        print(f"{status_icon} {report['name']}: {report['error_count']} ошибок")

    success_count = sum(1 for r in reports if r["status"] == "SUCCESS")
    print(f"\n✅ Успешно: {success_count}/{len(reports)}")
    print(f"📁 Подробные отчеты в: {REPORT_DIR}")
    print(f"📄 Итоговый отчет: {summary_file.name}")
    print("=" * 80 + "\n")

    # Возвращаем код ошибки если есть неудачи
    if any(r["status"] != "SUCCESS" for r in reports):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
