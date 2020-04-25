# env\Scripts\activate
from osrsbox import items_api
import concurrent.futures
import requests
import json
import os
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def insert_rsbuddy(conn, row):
    sql = ''' INSERT INTO rsbuddy(item_name,item_id,ts,overallPrice,overallQuantity,buyingPrice,buyingQuantity,sellingPrice,sellingQuantity)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, row)
    return cur.lastrowid


def make_web_call(URL, item_name, item_id):
    print(f'Requesting: {URL}')
    r = requests.get(URL)
    return r


def get_rsbuddy_price(r, item_name, item_id):
    data = r.json()
    database = r'D:\random\python\OSRS_Prices\OSRS_DataSet\OSRS_Data\osrs.db'
    conn = create_connection(database)

    for row in data:
        rsbuddy = [
            item_name.replace("'", ''),
            item_id,
            row['ts'],
            row['overallPrice'],
            row['overallQuantity'],
            row['buyingPrice'],
            row['buyingQuantity'],
            row['sellingPrice'],
            row['sellingQuantity']
        ]
        try:
            insert_rsbuddy(conn, rsbuddy)
        except Error:
            print(f'Got Error: {row["ts"]},{item_id}, {Error}')
            pass


def main(granularity=30):
    URLS = [[f'https://rsbuddy.com/exchange/graphs/{granularity}/{item.id}.json',
             item.name, item.id] for item in items_api.load() if item.tradeable_on_ge]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_url = {executor.submit(
            make_web_call, url[0], url[1], url[2]): url for url in URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                # Output,item.name, item.id
                get_rsbuddy_price(data, url[1], url[2])
            except Exception as exc:
                print(f'URL: {url}, generated an exception: {exc}')

if __name__ == '__main__':
    main()
