import codecs
from os import stat
import sqlite3
from sqlite3.dbapi2 import connect


from sys import modules
from string import Template

def init():
    pass

class SqlManager():    
    DATA_TYPES = {
        "int": "INTEGER",
        "string": "VARCHAR(256)",
        "binary": "BINARY(64)"
    }

    KEYWORDS = {
        "null": ("NULL", "NOT NULL"),
        "unique": ("UNIQUE", ""),
        "auto increment": ("AUTO_INCREMENT", "")
    }

    def __init__(self, file="../database.db"):
        self.db = sqlite3.connect(file, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        self.tables = {}
        
    def add_table(self, name, table):
        self.tables[name] = table

    def create_tables(self):
        for table_name, table in self.tables.items():
            current_table_obj = SqlManager.Table(table_name, self)
            query = f"CREATE TABLE IF NOT EXISTS {table_name}("
            keys = []
            keywords = []
            for var_name, attributes in table["vars"].items():
                keywords.append(var_name)
                if "key" in attributes:
                    keys.append(var_name)
                if "constraint" in attributes:
                    current_table_obj.add_constraint(var_name, attributes["constraint"])
                query += var_name + " " + SqlManager.DATA_TYPES[attributes["type"]]
                query += SqlManager.check_keywords(attributes)
                query += ", "
            if len(keys) < 1:
                query += "id INTEGER PRIMARY KEY AUTOINCREMENT"
                keywords.append("id")
            else:
                query += "PRIMARY KEY(" + ''.join([key + "," for key in keys])
                query = query[:-1] + ")"
            query += ")"
            self.cursor.execute(query)
            current_table_obj.add_keywords(keywords)
            modules[__name__].__dict__[table_name] = current_table_obj
        self.create_connections()

    def create_connections(self):
        for table_name, table_data in self.tables.items():
            table = modules[__name__].__dict__[table_name]
            new_keys = []
            if "connected" in table_data:
                for connected_table in table_data["connected"]:
                    key = SqlManager.create_foreign_key_name(connected_table)
                    if not table.column_exists(key):
                        table.add_to(
                            f"{key} INTEGER REFERENCES {connected_table}(id) ON DELETE SET DEFAULT"
                        )
                    new_keys.append(key)
            if "depends" in table_data:
                for dependant_table in table_data["depends"]:
                    key = SqlManager.create_foreign_key_name(dependant_table)
                    if not table.column_exists(key):
                        table.add_to(f"{key} INTEGER NOT NULL DEFAULT 0 REFERENCES {dependant_table}(id) ON DELETE CASCADE")
                    new_keys.append(key)
            table.add_keywords(new_keys)

    @staticmethod
    def add_limit(limit):
        if limit > 0:
            return f" LIMIT {limit}"
        return ""

    @staticmethod
    def interrupt_if_unsafe(val):
        if SqlManager.is_in_str(val, "'",  "\n", "\0", "%"):
            raise SqlManager.InvalidSqlStringError()

    @staticmethod
    def check_keywords(attributes):
        add = ""
        for name, options in SqlManager.KEYWORDS.items():
            if name in attributes:
                add += " " + SqlManager.check_keyword(attributes, name, *options)
        if "default" in attributes:
            add += " DEFAULT " + SqlManager.to_sql_val(attributes["default"])
        return add

    @staticmethod
    def check_keyword(attributes, name, true, false):
        if name in attributes:
            val = attributes[name]
            return true if val else false

    @staticmethod
    def t_str(template_str, **kwargs):
        return Template(template_str).substitute(**kwargs)

    @staticmethod
    def get_query(formatted_str, *args):
        for i in args:
            formatted_str = formatted_str.replace("%s", f"'{i}'", 1)
        print(formatted_str)

    @staticmethod
    def to_sql_val(val):
        if type(val) is int:
            return str(val)
        if type(val) is str:
            return SqlManager.quote_identifier(val)
        if type(val) is bytes:
            return SqlManager.quote_identifier(val.decode("ascii"))
        raise SqlManager.UnknownTypeError()

    @staticmethod
    def quote_identifier(s, errors="strict"):
        return "\"" + SqlManager.identify_quote_without_commas(s, errors) + "\""

    @staticmethod
    def identify_quote_without_commas(s, errors="strict"):
        encodable = s.encode("utf-8", errors).decode("utf-8")

        nul_index = encodable.find("\x00")

        if nul_index >= 0:
            error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                    nul_index, nul_index + 1, "NUL not allowed")
            error_handler = codecs.lookup_error(errors)
            replacement, _ = error_handler(error)
            encodable = encodable.replace("\x00", replacement)

        return encodable.replace("\"", "\"\"")

    #@staticmethod
    #def to_sql_str(val):
    #    SqlManager.interrupt_if_unsafe(val)
    #    return "'" + val + "'"

    @staticmethod
    def is_in_str(str, *args):
        for c in str:
            if c in args:
                return True
        return False

    @staticmethod
    def create_foreign_key_name(table_name):
        return f"{table_name}_id"

    class Table:
        def __init__(self, name, sql_manager):
            self.name = name
            self.sql_manager = sql_manager
            self.constraints = {}
            self.keywords = []

        def add_keywords(self, keys):
            self.keywords += keys

        def add_column(self, name, v_type, attributes):
            if not self.column_exists(name):
                self.add_to(f"{name} {SqlManager.DATA_TYPES[v_type]}" + SqlManager.check_keywords(attributes))

        def add_to(self, query):
            self.sql_manager.cursor.execute(f"ALTER TABLE {self.name} ADD {query}")

        def column_exists(self, column):
            self.sql_manager.cursor.execute(f"PRAGMA table_info({self.name});")
            for c in self.sql_manager.cursor:
                if column == c[1]:
                    return True
            return False

        def insert(self, obj):
            after_values = "("
            query = "INSERT INTO " + self.name + "("
            for key, val in obj.items():
                query += key + ", "
                after_values += SqlManager.to_sql_val(val) + ", "
                if not self.checks_constraint(key, val):
                    raise SqlManager.VariableConstraintError(self.get_constraint_error_message(key))
            after_values = after_values[:-2] + ")"
            query = query[:-2] + ") VALUES" + after_values
            self.sql_manager.cursor.execute(query)
            self.sql_manager.db.commit()
            return self.sql_manager.cursor.lastrowid

        def edit(self, _id, **kwargs):
            if type(_id) is not int:
                return
            query = f"UPDATE {self.name} SET "
            for key, val in kwargs.items():
                query += f"{key} = {SqlManager.to_sql_val(val)}, "
            query = query[:-2] + f" WHERE id = {_id}"
            self.sql_manager.cursor.execute(query)
            self.sql_manager.db.commit()

        def delete(self, _id):
            query = f"DELETE FROM {self.name} WHERE id = " + SqlManager.to_sql_val(_id)
            self.sql_manager.cursor.execute(query)
            self.sql_manager.db.commit()

        def get(self, _id):
            return self.get_mul(_id)[0]

        def get_mul(self, *ids):
            query = f"SELECT * FROM {self.name} WHERE id IN ("
            for _id in ids:
                if type(_id) is not int:
                    return
                query += str(_id) + ","
            query = query[:-1] + ")"
            return self.execute_get_query(query)

        def get_all(self, limit=0):
            query = f"SELECT * FROM {self.name}"
            query += SqlManager.add_limit(limit)
            return self.execute_get_query(query)
        
        def get_with(self, **kwargs):
            query = f"SELECT * FROM {self.name} WHERE "
            for kwarg in kwargs:
                if kwarg == "ORDER_BY":
                    query += " ORDER BY " + kwargs[kwarg]
                    break
                query += kwarg + "=" + SqlManager.to_sql_val(kwargs[kwarg]) + " AND "
            else:
                query = query[:-5]
            return self.execute_get_query(query)

        def execute_get_query(self, query):
            self.sql_manager.cursor.execute(query)
            data = self.sql_manager.cursor.fetchall()
            formatted_data = []
            for row in data:
                formatted_data.append({key: row[i] for i, key in enumerate(self.keywords)})
            return formatted_data

        def search(self, var_name, val, limit=0): 
            key = SqlManager.identify_quote_without_commas(val)
            query = f"SELECT * FROM {self.name} WHERE {var_name} LIKE '%{key}%' "
            query += SqlManager.add_limit(limit)
            self.sql_manager.cursor.execute(query)
            return self.sql_manager.cursor.fetchall()

        def add_constraint(self, var_name, constraint):
            self.constraints[var_name] = constraint

        def checks_constraint(self, var_name, value):
            if var_name in self.constraints:
                return self.constraints[var_name]["func"](value)
            return True

        def get_constraint_error_message(self, var_name):
            return self.constraints[var_name]["error_message"]

    # Errors
    # DatabaseError: The database is not loaded
    # SqlQueryError: A base error for any error that occurred because of invalid data sent
    # UnknownTypeError: Given type is not valid in sql parser
    # InvalidSqlStringError: Given string contains invalid sql characters(that may cause sql injection)
    # VariableConstraintError: given objects values don't match defined constraints

    class Error(Exception):
        pass


    class DatabaseError(Error):
        pass


    class SqlQueryError(Error):
        pass


    class UnknownTypeError(SqlQueryError):
        pass


    class InvalidSqlStringError(SqlQueryError):
        pass


    class VariableConstraintError(SqlQueryError):
        pass

