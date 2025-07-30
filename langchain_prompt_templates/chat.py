"""Реализация чат-ориентированного шаблона промта с возможностью динамического изменения."""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .base import PromptTemplateBase

@dataclass
class ChatMessage:
    """Представление сообщения в чат-промте."""
    role: str  # system, user, assistant
    content: str

class ChatPromptTemplate(PromptTemplateBase):
    """Реализация шаблона для чат-ориентированных промтов с возможностью динамического изменения."""
    
    def __init__(self, messages: List[Dict[str, str]], input_variables: List[str], **kwargs):
        super().__init__(input_variables, **kwargs)
        self.messages = messages
        self._original_input_vars = input_variables.copy()  # Сохраняем исходные переменные для отслеживания
    
    def format(self, **kwargs) -> List[ChatMessage]:
        if not self.validate(**kwargs):
            missing = set(self.input_variables) - set(kwargs.keys())
            raise ValueError(f"Отсутствуют обязательные переменные: {missing}")
        
        formatted_messages = []
        for msg in self.messages:
            role = msg["role"]
            # Форматируем содержимое сообщения, если оно содержит переменные
            content = msg["content"]
            if "{" in content and "}" in content:
                content = content.format(**kwargs)
            formatted_messages.append(ChatMessage(role=role, content=content))
        
        return formatted_messages
    
    def validate(self, **kwargs) -> bool:
        # Проверяем, что все переменные, используемые в шаблонах, предоставлены
        all_vars = []
        for msg in self.messages:
            content = msg["content"]
            # Извлекаем переменные из шаблона
            if "{" in content and "}" in content:
                vars_in_msg = re.findall(r'\{(\w+)\}', content)
                all_vars.extend(vars_in_msg)
        
        required_vars = set(all_vars) & set(self.input_variables)
        return all(var in kwargs for var in required_vars)
    
    @classmethod
    def from_template(cls, messages: List[Dict[str, str]], input_variables: List[str], **kwargs) -> 'ChatPromptTemplate':
        """Создает экземпляр из списка сообщений."""
        return cls(messages, input_variables, **kwargs)
    
    @classmethod
    def from_messages(cls, *message_tuples) -> 'ChatPromptTemplate':
        """
        Альтернативный конструктор для создания из кортежей (роль, содержание).
        
        Пример:
        ChatPromptTemplate.from_messages(
            ("system", "Ты {role}"),
            ("user", "Объясни {concept}")
        )
        """
        messages = [{"role": role, "content": content} for role, content in message_tuples]
        
        # Автоматически извлекаем переменные из содержимого
        input_variables = []
        for _, content in message_tuples:
            if "{" in content and "}" in content:
                vars_in_msg = re.findall(r'\{(\w+)\}', content)
                input_variables.extend(vars_in_msg)
        
        input_variables = list(set(input_variables))  # Уникальные переменные
        return cls(messages, input_variables)
    
    def add_message(self, role: str, content: str, index: Optional[int] = None) -> None:
        """
        Добавляет новое сообщение в шаблон.
        
        Args:
            role: Роль сообщения (system, user, assistant)
            content: Содержание сообщения, может содержать переменные в формате {variable}
            index: Позиция для вставки. Если None, добавляет в конец.
        """
        # Извлекаем переменные из нового содержимого
        new_vars = self._extract_variables(content)
        
        # Добавляем новые переменные в input_variables, если их там нет
        for var in new_vars:
            if var not in self.input_variables:
                self.input_variables.append(var)
        
        # Добавляем сообщение
        message = {"role": role, "content": content}
        if index is None:
            self.messages.append(message)
        else:
            self.messages.insert(index, message)
    
    def add_system_message(self, content: str, index: Optional[int] = None) -> None:
        """Добавляет системное сообщение."""
        self.add_message("system", content, index)
    
    def add_user_message(self, content: str, index: Optional[int] = None) -> None:
        """Добавляет сообщение пользователя."""
        self.add_message("user", content, index)
    
    def add_assistant_message(self, content: str, index: Optional[int] = None) -> None:
        """Добавляет сообщение ассистента."""
        self.add_message("assistant", content, index)
    
    def remove_message(self, index: int) -> None:
        """Удаляет сообщение по индексу."""
        if 0 <= index < len(self.messages):
            # Удаляем сообщение
            removed_msg = self.messages.pop(index)
            
            # Проверяем, не использовались ли переменные из этого сообщения в других
            content = removed_msg["content"]
            removed_vars = self._extract_variables(content)
            
            # Если переменные больше нигде не используются, удаляем их из input_variables
            remaining_vars = set()
            for msg in self.messages:
                remaining_vars.update(self._extract_variables(msg["content"]))
            
            self.input_variables = [
                var for var in self.input_variables 
                if var in remaining_vars or var in self._original_input_vars
            ]
        else:
            raise IndexError("Индекс сообщения вне диапазона")
    
    def update_message(self, index: int, new_content: Optional[str] = None, 
                      new_role: Optional[str] = None) -> None:
        """Обновляет существующее сообщение."""
        if 0 <= index < len(self.messages):
            old_content = self.messages[index]["content"]
            old_vars = self._extract_variables(old_content)
            
            if new_content is not None:
                # Обновляем содержимое
                self.messages[index]["content"] = new_content
                
                # Обновляем переменные
                new_vars = self._extract_variables(new_content)
                
                # Удаляем старые переменные, если они больше не нужны
                for var in old_vars:
                    if var not in new_vars:
                        # Проверяем, не используется ли переменная в других сообщениях
                        used_elsewhere = any(
                            var in self._extract_variables(msg["content"]) 
                            for i, msg in enumerate(self.messages) if i != index
                        )
                        if not used_elsewhere and var in self.input_variables:
                            self.input_variables.remove(var)
                
                # Добавляем новые переменные
                for var in new_vars:
                    if var not in self.input_variables:
                        self.input_variables.append(var)
            
            if new_role is not None:
                self.messages[index]["role"] = new_role
        else:
            raise IndexError("Индекс сообщения вне диапазона")
    
    def _extract_variables(self, text: str) -> List[str]:
        """Извлекает имена переменных из текста шаблона."""
        return re.findall(r'\{(\w+)\}', text)
    
    def get_message_history(self) -> List[Dict[str, str]]:
        """Возвращает текущую историю сообщений."""
        return self.messages.copy()
    
    def to_string_template(self) -> 'StringPromptTemplate':
        """Преобразует чат-шаблон в строковый, объединяя все сообщения."""
        from .string import StringPromptTemplate
        
        # Создаем строку с разделением по ролям
        formatted_messages = []
        for msg in self.messages:
            role = msg["role"].upper()
            content = msg["content"]
            formatted_messages.append(f"[{role}]: {content}")
        
        combined = "\n".join(formatted_messages)
        return StringPromptTemplate(
            template=combined,
            input_variables=self.input_variables.copy()
        )
    
    def to_chat_template(self) -> 'ChatPromptTemplate':
        return self  # Уже чат-шаблон
    
    def to_few_shot_template(self, 
                            example_separator: str = "\n\n",
                            prefix: Optional[str] = None,
                            suffix: Optional[str] = None) -> 'FewShotPromptTemplate':
        """
        Преобразует чат-шаблон в few-shot шаблон.
        Предполагает, что чат содержит пары сообщений (пользователь-ассистент) как примеры.
        """
        from .few_shot import FewShotPromptTemplate
        from .string import StringPromptTemplate
        
        # Группируем сообщения в пары (пользователь-ассистент)
        examples = []
        current_example = {}
        
        for i, msg in enumerate(self.messages):
            if msg["role"] == "user":
                if current_example and "input" in current_example:
                    examples.append(current_example)
                    current_example = {}
                current_example["input"] = msg["content"]
            elif msg["role"] == "assistant" and "input" in current_example:
                current_example["output"] = msg["content"]
                examples.append(current_example)
                current_example = {}
        
        # Если остался незавершенный пример
        if current_example and "input" in current_example:
            examples.append(current_example)
        
        # Создаем шаблон для примеров
        example_template = StringPromptTemplate(
            template="Вопрос: {input}\nОтвет: {output}",
            input_variables=["input", "output"]
        )
        
        # Настройка префикса и суффикса
        if prefix is None:
            prefix = "Решите следующие задачи:\n\n"
        
        if suffix is None:
            # Последнее сообщение пользователя становится шаблоном для ввода
            last_user_msg = next((msg["content"] for msg in reversed(self.messages) 
                                if msg["role"] == "user"), "{input}")
            suffix = f"\nВопрос: {last_user_msg}\nОтвет:"
        
        return FewShotPromptTemplate(
            prefix=prefix,
            suffix=suffix,
            example_template=example_template,
            examples=examples,
            input_variables=["input"],  # Переменная для нового ввода
            example_separator=example_separator
        )
    
    def _convert_to(self, target_type: Type['PromptTemplateBase']) -> 'PromptTemplateBase':
        from .string import StringPromptTemplate
        from .few_shot import FewShotPromptTemplate
        
        if target_type == StringPromptTemplate:
            return self.to_string_template()
        elif target_type == FewShotPromptTemplate:
            return self.to_few_shot_template()
        return self