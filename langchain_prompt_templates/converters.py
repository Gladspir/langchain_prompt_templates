"""Утилиты для преобразования между типами промт-шаблонов."""

from typing import Type, Any

from .base import PromptTemplateBase

def convert_template(source_template: PromptTemplateBase, 
                    target_type: Type[PromptTemplateBase]) -> PromptTemplateBase:
    """
    Универсальная функция для преобразования одного типа промт-шаблона в другой.
    
    Args:
        source_template: Исходный шаблон для преобразования
        target_type: Целевой тип шаблона
        
    Returns:
        Новый экземпляр целевого типа
        
    Example:
        # Преобразование строкового шаблона в чат-шаблон
        chat_template = convert_template(string_template, ChatPromptTemplate)
    """
    return source_template._convert_to(target_type)

def auto_convert(source_template: PromptTemplateBase, 
                target_type: Type[PromptTemplateBase],
                **kwargs) -> PromptTemplateBase:
    """
    Расширенное преобразование с возможностью настройки параметров преобразования.
    
    Args:
        source_template: Исходный шаблон для преобразования
        target_type: Целевой тип шаблона
        **kwargs: Дополнительные параметры для метода преобразования
        
    Returns:
        Новый экземпляр целевого типа
    """
    if target_type.__name__ == "ChatPromptTemplate":
        return source_template.to_chat_template(**kwargs)
    elif target_type.__name__ == "StringPromptTemplate":
        return source_template.to_string_template(**kwargs)
    elif target_type.__name__ == "FewShotPromptTemplate":
        return source_template.to_few_shot_template(**kwargs)
    else:
        return source_template._convert_to(target_type)