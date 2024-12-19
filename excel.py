import pandas as pd
import os

class Excel:
    df: pd.DataFrame
    path = os.getcwd() + "/Документы/Таблицы/"

    if not os.path.exists(path):
        os.makedirs(path)

    @classmethod
    def fromSQLtoExcel(cls, table: str, file: str, conn):
        try:
            query = 'SELECT * FROM ' + table
            cls.df = pd.read_sql(query, conn)
            path = cls.path + file
            return cls.df.to_excel(path, index=False)
        except:
            pass