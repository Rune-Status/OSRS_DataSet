import requests
from pprint import pprint
from datetime import datetime
import time
import subprocess
import sys
import csv

item_dict={}
waiting=0
waiting_list=[]
avg_waiting_time=1
# working on this part
def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])
    
def store_data(api_name,row):
    datenow = datetime.now().strftime('%Y-%m-%d')
    file = datenow+ '_' + api_name +'_prices'+ '.csv'

    with open(file, 'a',newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()

def get_prices_rsbuddy(item_id,granularity):
    base_url="https://rsbuddy.com/exchange/graphs/"
    URL=base_url+str(granularity)+"/"+str(item_id)+".json"
    r=requests.get(URL)
    data=r.json()
	
    for i in range(len(data)):
        ts=data[i]["ts"]
        # the timestamp (ts) is definedd in miliseconds, utc only in seconds
        date=date=datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S')
        buyprice=data[i]["buyingPrice"]
        sellprice=data[i]["sellingPrice"]
        buyquantity=data[i]["buyingQuantity"]
        sellquantity=data[i]["sellingQuantity"]
        row = [item_id,date,buyprice,sellprice,buyquantity,sellquantity]
        store_data('rsbuddy',row)
        print(row)

def get_prices_osrs(item_id):
    global avg_waiting_time
    global waiting_list
    global waiting
    Graph_URL="http://services.runescape.com/m=itemdb_oldschool/api/graph/"
    URL=Graph_URL+str(item_id)+".json"
    r = requests.get(URL)
    # if we do to many calls then we get an empty response of the server and have to redo our call
    # i do not know what the api limit is so 
    # if i hit the limit i make my script wait the average time it had to wait in the past
    if r.text=="":
        time.sleep(avg_waiting_time)
        waiting+=avg_waiting_time
        return get_prices_osrs(item_id)
    if waiting!=0:                      
        waiting_list.append(waiting)
        avg_waiting_time=sum(waiting_list[-10:])/len(waiting_list[-10:])
        waiting=0
        
    data=r.json()["daily"]
    for key,value in data.items():
        # the timestamp (ts) is definedd in miliseconds, utc only in seconds
        ts=int(key)/1000
        date=datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d') #%H:%M:%S
        # store this data in database
        row = [item_id,date,value]
        store_data('osrs',row)
        print(row)
        
def get_item_from_page(letter,page,osrs):
    global item_dict
    global avg_waiting_time
    global waiting_list
    global waiting
    API_URL="http://services.runescape.com/m=itemdb_oldschool/api/catalogue/items.json?category=1"
    URL=API_URL+"&alpha="+str(letter)+"&page="+str(page)
    r=requests.get(URL)
    # if we do to many calls then we get an empty response of the server and have to redo our call
    # i do not know what the api limit is so 
    # if i hit the limit i make my script wait the average time it had to wait in the past
    if r.text=="":
        time.sleep(avg_waiting_time)
        waiting+=avg_waiting_time
        return get_item_from_page(letter,page,0)
    if waiting!=0:                      
        waiting_list.append(waiting)
        avg_waiting_time=sum(waiting_list[-10:])/len(waiting_list[-10:])
        print(avg_waiting_time)
        waiting=0
        
    data=r.json()["items"]
    if len(data)==0:
        # print("next page letter")
        return 0
    else:
        for item in data:
            try:
                #write item["id"] & item["name"] to database
                print(item["id"],item["name"])
                if osrs==1:
					# get the prices of the last 180 days for that item
                    get_prices_osrs(item["id"])
                get_prices_rsbuddy(item["id"],30)
            except:
                continue
        return 1
    

for unicode_letter in range(97,122):
    letter=chr(unicode_letter)
    page=0
    while get_item_from_page(letter,page,0):
        page+=1
