import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import plotly as py
import plotly.graph_objs as go

CACHE_FNAME = 'cache.json'
DBNAME = 'realtor.db'

# sites_dumped= json.loads('sites.json')
# sites_file= open(CACHE_FNAME, 'w')
# sites_file.write(sites_dumped)
# sites_file.close()


try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def make_request_using_cache(url):
    unique_ident = url

    # first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        # print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    # if not, fetch the data afresh, add it to the cache,
    # then write the cache to file
    else:
        # print("Making a request for new data...")
        # Make the request and cache the new data
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }
        resp = requests.get(url, headers=headers, allow_redirects= False)
        prop = requests.models.Response.content
        if resp.encoding is None or resp.encoding == 'ISO-8859-1':
            resp.encoding = resp.apparent_encoding
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

try:
    conn = sqlite3.connect(DBNAME)
    print(sqlite3.version)
except:
    print('Error')
conn.close()

conn= sqlite3.connect(DBNAME)
cur= conn.cursor()

table= "Buy"
if table:
    user_input= input("Buy table exists. Delete? yes/no:")
    if user_input == "yes":
        cur.execute("DROP TABLE IF EXISTS 'Buy'")
        conn.commit()


statement= """
CREATE TABLE 'Buy'(
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Type' TEXT,
    'Price' TEXT,
    'Address' TEXT,
    'MoreInfo' TEXT
    );
"""
cur.execute(statement)
conn.commit()

table1= 'Rent'
if table1:
    user_input= input("Rent table exists. Delete? yes/no:")
    if user_input == "yes":
        cur.execute("DROP TABLE IF EXISTS 'Rent'")
        conn.commit()

statement= """
CREATE TABLE 'Rent'(
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Type' TEXT,
    'Price' TEXT,
    'Address' TEXT,
    'MoreInfo' TEXT
    );
"""
cur.execute(statement)
conn.commit()

tmp_len_buy=[]
def get_property_data_buy(command):
    baseurl= 'https://www.realtor.com/'
    buy= baseurl + 'realestateandhomes-search/' + command

    buy_page_text = make_request_using_cache(buy)
    buy_page_soup = BeautifulSoup(buy_page_text, 'html.parser')


    content_div = buy_page_soup.find(class_='srp-list')
    all_property_type= content_div.find_all(class_='property-type')
    all_property_price= content_div.find_all(class_='data-price')
    all_property_beds= content_div.find_all(class_='data-value meta-beds-display')
    info= content_div.find_all(class_='prop-meta ellipsis')
    addresses= content_div.find_all(class_='address ellipsis')
    total_prop= content_div.find(class_='srp-footer-found-listing')
    print(total_prop.string + ' for sale')
    tmp1= total_prop.string.split(' ')
    tmp_len_buy.append(int(tmp1[1]))


    more_info_lst= []
    x = [i.text for i in info]
    for l in range(len(x)):
        more_info_lst.append((x[l].strip().split('\n')))

    address_lst=[]
    y= [a.text for a in addresses]
    for l in range(len(y)):
        fin = " "
        tmp = y[l].strip().split('\n')
        for r in tmp:
            fin += (r.strip() + " ")
        address_lst.append(fin)

    property_type_lst= []
    for c in all_property_type:
        property_type_lst.append(c.text)


    property_price_lst= []
    for c in all_property_price:
        property_price_lst.append(c.text)

    id_lst=[]
    for r in range(len(info)):
        id_lst.append(r)


    join = list(map(lambda x,y,z,p:(x,y,z,p),property_type_lst,property_price_lst, address_lst, more_info_lst))
    for c in join:
        prop_type= c[0]
        prop_price= c[1]
        prop_add= c[2]
        prop_info= str(c[3])
        insert = (None, prop_type, prop_price, prop_add, prop_info)
        statement= "INSERT INTO Buy VALUES (?, ?, ?, ?, ?) "
        cur.execute(statement, insert)
        conn.commit()

tmp_len_rent= []
def get_property_data_rent(command):
    baseurl= 'https://www.realtor.com/'
    rent= baseurl + 'apartments/' + command
    rent_page_text = make_request_using_cache(rent)
    rent_page_soup = BeautifulSoup(rent_page_text, 'html.parser')


    content_div = rent_page_soup.find(class_='srp-list')
    # content_div = rent_page_soup.find(class_='photo-overlay')
    all_property_type_rent= content_div.find_all(class_='property-type')
    all_property_price_rent= content_div.find_all(class_='data-price')
    all_property_beds_rent= content_div.find_all(class_='data-value meta-beds-display')
    info_rent= content_div.find_all(class_='prop-meta ellipsis')
    addresses_rent= content_div.find_all(class_='address ellipsis')
    total_prop_rent= content_div.find(class_='srp-footer-found-listing')
    print(total_prop_rent.string + ' for rent')
    tmp= total_prop_rent.string.split(' ')
    tmp_len_rent.append(int(tmp[1]))
    # print(len_rent_lst)

    rent_more_info_lst= []
    x_rent = [i.text for i in info_rent]
    for l in range(len(x_rent)):
        rent_more_info_lst.append((x_rent[l].strip().split('\n')))

    rent_address_lst=[]
    y_rent= [a.text for a in addresses_rent]
    for l in range(len(y_rent)):
        fin_rent = " "
        tmp_rent = y_rent[l].strip().split('\n')
        for r in tmp_rent:
            fin_rent += (r.strip() + " ")
        rent_address_lst.append(fin_rent)

    rent_property_type_lst= []
    for c in all_property_type_rent:
        rent_property_type_lst.append(c.text)


    rent_property_price_lst= []
    for c in all_property_price_rent:
        rent_property_price_lst.append(c.text)

    rent_id_lst=[]
    for r in range(len(info_rent)):
        rent_id_lst.append(r)


    join_rent = list(map(lambda x,y,z,p:(x,y,z,p),rent_property_type_lst,rent_property_price_lst, rent_address_lst, rent_more_info_lst))
    for c in join_rent:
        prop_type_rent= c[0]
        prop_price_rent= c[1]
        prop_add_rent= c[2]
        prop_info_rent= str(c[3])
        insert_rent = (None, prop_type_rent, prop_price_rent, prop_add_rent, prop_info_rent)
        statement_rent= "INSERT INTO Rent VALUES (?, ?, ?, ?, ?) "
        cur.execute(statement_rent, insert_rent)
        conn.commit()


def process_buy():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print('Sorry. There was an error.')

    buy_results= []
    buy= 'SELECT Id, Type, Price, Address, MoreInfo FROM Buy'
    cur.execute(buy)
    conn.commit()
    for row in cur:
        buy_results.append(row)

    return buy_results

def process_rent():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print('Sorry. There was an error.')

    rent_results= []
    rent= 'SELECT Id, Type, Price, Address, MoreInfo FROM Rent'

    cur.execute(rent)
    conn.commit()
    for row in cur:
        rent_results.append(row)

    return rent_results

def data_graphs(len_buy, len_rent, prices_buy, prices_rent, buy_percent, rent_percent):

    data = [go.Bar(
            x=['FOR SALE', 'FOR RENT'],
            y=[len_buy, len_rent]
    )]
    py.offline.plot(data, filename='basic-bar.html')


    buy_x_axis = list(range(len_buy))
    buy_y_axis = prices_buy
    trace = go.Scatter(
        x = buy_x_axis,
        y = buy_y_axis,
        mode = 'markers'
    )
    data = [trace]
    py.offline.plot(data, filename='basic-scatter_buy.html')


    rent_x_axis = list(range(len_rent))
    rent_y_axis = prices_rent
    trace = go.Scatter(
        x = rent_x_axis,
        y = rent_y_axis,
        mode = 'markers'
    )
    data = [trace]
    py.offline.plot(data, filename='basic-scatter_rent.html')


    labels = ['Buy','Rent']
    values = [buy_percent,rent_percent]
    trace = go.Pie(labels=labels, values=values)
    py.offline.plot([trace], filename='basic_pie_chart.html')

def load_help_text():
    with open('help.txt') as f:
        return f.read()

if __name__== "__main__":
    command= ''
    help_text = load_help_text()
    # command= input('Enter your zip code followed by buy or rent or help for more options: ')
    # zip_code= command.split(' ')[0]
    # data= command.split(' ')[1]
    # get_property_data(zip_code)
    while command != 'exit':
        command = input('Enter your zip code followed by buy or rent or help for more options: ')
        if ' ' in command:
            try:
                zip_code= command.split(' ')[0]
                data= command.split(' ')[1]
                get_property_data_buy(zip_code)
                get_property_data_rent(zip_code)
                if data == "buy":
                    for c in process_buy():
                        print(str(c[0])+ ': ' + str(c[1]) + ' '+ str(c[2])+ ' ' + str(c[3]))

                elif data == "rent":
                    for c in process_rent():
                        print(str(c[0])+ ': ' + str(c[1]) + ' '+ str(c[2])+ ' ' + str(c[3]))
            except:
                print('Command not recognized')

        elif ' ' not in command:
            if command == 'help':
                print(help_text)
                continue
            elif command == 'plot':

                len_buy= tmp_len_buy[0]
                len_rent= tmp_len_rent[0]

                prices_buy= []
                statement_prices_buy= cur.execute('SELECT Price FROM Buy')
                for row in statement_prices_buy:
                    prices_buy.append(row[0])
                prices_rent= []
                statement_prices_rent= cur.execute('SELECT Price FROM Rent')
                for row in statement_prices_rent:
                    prices_rent.append(row[0])
                total= len_buy + len_rent
                buy_percent= float(len_buy/total)
                rent_percent=float(len_rent/total)
                data_graphs(len_buy, len_rent, prices_buy, prices_rent, buy_percent, rent_percent)
            elif command == 'exit':
                print('Bye!')
                break
            else:
                try:
                    zip_code= command
                    get_property_data(zip_code)
                except:
                    print('Command not recognized')
