"""Примеры использования пакета промт-шаблонов."""

from ..string import StringPromptTemplate
from ..chat import ChatPromptTemplate, ChatMessage
from ..few_shot import FewShotPromptTemplate
from ..builder import ChatPromptBuilder
from ..converters import convert_template

def basic_string_example():
    """Пример использования строкового шаблона."""
    template = StringPromptTemplate.from_template(
        "Объясни, что такое {concept}, простыми словами.",
        ["concept"]
    )
    return template.format(concept="нейронные сети")

def chat_example():
    """Пример использования чат-шаблона с динамическим изменением."""
    template = ChatPromptTemplate.from_messages(
        ("system", "Ты {role} по {domain}."),
        ("user", "Объясни, что такое {concept}.")
    )
    
    # Добавляем новые элементы диалога
    template.add_user_message("Можешь привести пример использования {concept}?")
    template.add_assistant_message("Конечно! {example}", index=2)
    template.add_system_message("Важно отвечать кратко и по делу.", index=1)
    
    return template.format(
        role="эксперт", 
        domain="программированию", 
        concept="декораторы в Python",
        example="Вот пример: @decorator\ndef my_func():\n    pass"
    )

def few_shot_example():
    """Пример использования few-shot шаблона."""
    example_template = StringPromptTemplate.from_template(
        "Вопрос: {question}\nОтвет: {answer}",
        ["question", "answer"]
    )

    few_shot = FewShotPromptTemplate.from_examples(
        examples=[
            {"question": "2+2", "answer": "4"},
            {"question": "Сколько планет в Солнечной системе?", "answer": "8"}
        ],
        example_prompt=example_template,
        prefix="Решите следующие задачи:",
        suffix="Вопрос: {input}\nОтвет:",
        input_variables=["input"]
    )
    return few_shot.format(input="Какая столица Франции?")

def conversion_example():
    """Пример преобразования между типами шаблонов."""
    # Создаем строковый шаблон
    string_template = StringPromptTemplate.from_template(
        "Объясни, что такое {concept}, простыми словами.",
        ["concept"]
    )
    
    # Преобразуем в чат-шаблон
    chat_template = string_template.to_chat_template()
    
    # Добавляем системное сообщение
    chat_template.add_system_message("Ты эксперт по {domain}.", index=0)
    
    # Преобразуем в few-shot шаблон
    few_shot = chat_template.to_few_shot_template(
        prefix="Объясни следующие концепции:",
        suffix="\nКонцепция: {concept}\nОбъяснение:"
    )
    
    return few_shot.format(
        concept="нейронные сети",
        domain="машинному обучению"
    )

def builder_example():
    """Пример использования ChatPromptBuilder."""
    builder = ChatPromptBuilder()
    builder.add_system_message("Ты эксперт по {domain}")
    builder.add_user_message("Объясни {concept}")
    
    if True:  # Условие для добавления дополнительного сообщения
        builder.add_user_message("Как это связано с {related_concept}?")
    
    template = builder.build()
    return template.format(
        domain="программированию",
        concept="декораторы",
        related_concept="функциями высшего порядка"
    )