from osrsbox import items_api
import concurrent.futures
import requests
import json
import os


def make_web_call(URL, item_name, item_id):
    print(f'Requesting: {URL}')
    r = requests.get(URL)
    return r

def get_rsbuddy_price(r, item_name, item_id, d):
    data = r.json()
    i = len(d)
    for row in data:
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

def main(d={},granularity = 30):
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
                    print('%r generated an exception: %s' % (url, exc))
    return d

if __name__ == '__main__':
    d= main()
    with open('rsbuddy.json', 'w') as fp:
        json.dump(d, fp)
    print('done')
