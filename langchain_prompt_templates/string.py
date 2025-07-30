"""Реализация простого строкового шаблона промта."""

import re
from typing import Dict, List, Any

from .base import PromptTemplateBase

class StringPromptTemplate(PromptTemplateBase):
    """Реализация простого строкового шаблона промта."""
    
    def __init__(self, template: str, input_variables: List[str], **kwargs):
        super().__init__(input_variables, **kwargs)
        self.template = template
    
    def format(self, **kwargs) -> str:
        if not self.validate(**kwargs):
            missing = set(self.input_variables) - set(kwargs.keys())
            raise ValueError(f"Отсутствуют обязательные переменные: {missing}")
        
        return self.template.format(**kwargs)
    
    def validate(self, **kwargs) -> bool:
        return all(var in kwargs for var in self.input_variables)
    
    @classmethod
    def from_template(cls, template: str, input_variables: List[str], **kwargs) -> 'StringPromptTemplate':
        """Создает экземпляр из строкового шаблона."""
        return cls(template, input_variables, **kwargs)
    
    def to_string_template(self) -> 'StringPromptTemplate':
        return self  # Уже строковый шаблон
    
    def to_chat_template(self) -> 'ChatPromptTemplate':
        """Преобразует строковый шаблон в чат-шаблон, используя его как сообщение пользователя."""
        from .chat import ChatPromptTemplate
        
        return ChatPromptTemplate(
            messages=[{"role": "user", "content": self.template}],
            input_variables=self.input_variables.copy()
        )
    
    def to_few_shot_template(self, 
                            example_separator: str = "\n\n",
                            prefix: Optional[str] = None,
                            suffix: Optional[str] = None) -> 'FewShotPromptTemplate':
        """Преобразует строковый шаблон в few-shot шаблон с одним примером."""
        from .few_shot import FewShotPromptTemplate
        
        # Создаем базовый шаблон для примеров
        example_template = StringPromptTemplate(
            template=self.template,
            input_variables=self.input_variables.copy()
        )
        
        # Если префикс не указан, используем пустую строку
        if prefix is None:
            prefix = ""
        
        # Если суффикс не указан, используем шаблон как суффикс
        if suffix is None:
            suffix = self.template
        
        return FewShotPromptTemplate(
            prefix=prefix,
            suffix=suffix,
            example_template=example_template,
            examples=[{var: f"{{{{{var}}}}}" for var in self.input_variables}],
            input_variables=self.input_variables.copy(),
            example_separator=example_separator
        )
    
    def _convert_to(self, target_type: Type['PromptTemplateBase']) -> 'PromptTemplateBase':
        from .chat import ChatPromptTemplate
        from .few_shot import FewShotPromptTemplate
        
        if target_type == ChatPromptTemplate:
            return self.to_chat_template()
        elif target_type == FewShotPromptTemplate:
            return self.to_few_shot_template()
        return self  # По умолчанию возвращаем себя