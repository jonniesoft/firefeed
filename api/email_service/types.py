"""
Type stubs for email service configuration.
Обеспечивает типобезопасность для конфигурации SMTP.
"""

from typing import TypedDict


class SMTPConfig(TypedDict, total=False):
    """Типизированная конфигурация SMTP для email отправки."""

    server: str
    port: int
    email: str
    password: str
    use_tls: bool
