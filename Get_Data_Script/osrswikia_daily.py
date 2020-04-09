# env\Scripts\activate
# comment: ctrl+k+c
# uncomment: ctrl+k+u
from osrsbox import items_api
import concurrent.futures
import requests
import json
import os
import time


def load_data(file_path, file_name):
    file_name = os.path.join(file_path, file_name + '.json')
    if os.path.isfile(file_name):
        print("File exist")
        with open(file_name) as json_file:
            d = json.load(json_file)
    else:
        print("File not exist")
        d = {}
    return d


def save_data(d, file_path, file_name):
    file_name = os.path.join(file_path, file_name + '.json')
    with open(file_name, 'w') as fp:
        json.dump(d, fp)


def make_web_call(URL):
    print(f'Requesting: {URL}')
    r = requests.get(URL)
    if r.status_code == 200:
        return r 
    else:
        print(f'Error: {r.status_code} Request: {URL}')
        

def get_wiki_item(r, item_name, item_id, d):
    if r is None:
        return d
    data = r.text.replace(' ', '').replace('return{', '').replace('}', '').replace(',', '').replace('\n', ',').replace("'", '').split(',')
    i = len(d)
    dts = [row['ts'] for row in d.values() if row['itemId'] == item_id]
    if unix_day(time.time()) in dts:
        return d
    row_data = {row.split('=')[0]: row.split('=')[1] for row in data if row != ''}
    row_data.update({'ts': unix_day(time.time())})
    d.update({i: row_data})
    return d


def main():
    URLS = [[f'https://oldschool.runescape.wiki/w/Module:Exchange/{item.name}?action=raw', item.name, item.id] for item in items_api.load() if item.tradeable_on_ge]
    d = load_data(file_path, file_name)
    errors = {}
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_url = {executor.submit(make_web_call, url[0]): url for url in URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                d = get_wiki_item(data, url[1], url[2], d)
            except Exception as exc:
                print(f'URL: {url}, generated an exception: {exc}')
                errors.update({len(errors):{'url':url}})
    save_data(errors,file_path,f'{file_name}_errors')
    save_data(d, file_path, file_name)
    print('done')


def unix_day(x): return x-divmod(x, 24*60*60)[1]


items = items_api.load()
file_path = r'D:\random\python\OSRS_Prices\OSRS_DataSet\OSRS_Data'
file_name = 'rswiki_daily'

if __name__ == '__main__':
    main()
