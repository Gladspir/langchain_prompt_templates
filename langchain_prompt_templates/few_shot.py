"""Реализация шаблона с примерами (few-shot learning)."""

from typing import Dict, List, Any, Optional

from .base import PromptTemplateBase
from .string import StringPromptTemplate

class FewShotPromptTemplate(PromptTemplateBase):
    """Реализация шаблона с примерами (few-shot learning)."""
    
    def __init__(self, 
                 prefix: str,
                 suffix: str,
                 example_template: PromptTemplateBase,
                 examples: List[Dict[str, str]],
                 input_variables: List[str],
                 example_separator: str = "\n\n",
                 **kwargs):
        """
        Args:
            prefix: Текст перед примерами
            suffix: Текст после примеров
            example_template: Шаблон для форматирования каждого примера
            examples: Список примеров (словари с переменными)
            input_variables: Переменные для всего шаблона
            example_separator: Разделитель между примерами
        """
        super().__init__(input_variables, **kwargs)
        self.prefix = prefix
        self.suffix = suffix
        self.example_template = example_template
        self.examples = examples
        self.example_separator = example_separator
    
    def format(self, **kwargs) -> str:
        if not self.validate(**kwargs):
            missing = set(self.input_variables) - set(kwargs.keys())
            raise ValueError(f"Отсутствуют обязательные переменные: {missing}")
        
        # Форматируем примеры
        formatted_examples = []
        for example in self.examples:
            # Объединяем переменные примера с переменными из kwargs
            example_vars = {**example, **{k: v for k, v in kwargs.items() if k in self.input_variables}}
            formatted_example = self.example_template.format(**example_vars)
            formatted_examples.append(formatted_example)
        
        # Форматируем префикс и суффикс
        prefix = self.prefix.format(**kwargs) if "{" in self.prefix else self.prefix
        suffix = self.suffix.format(**kwargs)
        
        # Собираем всё вместе
        return f"{prefix}{self.example_separator.join(formatted_examples)}{suffix}"
    
    def validate(self, **kwargs) -> bool:
        # Проверяем переменные в префиксе, суффиксе и примерах
        all_vars = []
        
        # Переменные в префиксе
        if "{" in self.prefix and "}" in self.prefix:
            prefix_vars = self._extract_variables(self.prefix)
            all_vars.extend(prefix_vars)
        
        # Переменные в суффиксе
        if "{" in self.suffix and "}" in self.suffix:
            suffix_vars = self._extract_variables(self.suffix)
            all_vars.extend(suffix_vars)
        
        # Переменные в примерах
        for example in self.examples:
            all_vars.extend(example.keys())
        
        # Удаляем дубликаты и оставляем только те, что в input_variables
        required_vars = set(all_vars) & set(self.input_variables)
        return all(var in kwargs for var in required_vars)
    
    def _extract_variables(self, text: str) -> List[str]:
        """Извлекает имена переменных из текста шаблона."""
        import re
        return re.findall(r'\{(\w+)\}', text)
    
    @classmethod
    def from_examples(cls, 
                     examples: List[Dict[str, str]],
                     example_prompt: PromptTemplateBase,
                     prefix: str,
                     suffix: str,
                     input_variables: List[str],
                     example_separator: str = "\n\n",
                     **kwargs) -> 'FewShotPromptTemplate':
        """Создает экземпляр из примеров и шаблонов."""
        return cls(prefix, suffix, example_prompt, examples, input_variables, example_separator, **kwargs)
    
    def to_string_template(self) -> 'StringPromptTemplate':
        """Преобразует few-shot шаблон в строковый, объединяя все элементы."""
        from .string import StringPromptTemplate
        
        # Форматируем примеры без подстановки переменных
        example_strings = []
        for example in self.examples:
            formatted = self.example_template.template
            for var, value in example.items():
                formatted = formatted.replace(f"{{{var}}}", f"{{{var}}}")
            example_strings.append(formatted)
        
        combined = f"{self.prefix}\n{self.example_separator.join(example_strings)}\n{self.suffix}"
        return StringPromptTemplate(
            template=combined,
            input_variables=self.input_variables.copy()
        )
    
    def to_chat_template(self) -> 'ChatPromptTemplate':
        """Преобразует few-shot шаблон в чат-шаблон."""
        from .chat import ChatPromptTemplate, ChatMessage
        
        messages = []
        
        # Добавляем префикс как системное сообщение
        if self.prefix.strip():
            messages.append({"role": "system", "content": self.prefix})
        
        # Добавляем примеры как пары сообщений
        for example in self.examples:
            # Форматируем пример без подстановки переменных
            formatted_example = self.example_template.template
            for var, value in example.items():
                formatted_example = formatted_example.replace(f"{{{var}}}", f"{{{var}}}")
            
            # Пытаемся извлечь input и output из примера
            if "input" in example and "output" in example:
                messages.append({"role": "user", "content": example["input"]})
                messages.append({"role": "assistant", "content": example["output"]})
            else:
                # Если структура неизвестна, добавляем как одно сообщение
                messages.append({"role": "user", "content": formatted_example})
        
        # Добавляем суффикс как последнее сообщение пользователя
        if self.suffix.strip():
            messages.append({"role": "user", "content": self.suffix})
        
        return ChatPromptTemplate(
            messages=messages,
            input_variables=self.input_variables.copy()
        )
    
    def to_few_shot_template(self) -> 'FewShotPromptTemplate':
        return self  # Уже few-shot шаблон
    
    def _convert_to(self, target_type: Type['PromptTemplateBase']) -> 'PromptTemplateBase':
        from .string import StringPromptTemplate
        from .chat import ChatPromptTemplate
        
        if target_type == StringPromptTemplate:
            return self.to_string_template()
        elif target_type == ChatPromptTemplate:
            return self.to_chat_template()
        return self