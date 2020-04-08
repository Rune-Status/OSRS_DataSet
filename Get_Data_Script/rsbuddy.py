from osrsbox import items_api
import concurrent.futures
import requests
import json
import os

def load_data(file_path,file_name):
  file_name = os.path.join(file_path,file_name+ '.json')  
  if os.path.isfile(file_name):
    print ("File exist")
    with open(file_name) as json_file:
      d = json.load(json_file)
  else:
    print ("File not exist")
    d ={}
  return d

def save_data(d,file_path,file_name):
  file_name = os.path.join(file_path,file_name+ '.json') 
  with open(file_name, 'w') as fp:
    json.dump(d, fp)

def make_web_call(URL, item_name, item_id):
    print(f'Requesting: {URL}')
    r = requests.get(URL)
    return r

def get_rsbuddy_price(r, item_name, item_id, d):
    data = r.json()
    i = len(d)
    dts=[row['ts'] for row in d.values() if row['item_id']== item_id]
    for row in data:
        if row['ts'] in dts: continue
        d.update({i: {
            'item_name': item_name,
            'item_id': item_id,
            'ts': row['ts'],
            'overallPrice': row['overallPrice'],
            'overallQuantity': row['overallQuantity'],
            'buyingPrice': row['buyingPrice'],
            'buyingQuantity': row['buyingQuantity'],
            'sellingPrice': row['sellingPrice'],
            'sellingQuantity': row['sellingQuantity']}
        })
        i += 1
    return d

def main(granularity = 30):
    d = load_data(file_path,file_name)
    URLS = [[f'https://rsbuddy.com/exchange/graphs/{granularity}/{item.id}.json',item.name, item.id] for item in items_api.load() if item.tradeable_on_ge]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_url = {executor.submit(make_web_call, url[0], url[1], url[2]): url for url in URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                # Output,item.name, item.id
                d = get_rsbuddy_price(data, url[1], url[2], d)
            except Exception as exc:
                print(f'URL: {url}, generated an exception: {exc}')
    save_data(d,file_path,file_name)
    

file_path = r'D:\random\python\OSRS_Prices\OSRS_DataSet\OSRS_Data'
file_name ='rsbuddy'
if __name__ == '__main__':
    main()

