# env\Scripts\activate
from bs4 import BeautifulSoup
import requests
import json
import time
import os


def get_url(display, interval, total, mid):
    return f'http://www.misplaceditems.com/rs_tools/graph/?display={display[0]}&interval={interval[0]}&total={total[0]}&mid={mid}'


def make_web_call(URL):
    if URL not in URL_Checklist:
        URL_Checklist.append(URL)
    else:
        print(f'Duplicate Request: {URL}')
        return False
    print(f'Requesting: {URL}')
    r = requests.get(URL)
    return r


def parse_data(resp, d):
    if not(resp):
        return d
    soup = BeautifulSoup(resp.text, 'html.parser')

    script_text = soup.findAll('script')[8].get_text()
    jsonfile = script_text.split('\n')[5].replace('var db_data = ', '').replace(';', '').strip()

    jsonfile = json.loads(jsonfile)
    i = len(d)
    dts = [row['ts'] for row in d.values()]
    for row in jsonfile['osrs']:
        if row[0] in dts:
            continue
        d.update({i: {
            'ts': row[0],
            'playercount': row[1]
        }})
        i += 1

    dts = [row['ts'] for row in d.values()]
    if jsonfile['osrs'][-1][0]-15*60*1000 not in dts:
        URL = get_url(display, interval, total,
                      (jsonfile['osrs'][-1][0]-15*60*1000)/1000)
        d = parse_data(make_web_call(URL), d)
    else:
        print('Data Already available')
    return d


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


def main():
    URL = get_url(display, interval, total, mid)
    d = load_data(file_path, file_name)
    d = parse_data(make_web_call(URL), d)
    save_data(d, file_path, file_name)
    print('done')


# Lambda functions
def unix_qtr_hr(x): return x-divmod(x, 15*60)[1]


# Global variables
URL_Checklist = []
file_path = r'D:\random\python\OSRS_Prices\OSRS_DataSet\OSRS_Data'
file_name = 'playercount'
display = ['avg', 'max']
interval = ['qtr_hr', 'hr', 'day', 'week', 'month', 'qtr_yr']
total = [0, 1]
mid = unix_qtr_hr(time.time())
main()
