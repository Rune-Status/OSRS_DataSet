from osrsbox import items_api
import requests
import json
import pandas as pd

def get_wiki_item_price(item_name,item_id,df):
  if df.empty:
    df = pd.DataFrame(columns=['ts','price','volume'])
  URL= f'https://oldschool.runescape.wiki/w/Module:Exchange/{item_name}/Data?action=raw'
  print(f'Requesting: {URL}')
  r=requests.get(URL)
  data = r.text.replace(' ','').replace('return{','').replace('}','').replace('\n','').replace("'",'').split(',')
  
  for row in data:
    row_data = row.split(':')
    if len(row_data) ==3:
      df = df.append({'ts':row_data[0],'price':row_data[1],'volume':row_data[2]},ignore_index=True)
    if len(row_data) ==2:
      df =df.append({'ts':row_data[0],'price':row_data[1],'volume':''},ignore_index=True)
  df['item'] = item_name
  df['item_id'] = item_id
  return df

df=pd.DataFrame()
items = items_api.load()
for item in items:
  if item.tradeable_on_ge:
    df = get_wiki_item_price(item.name,item.id,df)
    print(f'Total shape: {df.shape}')
df