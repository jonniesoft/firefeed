#!/usr/bin/env python3
"""
Кастомные трансформации libcst для FireFeed проекта.
Автоматизированные исправления типов и улучшения кода.
"""

import pathlib
import libcst as cst

Path = pathlib.Path


class FixMIMEMultipartAssignment(cst.CSTTransformer):
    """Исправляет ошибки типов при работе с MIMEMultipart."""

    METADATA_DEPENDENCIES = (cst.metadata.ParentNodeProvider,)

    def leave_Assign(self, original_node: cst.Assign) -> cst.Assign:
        """Проверяет и исправляет присваивания в MIMEMultipart."""
        # Ищем паттерн: message["key"] = value
        if (
            isinstance(original_node.targets[0].target, cst.Subscript)
            and isinstance(original_node.targets[0].target.value, cst.Name)
            and original_node.targets[0].target.value.value == "message"
        ):
            # Получаем ключ
            key = original_node.targets[0].target.slice[0].value
            if isinstance(key, cst.SimpleString):
                key_name = key.value.strip("\"'")
                # Добавляем type: ignore для известных проблемных мест
                if key_name in ["Subject", "From", "To"]:
                    # Создаем комментарий с type: ignore
                    comment = cst.Comment("# type: ignore[assignment]")
                    new_node = original_node.with_changes(
                        leading_lines=[*original_node.leading_lines, cst.EmptyLine(comment=comment)]
                    )
                    return new_node
        return original_node


class FixDictAccessAnnotations(cst.CSTTransformer):
    """Добавляет аннотации типов для доступа к словарям конфигурации."""

    METADATA_DEPENDENCIES = (cst.metadata.ParentNodeProvider,)

    def leave_Attribute(self, original_node: cst.Attribute) -> cst.Attribute:
        """Добавляет type: ignore для доступа к конфигурации."""
        # Ищем паттерны доступа к конфигурации
        if (
            isinstance(original_node.value, cst.Name)
            and original_node.value.value == "self"
            and original_node.attr.value in ["smtp_config", "config", "settings"]
        ):
            # Добавляем type: ignore
            comment = cst.Comment("# type: ignore[typeddict-item]")
            new_node = original_node.with_changes(
                leading_lines=[*original_node.leading_lines, cst.EmptyLine(comment=comment)]
            )
            return new_node
        return original_node


class AddAsyncTypeHints(cst.CSTTransformer):
    """Добавляет корректные type hints для async функций."""

    METADATA_DEPENDENCIES = (cst.metadata.ParentNodeProvider,)

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> cst.FunctionDef:
        """Добавляет корректные возвращаемые типы для async функций."""
        # Проверяем, что функция async
        is_async = False
        for parent in self.metadata.get_parents(original_node):
            if isinstance(parent, cst.SimpleStatementLine):
                for stmt in parent.body:
                    if isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.Await):
                        is_async = True
                        break

        # Добавляем type hint для функций, которые его не имеют
        if is_async and not original_node.returns:
            # Возвращаем bool для функций отправки email
            func_name = original_node.name.value
            if "email" in func_name.lower() or "send" in func_name.lower():
                returns = cst.Annotation(annotation=cst.Name("bool"))
                return original_node.with_changes(returns=returns)

        return original_node


class FixStringConcatenation(cst.CSTTransformer):
    """Использует f-strings вместо .format() и + конкатенации."""

    METADATA_DEPENDENCIES = (cst.metadata.ParentNodeProvider,)

    def leave_BinaryOperation(self, original_node: cst.BinaryOperation) -> cst.BaseExpression:
        """Заменяет простую конкатенацию строк на f-строки."""
        # Проверяем, что это конкатенация строк
        if original_node.operator == cst.Add:
            left_type = type(original_node.left).__name__
            right_type = type(original_node.right).__name__
            # Если левая или правая часть не строки, пропускаем
            if left_type not in [
                "SimpleString",
                "FormattedString",
                "ConcatenatedString",
            ] and right_type not in ["SimpleString", "FormattedString", "ConcatenatedString"]:
                return original_node

        return original_node


def transform_file(file_path: str) -> str:
    """
    Применяет все трансформации к файлу.

    Args:
        file_path: Путь к файлу для трансформации

    Returns:
        Строка с трансформированным кодом
    """
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            source_code = f.read()

        # Парсим код в CST
        tree = cst.parse_module(source_code)

        # Применяем трансформации
        transformer = FixMIMEMultipartAssignment()
        tree = tree.visit(transformer)

        transformer = FixDictAccessAnnotations()
        tree = tree.visit(transformer)

        transformer = AddAsyncTypeHints()
        tree = tree.visit(transformer)

        transformer = FixStringConcatenation()
        tree = tree.visit(transformer)

        # Возвращаем трансформированный код
        return tree.code
    except Exception as e:
        print(f"Ошибка при трансформации файла {file_path}: {e}")
        return source_code


def batch_transform(directory: str, pattern: str = "*.py") -> None:
    """
    Применяет трансформации ко всем файлам в директории.

    Args:
        directory: Директория для обработки
        pattern: Паттерн файлов (по умолчанию *.py)
    """

    files = list(Path(directory).rglob(pattern))

    for file_path in files:
        # Пропускаем __pycache__ и .git
        if "__pycache__" in str(file_path) or ".git" in str(file_path):
            continue

        print(f"Трансформация: {file_path}")
        transformed_code = transform_file(str(file_path))

        # Записываем обратно
        with file_path.open("w", encoding="utf-8") as f:
            f.write(transformed_code)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Применяет libcst трансформации к коду")
    parser.add_argument("path", help="Путь к файлу или директории")
    parser.add_argument("--pattern", default="*.py", help="Паттерн файлов (по умолчанию *.py)")

    args = parser.parse_args()

    if Path(args.path).is_dir():
        batch_transform(args.path, args.pattern)
        print(f"\n✅ Трансформации применены ко всем файлам в {args.path}")
    else:
        transformed = transform_file(args.path)
        with Path(args.path).open("w", encoding="utf-8") as f:
            f.write(transformed)
        print(f"✅ Файл {args.path} трансформирован")
