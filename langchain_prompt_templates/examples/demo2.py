# Преобразование любого шаблона в нужный тип
chat_template = convert_template(any_template, ChatPromptTemplate)

# Добавление, удаление и обновление сообщений
chat_template.add_assistant_message("Новый ответ", index=3)
chat_template.remove_message(2)
chat_template.update_message(1, new_content="Обновленное сообщение")

# Проверка перед форматированием
if chat_template.validate(concept="нейронные сети", domain="AI"):
    messages = chat_template.format(...)

# Построение шаблона пошагово
builder = ChatPromptBuilder()
builder.add_system_message("...")
# ... много шагов ...
template = builder.build()