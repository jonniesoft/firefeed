#!/usr/bin/env python3
"""
Скрипт для применения codemod трансформаций к FireFeed проекту.
Автоматизированное применение безопасных рефакторингов.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """
    Запускает команду и возвращает True при успехе.

    Args:
        cmd: Команда для выполнения
        description: Описание для логирования

    Returns:
        True если команда выполнена успешно, False иначе
    """
    print(f"\n🔧 {description}...")
    print(f"   Команда: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.stdout:
            print(f"   stdout: {result.stdout[:200]}")

        if result.stderr:
            print(f"   stderr: {result.stderr[:200]}")

        if result.returncode == 0:
            print("   ✅ Успешно")
            return True
        else:
            print(f"   ❌ Ошибка (код: {result.returncode})")
            return False

    except Exception as e:
        print(f"   ❌ Исключение: {e}")
        return False


def apply_codemods(directory: str = ".") -> bool:
    """
    Применяет безопасные codemod трансформации.

    Args:
        directory: Директория для обработки

    Returns:
        True если все операции успешны
    """
    print("=" * 70)
    print("🚀 Применение codemod трансформаций")
    print("=" * 70)

    all_success = True

    # 1. Удаление неиспользуемых импортов
    success = run_command(
        ["uv", "run", "codemod", "remove_unused_imports", "--verbose", directory],
        "Удаление неиспользуемых импортов",
    )
    all_success = all_success and success

    # 2. Обновление до Python 3.11+ синтаксиса
    success = run_command(
        ["uv", "run", "codemod", "python/py311-plus", directory],
        "Обновление до Python 3.11+ синтаксиса",
    )
    all_success = all_success and success

    # 3. Исправление unsafe overrides (с предварительным diff)
    print("\n" + "=" * 70)
    print("⚠️  unsafe-overrides требует ручной проверки")
    print("=" * 70)
    print("Выполните вручную для предварительного просмотра:")
    print("  uv run codemod mypy/unsafe-overrides --diff .")
    print("Затем примените при необходимости:")
    print("  uv run codemod mypy/unsafe-overrides .")

    return all_success


def create_pycodespell_config():
    """Создает конфигурацию для pycodespell."""
    config_content = """# Конфигурация pycodespell для FireFeed
# Игнорируем технические термины и доменные слова

ignore-words-list = \
    alse,ba,falt,focu,nd,parm,parms,ro,te,vertexes,wa,hist,coo,\
    ot,synopsys,creat,nin,som,acount,opend,programatically,\
    bu,specfic,hel,adress,creat,attribues,incude,semver,\
    alidation,ttribute,ons,bu,locu,mut,attribut

skip = \
    *.git,\
    *.pyc,\
    __pycache__,\
    .venv,\
    .pytest_cache,\
    .ruff_cache,\
    node_modules,\
    build,\
    dist,\
    *.egg-info,\
    migrations
"""
    config_path = Path(".pycodespellignore")
    with config_path.open("w", encoding="utf-8") as f:
        f.write(config_content)
    print(f"\n📝 Создан файл конфигурации: {config_path}")


def main():
    """Главная функция."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Применяет codemod трансформации к FireFeed проекту"
    )
    parser.add_argument(
        "directory", nargs="?", default=".", help="Директория для обработки (по умолчанию текущая)"
    )
    parser.add_argument(
        "--with-spellcheck", action="store_true", help="Также запустить проверку орфографии кода"
    )

    args = parser.parse_args()

    # Применяем codemods
    success = apply_codemods(args.directory)

    # Дополнительные опции
    if args.with_spellcheck:
        print("\n" + "=" * 70)
        print("🔍 Проверка орфографии кода")
        print("=" * 70)
        create_pycodespell_config()
        run_command(["uv", "run", "pycodespell", args.directory], "Проверка орфографии в коде")

    # Итоговый отчет
    print("\n" + "=" * 70)
    if success:
        print("✅ Все codemod операции выполнены успешно!")
    else:
        print("⚠️ Некоторые операции завершились с ошибками")
    print("=" * 70)

    # Предлагаем следующие шаги
    print("\n📋 Следующие шаги:")
    print("   1. Проверьте изменения: git diff")
    print("   2. Запустите тесты: uv run pytest")
    print("   3. Проверьте типы: uv run pyrefly check")
    print("   4. Проверьте стиль: uv run ruff check .")
    print("   5. Зафиксируйте изменения: git add . && git commit")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
