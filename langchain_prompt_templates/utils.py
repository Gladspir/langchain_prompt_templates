"""Вспомогательные утилиты для работы с промт-шаблонами."""

import re
from typing import List, Dict, Any

def extract_variables(text: str) -> List[str]:
    """Извлекает имена переменных из текста шаблона."""
    return re.findall(r'\{(\w+)\}', text)

def validate_template_variables(template: str, provided_vars: Dict[str, Any]) -> bool:
    """Проверяет, что все переменные в шаблоне предоставлены."""
    required_vars = extract_variables(template)
    return all(var in provided_vars for var in required_vars)

def format_template(template: str, **kwargs) -> str:
    """Форматирует шаблон с проверкой переменных."""
    if not validate_template_variables(template, kwargs):
        missing = set(extract_variables(template)) - set(kwargs.keys())
        raise ValueError(f"Отсутствуют обязательные переменные: {missing}")
    return template.format(**kwargs)