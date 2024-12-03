from utils.logger import Logger
import sqlite3
from threading import Lock


class Db():
    def __init__(self):
        self._logger = Logger().get_logger(__name__)
        self.conn = sqlite3.connect('rpc.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = Lock()
        self.table_name = 'keys'
        self.table_structure = [
            {'name': 'rpc', 'spec': 'VARCHAR(255)', 'default': ''},
            {'name': 'moniker', 'spec': 'VARCHAR(255)', 'default': ''}
        ]
        self.create_db()

    def create_table(self, name: str, fields: list):
        sql = f"CREATE TABLE IF NOT EXISTS {name} ("
        comma = ""
        for field in fields:
            sql += comma + field
            if comma == "": comma = ","
        sql += ")"
        try:
            self.cursor.execute(sql)
        except Exception as e:
            self._logger.error(f'SQL: {sql}')
            
    def commit(self, sql: str):       
        try:
            self.lock.acquire(True)
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self._logger.error(f'SQL: {sql}')
        finally:
            self.lock.release()
        
    def get_data(self, sql: str) -> list:       
        try:
            self.lock.acquire(True)
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            self._logger.error(f'SQL: {sql}')  
        finally:
            self.lock.release()

    def insert(self, values: dict):
        sql_field_str = ', '.join(values)
        sql_value_list = [f"'{val}'" for val in values.values()]
        sql_value_str = ', '.join(sql_value_list)
        sql_values = (self.table_name, sql_field_str, sql_value_str)
        self.commit('INSERT INTO %s (%s) VALUES (%s)' % sql_values)

    def create_db(self):
        create_structure = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for column in self.table_structure:
            t_string = f'{column["name"]} {column["spec"]}'
            create_structure.append(t_string)
        self.create_table(self.table_name, create_structure)

    def get_table_fields(self) -> list:
        fields = ['id']
        for column in self.table_structure:
            fields.append(column['name'])
        return fields
    
    def get_raw(self, condition: str, order: str = 'DESC') -> list:
        sql_fields = ', '.join(self.get_table_fields())
        sql_values = (sql_fields, self.table_name, condition, 'id', order)
        sql = 'SELECT %s FROM %s WHERE %s ORDER BY %s %s' % sql_values
        sql_records = self.get_data(sql)
        return sql_records

    def select(self, condition: str='id > 0', order='DESC') -> list:
        raw_data = self.get_raw(condition, order)
        refined_data = self.refine_raw_data(raw_data)
        return refined_data

    def refine_raw_data(self, raw_data: list) -> list:
        if not raw_data: return []
        refined_data = []
        table_fields = self.get_table_fields()
        for row in raw_data:
            refined_row = {}
            for index, cell in enumerate(row):
                refined_row[table_fields[index]] = cell
            refined_data.append(refined_row)
        return refined_data
    
    def does_record_exist(self, condition: str) -> bool:
        sql = 'SELECT * FROM %s WHERE %s' % (self.table_name, condition)
        result = self.get_data(sql)
        return len(result) > 0
