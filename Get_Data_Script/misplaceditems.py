from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time
import os.path

def ts_to_unix(date):
  return (date - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s') 

def dateparse(x):
  return pd.to_datetime(int(x/1000), unit='s').round('15min')

def get_player_count(display,interval,total,mid,output,retry=True):
  if (output.empty):
    print('output is empty')
    output = pd.DataFrame(columns=['ts','player_count'])
  
  URL=f'http://www.misplaceditems.com/rs_tools/graph/?display={display[0]}&interval={interval[0]}&total={total[0]}&mid={mid}'
  print(f'Requesting: {URL}')
  resp = requests.get(URL)
  soup = BeautifulSoup(resp.text, 'html.parser')

  script_text = soup.findAll('script')[8].get_text()
  jsonfile = script_text.split('\n')[5].replace('var db_data = ','').replace(';','').strip()

  jsonfile = json.loads(jsonfile)

  df = pd.DataFrame.from_dict(jsonfile)
  result = pd.DataFrame()
  
  for row in df['osrs']:
    result = result.append({'ts':row[0],'player_count':row[1]},ignore_index=True)

  result['ts'] = result['ts'].astype(float)

  if(output.empty):
    print('Output is empty')
    output = pd.concat([output,result],sort=True)
    return get_player_count(display,interval,total,min(result['ts'])/1000,output)

  cnt = output[output['ts'].isin({min(result['ts'])})].count().values[0]
  if(cnt==0):
    print(f'  {dateparse(min(result["ts"]))} is not in min: {dateparse(min(output["ts"]))} max: {dateparse(max(output["ts"]))}')
    output = pd.concat([output,result],sort=True)
    return get_player_count(display,interval,total,min(result['ts'])/1000,output,retry=True)
  
  print(f'  {dateparse(min(result["ts"]))} is in min: {dateparse(min(output["ts"]))} max: {dateparse(max(output["ts"]))}')
  
  if(retry):
    output = pd.concat([output,result],sort=True)
    print(f'  Retrying with date: {dateparse((min(output["ts"])-3600000))}')
    return get_player_count(display,interval,total,min(output['ts'])/1000-3600,output,retry=False)

  output = pd.concat([output,result],sort=True)
  return output

display = ['avg','max']
interval = ['qtr_hr','hr','day','week','month','qtr_yr']
total = [0,1]
mid= ts_to_unix(pd.to_datetime(int(time.time()), unit='s').round('15min')) # this can probably be cleaner

if os.path.isfile('player_count.csv'):
    print ("File exist")
    output = pd.read_csv('player_count.csv')
    output['player_count'] = output['player_count'].astype(float)
else:
    print ("File not exist")
    output = pd.DataFrame()

player_count = get_player_count(display,interval,total,mid,output)
player_count.drop_duplicates(keep='last',inplace=True)
player_count.to_csv('player_count.csv',index=False)
print('**done**')