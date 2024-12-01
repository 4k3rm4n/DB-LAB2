import random
import string
from datetime import datetime, timedelta

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import inspect
from sqlalchemy import text

DATABASE_URL = "postgresql://postgres:Vfdgjxrf1!@localhost:5432/lab1"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# Визначення моделей
class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_firstname = Column(String, nullable=False)
    user_lastname = Column(String, nullable=False)
    user_weight = Column(Integer, nullable=False)
    user_height = Column(Integer, nullable=False)



class Exercise(Base):
    __tablename__ = 'exercises'
    exercise_id = Column(Integer, primary_key=True)
    exercise_name = Column(String, nullable=False)
    difficulty = Column(Integer, nullable=False)
    description = Column(String, nullable=False)


class Training(Base):
    __tablename__ = 'training'
    training_id = Column(Integer, primary_key=True)
    start_date_time = Column(DateTime, nullable=False)
    end_date_time = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'))


class Workout(Base):
    __tablename__ = 'workout'
    workout_id = Column(Integer, primary_key=True)
    training_id = Column(Integer, ForeignKey('training.training_id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.exercise_id'), nullable=False)
    number_of_sets = Column(Integer, nullable=False)
    number_of_repetitions = Column(Integer, nullable=False)


# Мапа таблиць
TABLES = {
    "users": User,
    "exercises": Exercise,
    "training": Training,
    "workout": Workout
}

def generate_data(table, rows_count): # генерує і додає дані в таблицю
    data_dict = {}
    model = get_model(table)
    try:
        column_types = get_table_columns_and_types(table, engine)
        for i in range(rows_count):
            for key, value in column_types.items():
                reference_table_name = get_referred_table_by_column(key, table, engine)
                if reference_table_name is not None:
                    data_dict[key] = generate_random_value(value, reference_table_name, key)
                else:
                    data_dict[key] = generate_random_value(value)
            new_record = model(**data_dict)
            session.add(new_record)
            print(i)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def get_referred_table_by_column(column_name, table_name, engine):
    inspector = inspect(engine)

    foreign_keys = inspector.get_foreign_keys(table_name)

    for fk in foreign_keys:

        if column_name in fk['constrained_columns']:
            referred_table = fk['referred_table']
            return referred_table

    return None


def get_random_foreign_key_value(table_name, column_name):
    result = session.execute(text(f"SELECT {column_name} FROM {table_name}"))
    values = [row[0] for row in result.fetchall()]

    if not values:
        raise ValueError(f"Немає доступних значень у таблиці {table_name} для колонки {column_name}.")

    # Повертаємо випадкове значення
    return random.choice(values)


def generate_random_value(column_type, reference_table_name=None, column_name=None):
    column_type = column_type.lower()

    if column_name:
        return get_random_foreign_key_value(reference_table_name, column_name)

    if column_type == 'text':
        return ''.join(random.choices(string.ascii_letters, k=10))

    elif column_type == 'integer':
        return random.randint(1, 100)

    elif column_type == 'timestamp':
        now = datetime.now()
        random_days = random.randint(0, 30)
        random_seconds = random.randint(0, 86400)
        return now - timedelta(days=random_days, seconds=random_seconds)

    else:
        raise ValueError(f"Невідомий тип колонки: {column_type}")


def get_table_columns_and_types(table_name, engine):
    inspector = inspect(engine)

    columns = inspector.get_columns(table_name)
    pk_columns = inspector.get_pk_constraint(table_name)['constrained_columns']

    column_types = {column['name']: str(column['type']) for column in columns if column['name'] not in pk_columns}
    return column_types


def get_all_tables():
    try:
        inspector = inspect(session.bind)
        table_names = inspector.get_table_names()
        return table_names
    except Exception as e:
        raise RuntimeError(f"Не вдалося отримати список таблиць: {str(e)}")


def get_model(table_name):
    model = TABLES.get(table_name)
    if not model:
        raise ValueError(f"Таблиця {table_name} не знайдена.")
    return model


def add_data(table_name, data_dict):
    model = get_model(table_name)
    new_record = model(**data_dict)
    session.add(new_record)
    session.commit()
    return new_record


def read_data(table_name, filters=None):
    model = get_model(table_name)

    # Виконуємо запит до таблиці
    query = session.query(model).all()

    # Отримуємо назви колонок
    columns = [column.name for column in model.__table__.columns]

    # Формуємо список записів
    records = [
        {column: getattr(row, column) for column in columns}
        for row in query
    ]

    return records, columns


def update_data(table_name, record_id, updates):
    model = get_model(table_name)

    try:
        record = session.query(model).get(record_id)

        if record is None:
            raise ValueError(f"Запис із ID {record_id} не знайдено у таблиці {table_name}.")

        for column, value in updates.items():
            if not hasattr(record, column):
                raise ValueError(f"Колонка '{column}' не існує в таблиці {table_name}.")
            setattr(record, column, value)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def delete_data(table_name, record_id):
    model = get_model(table_name)

    try:
        record = session.query(model).get(record_id)

        if record is None:
            raise ValueError(f"Запис із ID {record_id} не знайдено у таблиці {table_name}.")

        session.delete(record)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

# class Model:
#     def __init__(self):
#         self.conn = psycopg.connect(
#             dbname='lab1',
#             user='postgres',
#             password='Vfdgjxrf1!',
#             host='localhost',
#             port=5432
#         )
#
#     def get_all_tables(self): # повертає усі таблиці в базі данних
#         c = self.conn.cursor()
#         c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
#         tables = [table[0] for table in c.fetchall()]
#         return tables
#
#     def get_all_columns(self, table_name): # повертає усі колонки у відповідній таблиці
#         c = self.conn.cursor()
#         c.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position", (table_name,))
#         columns = [row[0] for row in c.fetchall()]
#         return columns
#
#     def get_all_column_types(self, table_name, columns) -> dict: # повертає усі колонки і типи колонок у вигляді словника
#         column_types = {}
#         with self.conn.cursor() as cursor:
#             cursor.execute("""
#                 SELECT column_name, data_type
#                 FROM information_schema.columns
#                 WHERE table_name = %s AND column_name = ANY(%s);
#             """, (table_name, columns))
#
#             for column_name, data_type in cursor.fetchall():
#                 column_types[column_name] = data_type
#
#         return column_types
#
#     def get_foreign_keys(self, table): # повертає усі зовнішні ключі для відповідної таблиці
#         query = f"""
#             SELECT
#                 kcu.column_name,
#                 ccu.table_name AS referenced_table
#             FROM
#                 information_schema.table_constraints AS tc
#                 JOIN information_schema.key_column_usage AS kcu
#                     ON tc.constraint_name = kcu.constraint_name
#                 JOIN information_schema.constraint_column_usage AS ccu
#                     ON ccu.constraint_name = tc.constraint_name
#             WHERE tc.table_name = '{table}' AND tc.constraint_type = 'FOREIGN KEY';
#         """
#         c = self.conn.cursor()
#         c.execute(query)
#         foreign_keys = {row[0]: row[1] for row in c.fetchall()}
#         return foreign_keys
#
#     def add_data(self, table, columns, val): # додає дані до таблиці
#         c = self.conn.cursor()
#         columns_str = ', '.join(columns)
#         placeholders = ', '.join(['%s'] * len(val))
#         try:
#             c.execute(f'INSERT INTO "public"."{table}" ({columns_str}) VALUES ({placeholders})', val)
#             self.conn.commit()
#             return "all done"
#         except Exception as e:
#             return e
#
#     def read_data(self, table): # повертає дані з таблиці
#         table_temp = table
#         if table == 'users' or table == 'exercises':
#             table_temp = table_temp[:-1]
#         try:
#             c = self.conn.cursor()
#             c.execute(f'SELECT * FROM {table}')
#             return c.fetchall()
#         except Exception as e:
#             print(e)
#
#     def delete_data(self, table, id): # видаляє дані з таблиці
#         table_temp = table
#         if table == 'users' or table == 'exercises':
#             table_temp = table_temp[:-1]
#         try:
#             c = self.conn.cursor()
#             c.execute(f'DELETE FROM {table} WHERE {table_temp}_id = %s', (id,))
#             self.conn.commit()
#             return "all done"
#         except Exception as e:
#             return e
#
#     def update_data(self, table, columns, id, new_values): # оновлює дані в таблиці
#         if len(columns) > 1:
#             columns_str = '=%s, '.join(columns).strip() + "=%s"
#         else:
#             columns_str = columns[0] + "=%s"
#         table_temp = table
#         if table == 'users' or table == 'exercises':
#             table_temp = table_temp[:-1]
#         try:
#             c = self.conn.cursor()
#             c.execute(f'UPDATE {table} SET {columns_str} WHERE {table_temp}_id=%s', (*new_values, id,))
#             self.conn.commit()
#             return "all done"
#         except Exception as e:
#             return e
#
#
#     def find_training_first(self, user_weight, exercise_name): # пошук тренування
#         try:
#             c = self.conn.cursor()
#             sql = f"""
#                 SELECT DISTINCT t.training_id, t.start_date_time, t.end_date_time
#                 FROM training t
#                 JOIN users u ON t.user_id = u.user_id
#                 JOIN workout w ON t.training_id = w.training_id
#                 JOIN exercises e ON w.exercise_id = e.exercise_id
#                 WHERE u.user_weight = {user_weight}
#                 AND e.exercise_name = '{exercise_name}';
#                 """
#             start_time = time.time()
#             c.execute(sql)
#             elapsed_time = time.time() - start_time
#             res_time_string = f"Час виконання запиту: {elapsed_time:.4f} секунд"
#             columns = []
#             columns.append("training_id")
#             columns.append("start_date_time")
#             columns.append("end_date_time")
#             return c.fetchall(), columns, res_time_string
#         except Exception as e:
#             print(e)
#             return [], []
#
#     def find_exercise_name(self, number_of_sets, difficulty): # пошук вправи
#         try:
#             c = self.conn.cursor()
#             sql = f"""
#                 SELECT DISTINCT e.exercise_name, e.difficulty, w.number_of_sets FROM exercises e
#                 JOIN workout w ON e.exercise_id = w.exercise_id
#                 WHERE w.number_of_sets = %s AND e.difficulty = %s;
#                 """
#
#             columns = []
#             columns.append("exercise_name")
#             columns.append("difficulty")
#             columns.append("number_of_sets")
#             start_time = time.time()
#             c.execute(sql, (number_of_sets, difficulty))
#             elapsed_time = time.time() - start_time
#             res_time_string = f"Час виконання запиту: {elapsed_time:.4f} секунд"
#             return c.fetchall(), columns, res_time_string
#         except Exception as e:
#             print(e)
#             return [], []
#
#     def find_avg_exercises(self, date): # пошук середних показників для тренувань
#         try:
#             c = self.conn.cursor()
#             sql = f"""
#                 SELECT
#                     t.start_date_time,
#                     AVG(w.number_of_sets) AS avg_sets,
#                     AVG(w.number_of_repetitions) AS avg_reps
#                 FROM
#                     training t
#                 JOIN
#                     workout w ON t.training_id = w.training_id
#                 WHERE
#                     t.start_date_time >= '{date}'
#                 GROUP BY
#                     t.start_date_time
#                 ORDER BY
#                     t.start_date_time DESC;
#                 """
#
#             columns = []
#             columns.append("exercise_name")
#             columns.append("difficulty")
#             columns.append("number_of_sets")
#             start_time = time.time()
#             c.execute(sql)
#             elapsed_time = time.time() - start_time
#             res_time_string = f"Час виконання запиту: {elapsed_time:.4f} секунд"
#             return c.fetchall(), columns, res_time_string
#         except Exception as e:
#             print(e)
#             return [], []
