import model
from view import View


class Controller:
    def __init__(self):
        self.view = View()
        #self.model = Model()

    def run(self):
        while True:
            choice = self.view.show_menu()
            if choice == '1':
                self.view_tables()
            elif choice == '2':
                self.add_data()
            elif choice == '3':
                self.update_data()
            elif choice == '4':
                self.delete_data()
            elif choice == '5':
                self.generate_data()
            elif choice == '6':
                self.read_data()
            elif choice == '7':
                break

    def view_tables(self):
        tables = model.get_all_tables()
        self.view.show_tables(tables)

    def add_data(self):
        # Отримуємо назву таблиці та дані для вставки
        table, columns, values = self.view.insert()

        # Формуємо словник для передачі даних у модель
        data_dict = dict(zip(columns, values))

        # Викликаємо ORM-метод для додавання даних
        try:
            model.add_data(table, data_dict)
            new_record = data_dict
            self.view.show_message(f"Дані успішно додані: {new_record}")
        except Exception as e:
            self.view.show_message(f"Помилка під час додавання: {str(e)}")

    def read_data(self):
        try:
            # Отримуємо назву таблиці
            table = self.view.ask_table()

            # Викликаємо ORM-метод для читання даних
            records, columns = model.read_data(table)
            self.view.show_data(records, columns)
        except ValueError as e:
            self.view.show_message(f"Помилка: {str(e)}")
        except Exception as e:
            self.view.show_message(f"Неочікувана помилка: {str(e)}")

    def delete_data(self):
        try:
            # Отримуємо назву таблиці
            table, record_id = self.view.delete()

            # Викликаємо ORM-метод для видалення даних
            model.delete_data(table, record_id)

            self.view.show_message(f"Запис із ID {record_id} успішно видалено з таблиці {table}.")
        except ValueError as e:
            self.view.show_message(f"Помилка: {str(e)}")
        except Exception as e:
            self.view.show_message(f"Неочікувана помилка: {str(e)}")

    def update_data(self):
        try:
            # Отримуємо дані для оновлення
            table, columns, record_id, new_values = self.view.update()

            # Перевіряємо, що кількість колонок відповідає кількості нових значень
            if len(columns) != len(new_values):
                raise ValueError("Кількість колонок не співпадає з кількістю нових значень.")

            # Формуємо словник оновлень
            updates = dict(zip(columns, new_values))

            # Викликаємо ORM-метод для оновлення даних
            model.update_data(table, record_id, updates)

            self.view.show_message(f"Запис із ID {record_id} успішно оновлено у таблиці {table}.")
        except ValueError as e:
            self.view.show_message(f"Помилка: {str(e)}")
        except Exception as e:
            self.view.show_message(f"Неочікувана помилка: {str(e)}")

    def generate_data(self):
        try:
            table, rows_count = self.view.generate_data_input()

            model.generate_data(table, rows_count)

            self.view.show_message(f"{rows_count} записів успішно згенеровано у таблицю {table}.")
        except ValueError as e:
            self.view.show_message(f"Помилка: {str(e)}")
        except Exception as e:
            self.view.show_message(f"Неочікувана помилка: {str(e)}")

