import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

# Инициализация истории
history = load_history()

def load_history(filename="history.json"):
    """Загрузка истории из JSON-файла"""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_history(history, filename="history.json"):
    """Сохранение истории в JSON-файл"""
    with open(filename, "w") as f:
        json.dump(history, f, indent=4)

def validate_amount(amount_str):
    """Проверка корректности суммы"""
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Сумма должна быть положительным числом")
        return amount
    except ValueError:
        raise ValueError("Некорректный формат суммы")

def get_exchange_rate(from_currency, to_currency, api_key):
    """Получение курса валют через API"""
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and to_currency in data["rates"]:
            return data["rates"][to_currency]
        else:
            raise Exception("Ошибка получения курса валют")
    except requests.exceptions.RequestException:
        raise Exception("Ошибка подключения к API")

def convert_currency():
    """Функция конвертации валют"""
    try:
        from_curr = from_currency.get()
        to_curr = to_currency.get()
        amount_str = amount_entry.get()

        # Проверка ввода
        amount = validate_amount(amount_str)

        # Получение курса
        rate = get_exchange_rate(from_curr, to_curr, API_KEY)
        result = amount * rate

        # Добавление в историю
        history_entry = {
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": round(result, 2)
        }
        history.append(history_entry)
        save_history(history)

        # Обновление таблицы
        history_tree.insert("", "end", values=(
            from_curr,
            to_curr,
            amount,
            round(result, 2)
        ))

        # Показ результата
        messagebox.showinfo(
            "Результат",
            f"{amount} {from_curr} = {round(result, 2)} {to_curr}"
        )

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def create_gui():
    """Создание графического интерфейса"""
    root = tk.Tk()
    root.title("Currency Converter")
    root.geometry("600x400")

    # Выбор валюты «из»
    tk.Label(root, text="Из:").grid(row=0, column=0, padx=10, pady=10)
    from_currency = ttk.Combobox(root, values=["USD", "EUR", "RUB", "GBP", "JPY"])
    from_currency.grid(row=0, column=1, padx=10, pady=10)

    # Выбор валюты «в»
    tk.Label(root, text="В:").grid(row=1, column=0, padx=10, pady=10)
    to_currency = ttk.Combobox(root, values=["USD", "EUR", "RUB", "GBP", "JPY"])
    to_currency.grid(row=1, column=1, padx=10, pady=10)

    # Поле ввода суммы
    tk.Label(root, text="Сумма:").grid(row=2, column=0, padx=10, pady=10)
    amount_entry = tk.Entry(root)
    amount_entry.grid(row=2, column=1, padx=10, pady=10)

    # Кнопка конвертации
    convert_button = tk.Button(root, text="Конвертировать", command=convert_currency)
    convert_button.grid(row=3, column=0, columnspan=2, pady=20)

    # Таблица истории
    history_tree = ttk.Treeview(root, columns=("From", "To", "Amount", "Result"), show="headings")
    history_tree.heading("From", text="Из")
    history_tree.heading("To", text="В")
    history_tree.heading("Amount", text="Сумма")
    history_tree.heading("Result", text="Результат")
    history_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # Заполнение таблицы существующей историей
    for entry in history:
        history_tree.insert("", "end", values=(
            entry["from"],
            entry["to"],
            entry["amount"],
            entry["result"]
        ))

    return root, from_currency, to_currency, amount_entry, history_tree

# Запуск приложения
if __name__ == "__main__":
    root, from_currency, to_currency, amount_entry, history_tree = create_gui()
    root.mainloop()
