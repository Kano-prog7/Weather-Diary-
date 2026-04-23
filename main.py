import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.records = []
        self.load_records()
        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="Дата:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_picker = DateEntry(self.root, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        self.date_picker.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Температура (°C):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.temp_entry = tk.Entry(self.root)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Описание:").grid(row=2, column=0, padx=5, pady=5, sticky="ne")
        self.desc_text = tk.Text(self.root, height=4, width=20)
        self.desc_text.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Осадки:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.rain_var = tk.IntVar()
        tk.Checkbutton(self.root, text="Да", variable=self.rain_var).grid(row=3, column=1, padx=5, pady=5)

        # Кнопка добавления
        tk.Button(self.root, text="Добавить запись", command=self.add_record).grid(row=4, column=0, columnspan=2, pady=10)

        # Таблица записей
        self.tree = ttk.Treeview(self.root, columns=("date", "temp", "desc", "rain"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("rain", text="Осадки")
        self.tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Фильтры
        tk.Label(self.root, text="Фильтр по дате:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.filter_date_picker = DateEntry(self.root, width=12)
        self.filter_date_picker.grid(row=6, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Фильтр по температуре (выше):").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.filter_temp_entry = tk.Entry(self.root)
        self.filter_temp_entry.grid(row=7, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Применить фильтр", command=self.apply_filter).grid(row=8, column=0, columnspan=2)

    def add_record(self):
        date = self.date_picker.get_date().strftime("%Y-%m-%d")
        temp = self.temp_entry.get()
        desc = self.desc_text.get("1.0", tk.END).strip()
        rain = "Да" if self.rain_var.get() else "Нет"

        # Валидация
        if not temp.replace('.', '', 1).isdigit():
            messagebox.showerror("Ошибка", "Температура должна быть числом.")
            return

        if not desc:
            messagebox.showerror("Ошибка", "Поле 'Описание' не может быть пустым.")
            return

        if datetime.strptime(date, "%Y-%m-%d") > datetime.now():
            messagebox.showerror("Ошибка", "Дата не может быть в будущем.")
            return

        # Добавление записи
        self.records.append({
            "date": date,
            "temperature": float(temp),
            "description": desc,
            "rain": rain == "Да"
        })

        self.save_records()
        self.update_table()
        
        # Очистка полей после добавления
        self.temp_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)

    def update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for record in self.records:
            rain_text = "Да" if record["rain"] else "Нет"
            self.tree.insert("", "end", values=(record["date"], record["temperature"], record["description"], rain_text))

    def apply_filter(self):
        filtered_records = self.records.copy()
        
        # Фильтр по дате
        filter_date = self.filter_date_picker.get_date().strftime("%Y-%m-%d")
        
        # Фильтр по температуре
        filter_temp_text = self.filter_temp_entry.get()
        
        if filter_date:
            filtered_records = [r for r in filtered_records if r["date"] == filter_date]
            
            if filter_temp_text and filter_temp_text.replace('.', '', 1).isdigit():
                filtered_records = [r for r in filtered_records if r["temperature"] > float(filter_temp_text)]
        
        elif filter_temp_text and filter_temp_text.replace('.', '', 1).isdigit():
            filtered_records = [r for r in filtered_records if r["temperature"] > float(filter_temp_text)]
        
        # Обновление таблицы с отфильтрованными данными
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for record in filtered_records:
            rain_text = "Да" if record["rain"] else "Нет"
            self.tree.insert("", "end", values=(record["date"], record["temperature"], record["description"], rain_text))

    def save_records(self):
        with open("weather.json", "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)

    def load_records(self):
        if os.path.exists("weather.json"):
            with open("weather.json", "r", encoding="utf-8") as f:
                try:
                    self.records = json.load(f)
                except json.JSONDecodeError:
                    self.records = []
                    messagebox.showwarning("Предупреждение", "Файл погоды поврежден или пуст. Создан новый список.")
