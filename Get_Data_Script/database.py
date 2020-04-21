import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_rsbuddy(conn, row):
    sql = ''' INSERT INTO rsbuddy(item_name,item_id,ts,overallPrice,overallQuantity,buyingPrice,buyingQuantity,sellingPrice,sellingQuantity)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, row)
    return cur.lastrowid

def main():
    database = r'D:\random\python\OSRS_Prices\OSRS_DataSet\OSRS_Data\osrs.db'

    # create a database connection
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        
        sql_create_rsbuddy = """ CREATE TABLE IF NOT EXISTS rsbuddy (
                                        id integer PRIMARY KEY,
                                        item_name text,
                                        item_id integer,
                                        ts integer,
                                        overallPrice integer,
                                        overallQuantity integer,
                                        buyingPrice integer,
                                        buyingQuantity integer,
                                        sellingPrice integer,
                                        sellingQuantity integer
                                    ); """
        create_table(conn,sql_create_rsbuddy)
        rsbuddy = ('test',1,2,3,4,5,6,7,8)
        insert_rsbuddy(conn,rsbuddy)

if __name__ == '__main__':
    main()