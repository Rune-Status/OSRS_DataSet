# osrs_scripts\Scripts\activate
import requests
import time
import pandas as pd
#import fastparquet as pq

def check_response(resp,sec=5):
  if resp.text=="":
    print(f'sleeping {sec} seconds')
    time.sleep(sec)
    return True
  return False

def clean_data(x):
  if isinstance(x, str):
    return x.replace('k', '000').replace('m', '000000').replace('b', '000000000').replace(',', '').replace('.', '').replace('+', '').replace('- ', '-')
  return(x)

def get_prices_osrs(item_id):
  # Make API request
  Graph_URL="http://services.runescape.com/m=itemdb_oldschool/api/graph/"
  URL=Graph_URL+str(item_id)+".json"
  resp = requests.get(URL)
  # Check if valid response
  if(check_response(resp)): return get_prices_osrs(item_id)

  df = pd.DataFrame.from_dict(resp.json()).reset_index()
  df.rename(columns={"index":"ts"},inplace=True)
  df['ts'] = pd.to_datetime(df['ts'], unit='ms')
  df['item_id'] = item_id
  return df
def get_prices_rsbuddy(item_id,granularity):
  # Make API request
  base_url="https://rsbuddy.com/exchange/graphs/"
  URL=base_url+str(granularity)+"/"+str(item_id)+".json"
  resp=requests.get(URL)

  # Check if valid response
  if(check_response(resp)): return get_prices_rsbuddy(item_id,granularity)
  if(resp.status_code!=200): return pd.DataFrame({'item_id':[item_id]} )

  # Data cleaning
  df = pd.DataFrame.from_dict(resp.json())
  df['ts'] = pd.to_datetime(df['ts'], unit='ms')
  df['ts_day'] = df['ts'].apply(lambda x:x.date().strftime('%Y-%m-%d'))
  df['item_id'] = item_id
  
  return df

def get_item_from_page(letter,page):
  # Make API request
  API_URL="http://services.runescape.com/m=itemdb_oldschool/api/catalogue/items.json?category=1"
  URL=API_URL+"&alpha="+str(letter)+"&page="+str(page)
  resp=requests.get(URL)

  # Check if valid response
  if check_response(resp): return get_item_from_page(letter,page)
  if len(resp.json()["items"])==0: return False,pd.DataFrame()

  # Unpacking json
  df = pd.DataFrame()
  for item in resp.json()["items"]:
    df = pd.concat([df, pd.DataFrame.from_dict(item).drop('trend').reset_index()], ignore_index=True)

  # Data cleaning
  df.drop(columns=['icon','icon_large','typeIcon','index'],inplace=True)
  df['current'] = df['current'].apply(clean_data).astype('float')
  df['today'] = df['today'].apply(clean_data).astype('float')
  
  return True,df
def run(data_store,path):
  for unicode_letter in range(97,122):
    page=1
    while True:
      # get Each items of the osrs page (12 items)
      myTrue,df = get_item_from_page(chr(unicode_letter),page)
      if not(myTrue): break
      
      print(f'Char: {chr(unicode_letter)}, Page: {page}, CountItems: {len(list(df.name))}')

      # Get from each item rsbuddy data 
      rsbuddy_df = pd.DataFrame()
      for item_id in df.id:
        if(rsbuddy_df.empty):
          rsbuddy_df = get_prices_rsbuddy(item_id,30) 
        else:
          rsbuddy_df = pd.concat([rsbuddy_df,get_prices_rsbuddy(item_id,30)],sort=False)

      # merge osrs data and rs buddy data
      output = df.merge(rsbuddy_df,
                      left_on='id',
                      right_on='item_id',
                      how='left',
                      sort=False)

      # store the merged dataFrame
      if(data_store.empty):
        #print('***********data_store is empty***********')
        data_store = output 
      else:
        data_store = pd.concat([data_store, output],sort=False)
      print(f'  data_store shape: {data_store.shape}')
      page+=1
  data_store.drop_duplicates(keep='last',inplace=True)
  data_store.to_csv('data_store.csv')
path=''
try:
  data_store = pd.read_csv('data_store.csv')
except:
  data_store = pd.DataFrame()

run(data_store,path)

