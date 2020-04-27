# env\Scripts\activate
# when querying
# .header on
# .mode column

import sqlite3
from sqlite3 import Error
import pandas as pd
from sklearn import preprocessing
from collections import deque
import numpy as np
import random
import time
import tensorflow as tf 
from tensorflow.keras.models import sequential 
from tensorflow.keras.layers import Dense, Dropout, LSTM, CuDNNLSTM, BatchNormalization
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def select_table_by_item_id(db, table, item_ids):
  conn = create_connection(db)
  with conn:
    table = 'rsbuddy'
    item_ids = ",".join(str(v) for v in item_ids)
    sql = f'select * from {table} where item_id in ({item_ids});'
    df = pd.read_sql_query(sql, conn)
  return df


table = 'rsbuddy'
db = r'D:\random\python\OSRS_Prices\OSRS_DataSet\OSRS_Data\osrs.db'

SEQ_LEN = 100
FUTURE_PERIOD_PREDICT = 3
ITEM_TO_PREDICT = 2
EPOCHS = 10
BATCH_SIZE = 64
NAME = f'{SEQ_LEN}-SEQ-{FUTURE_PERIOD_PREDICT}-PRED-{int(time.time())}'

def classify(current, future):
  if int(future) > int(current):
    return 1  # buy
  else:
    return 0  # sell


def preprocess_df(df):
	df = df.drop('future', 1)
	for col in df.columns:
		if col != 'target':
			# normalizing
			df[col] = df[col].pct_change()
			df.dropna(inplace=True)
			df[col] = preprocessing.scale(df[col].values)
	df.dropna(inplace=True)

	sequential_data = []
	prev_days = deque(maxlen=SEQ_LEN)  # makes a list with a certain length

	for i in df.values:
		# append a row from df excluding the last column
		prev_days.append([n for n in i[:-1]])
		if len(prev_days) == SEQ_LEN:
			sequential_data.append([np.array(prev_days), i[-1]])

	random.shuffle(sequential_data)

	# balancing buy & sell
	buys = []
	sells = []

	for seq, target in sequential_data:
		if target == 0:
			sells.append([seq, target])
		elif target == 1:
			buys.append([seq, target])

	random.shuffle(buys)
	random.shuffle(sells)

	lower = min(len(buys), len(sells))

	buys = buys[:lower]
	sells = sells[:lower]

	sequential_data = buys+sells
	random.shuffle(sequential_data)

	x = []
	y = []

	for seq, target in sequential_data:
		x.append(seq)
		y.append(target)
	
	return np.array(x), y

main_df = pd.DataFrame()
items= [2,245,1515]


for item in items:
  df = select_table_by_item_id(db,table,[item])
  df.drop(columns=['id','item_id','item_name','buyingPrice', 'buyingQuantity', 'sellingPrice', 'sellingQuantity'],inplace=True)
  df.rename(columns={'overallPrice':f'{item}_price','overallQuantity':f'{item}_volume'},inplace=True)
  df.set_index('ts',inplace=True)
  if len(main_df)==0:
    main_df = df
  else:
    main_df = main_df.join(df)

main_df.dropna(inplace=True)
for col in main_df.columns:
  main_df[col] = main_df[col].astype(int)

COLUMN_TO_PREDICT = 'price'
main_df['future'] = main_df[f'{ITEM_TO_PREDICT}_{COLUMN_TO_PREDICT}'].shift(-FUTURE_PERIOD_PREDICT)

main_df.dropna(inplace=True)
main_df['future'] = main_df['future'].astype(int)

main_df['target'] = list(map(classify,main_df[f'{ITEM_TO_PREDICT}_{COLUMN_TO_PREDICT}'],main_df['future']))

# print(main_df.dtypes)
# print(main_df.head(10))

times = sorted(main_df.index.values)
last_5pct = times[-int(0.05*len(times))]
 
# splitting validaiton
validation_main_df = main_df[(main_df.index >= last_5pct)]
main_df = main_df[(main_df.index < last_5pct)]

train_x, train_y = preprocess_df(main_df)
validation_x, validation_y = preprocess_df(validation_main_df)

print(f'Train data: {len(train_x)} Validation: {len(validation_x)}')
print(f'Dont buys: {train_y.count(0)}, buys: {train_y.count(1)}')
print(f'Validation dont buys: {validation_y.count(0)}, buys: {validation_y.count(1)}')