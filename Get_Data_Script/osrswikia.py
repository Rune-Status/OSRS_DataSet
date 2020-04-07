from osrsbox import items_api
import requests
import json
import os
def make_web_call(URL,item_name,item_id):
  print(f'Requesting: {URL}')
  r=requests.get(URL)
  return r

def get_wiki_item_price(r,item_name,item_id,d):
  data = r.text.replace(' ','').replace('return{','').replace('}','').replace('\n','').replace("'",'').split(',')
  i =len(d)
  for row in data:
    row_data = row.split(':')
    if len(row_data) ==3:
      d.update({f"{i}":{"ts":row_data[0],"price":row_data[1],"volume":row_data[2],"item_name":item_name,"item_id":item_id}})
    if len(row_data) ==2:
      d.update({f"{i}":{"ts":row_data[0],"price":row_data[1],"volume":0,"item_name":item_name,"item_id":item_id}})
    i+=1
  return d


from osrsbox import items_api
import concurrent.futures
items = items_api.load()
d= {}
URLS = [[f'https://oldschool.runescape.wiki/w/Module:Exchange/{item.name}/Data?action=raw',item.name,item.id] for item in items_api.load() if item.tradeable_on_ge]
if __name__ == '__main__':
  with concurrent.futures.ProcessPoolExecutor() as executor:
    future_to_url = {executor.submit(make_web_call, url[0],url[1],url[2]): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
      url = future_to_url[future]
      try:
        data= future.result()
        d = get_wiki_item_price(data,url[1],url[2],d)
      except Exception as exc:
        print('%r generated an exception: %s' % (url, exc))
  with open('osrswikia.json', 'w') as fp:
    json.dump(d, fp)
  print('done')
