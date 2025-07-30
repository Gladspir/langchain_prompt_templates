from langchain_prompt_templates import (
    StringPromptTemplate,
    ChatPromptTemplate,
    FewShotPromptTemplate,
    convert_template
)

# 1. Создание строкового шаблона
string_template = StringPromptTemplate.from_template(
    "Объясни, что такое {concept}, простыми словами.",
    ["concept"]
)

# 2. Преобразование в чат-шаблон
chat_template = string_template.to_chat_template()
chat_template.add_system_message("Ты эксперт по {domain}.", index=0)

# 3. Динамическое добавление сообщений
chat_template.add_user_message("Можешь привести пример кода для {concept}?")

# 4. Форматирование
messages = chat_template.format(
    concept="декораторы в Python",
    domain="программированию"
)

# 5. Преобразование в few-shot шаблон
few_shot = convert_template(
    chat_template,
    FewShotPromptTemplate,
    prefix="Объясни следующие концепции Python:",
    suffix="\nКонцепция: {concept}\nОбъяснение:"
)

# 6. Использование builder-паттерна
from langchain_prompt_templates import ChatPromptBuilder

builder = ChatPromptBuilder()
builder.add_system_message("Ты помощник по программированию на {language}")
builder.add_user_message("Как работает {concept}?")

if need_more_context:
    builder.add_system_message("Важно приводить примеры кода.")

template = builder.build()