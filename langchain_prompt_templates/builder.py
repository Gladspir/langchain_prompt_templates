"""Builder-паттерн для создания и модификации чат-промтов."""

import re
from typing import Dict, List, Any

from .chat import ChatPromptTemplate, ChatMessage

class ChatPromptBuilder:
    """Строитель для создания и модификации чат-промтов."""
    
    def __init__(self):
        self.messages = []
        self.input_variables = []
    
    def add_system_message(self, content: str) -> 'ChatPromptBuilder':
        """Добавляет системное сообщение."""
        self.messages.append({"role": "system", "content": content})
        self._update_variables(content)
        return self
    
    def add_user_message(self, content: str) -> 'ChatPromptBuilder':
        """Добавляет сообщение пользователя."""
        self.messages.append({"role": "user", "content": content})
        self._update_variables(content)
        return self
    
    def add_assistant_message(self, content: str) -> 'ChatPromptBuilder':
        """Добавляет сообщение ассистента."""
        self.messages.append({"role": "assistant", "content": content})
        self._update_variables(content)
        return self
    
    def _update_variables(self, content: str):
        """Извлекает и добавляет переменные из содержимого."""
        new_vars = re.findall(r'\{(\w+)\}', content)
        for var in new_vars:
            if var not in self.input_variables:
                self.input_variables.append(var)
    
    def build(self) -> ChatPromptTemplate:
        """Создает финальный шаблон чата."""
        return ChatPromptTemplate(
            messages=self.messages.copy(),
            input_variables=self.input_variables.copy()
        )
    
    def reset(self) -> 'ChatPromptBuilder':
        """Сбрасывает строитель к начальному состоянию."""
        self.messages = []
        self.input_variables = []
        return self
    
    def from_template(self, template: ChatPromptTemplate) -> 'ChatPromptBuilder':
        """Инициализирует строитель на основе существующего шаблона."""
        self.reset()
        for msg in template.messages:
            self.messages.append(msg.copy())
        self.input_variables = template.input_variables.copy()
        return self