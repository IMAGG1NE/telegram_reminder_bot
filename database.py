import sqlite3 

# Создание соединения с базой данных
conn = sqlite3.connect('tasks.db')

# Получение курсора
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   task_text TEXT,
                   task_time TEXT)''')
