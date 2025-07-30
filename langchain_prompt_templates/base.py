"""Базовые абстрактные классы для всех типов промт-шаблонов."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Type, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .string import StringPromptTemplate
    from .chat import ChatPromptTemplate
    from .few_shot import FewShotPromptTemplate

class PromptTemplateBase(ABC):
    """Абстрактный базовый класс для всех типов шаблонов промтов с поддержкой преобразований."""
    
    def __init__(self, input_variables: List[str], **kwargs):
        """
        Инициализация шаблона промта.
        
        Args:
            input_variables: Список переменных, которые должны быть предоставлены при форматировании
            **kwargs: Дополнительные параметры, специфичные для конкретного типа шаблона
        """
        self.input_variables = input_variables
        self.kwargs = kwargs
    
    @abstractmethod
    def format(self, **kwargs) -> Any:
        """Форматирует шаблон, подставляя переданные переменные. Должен возвращать объект, готовый к использованию с LLM."""
        pass
    
    @abstractmethod
    def validate(self, **kwargs) -> bool:
        """Проверяет, что все необходимые переменные предоставлены для форматирования."""
        pass
    
    @classmethod
    @abstractmethod
    def from_template(cls, template: Any, input_variables: List[str], **kwargs) -> 'PromptTemplateBase':
        """Создает экземпляр шаблона из шаблонной строки или структуры."""
        pass
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Возвращает информацию о требуемых входных переменных."""
        return {
            "type": "object",
            "properties": {var: {"type": "string"} for var in self.input_variables},
            "required": self.input_variables
        }
    
    @abstractmethod
    def to_string_template(self) -> 'StringPromptTemplate':
        """Преобразует текущий шаблон в строковый шаблон."""
        pass
    
    @abstractmethod
    def to_chat_template(self) -> 'ChatPromptTemplate':
        """Преобразует текущий шаблон в чат-шаблон."""
        pass
    
    @abstractmethod
    def to_few_shot_template(self, 
                            example_separator: str = "\n\n",
                            prefix: Optional[str] = None,
                            suffix: Optional[str] = None) -> 'FewShotPromptTemplate':
        """Преобразует текущий шаблон в few-shot шаблон."""
        pass
    
    @classmethod
    def from_other_template(cls, source_template: 'PromptTemplateBase') -> 'PromptTemplateBase':
        """
        Фабричный метод для создания экземпляра текущего класса из другого шаблона.
        
        Args:
            source_template: Исходный шаблон для преобразования
            
        Returns:
            Новый экземпляр текущего класса
        """
        if isinstance(source_template, cls):
            return source_template  # Уже нужного типа
        
        # Делегируем преобразование исходному шаблону
        return source_template._convert_to(cls)
    
    @abstractmethod
    def _convert_to(self, target_type: Type['PromptTemplateBase']) -> 'PromptTemplateBase':
        """Внутренний метод для преобразования в указанный тип."""
        pass