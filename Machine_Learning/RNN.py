# env\Scripts\activate
# when querying
# .header on
# .mode column
import sqlite3
from sqlite3 import Error
import pandas as pd

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn
def clean_results(df):
  for col in df.columns:
    if col =='item_name': 
      continue
    if df[col].dtypes in ['int64','str']: 
      continue
    df[col] = df[col].apply(lambda x: int.from_bytes(x,byteorder='little'))
  return df
def select_table(db,table):
  conn = create_connection(db)
  with conn:
    table = 'rsbuddy'
    # item_ids = [2]
    # item_ids = ",".join(str(v) for v in item_ids)
    sql = f'select * from {table};'
    df = pd.read_sql_query(sql,conn)
    df = clean_results(df)
  return df
table='rsbuddy'
db = r'D:\random\python\OSRS_Prices\OSRS_DataSet\OSRS_Data\osrs.db'
df = select_table(db,table)
df.head()