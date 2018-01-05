import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import urllib2, json
import datetime as dt
from datetime import date, timedelta
import sys
import os
from subprocess import Popen, PIPE

# Create the URL
logs = []
url = "http://www.christies.com/calendar/"
name_n_sales_offline = '//SAPDATA01/SAPFS/Automation_Anywhere/Projects/Christies/Control_files/n_sales_offline.txt'

# Read the excel spreadsheet of sale calendar
file_name_offline   = '//SAPDATA01/SAPFS/Automation_Anywhere/Projects/Christies/Control_files/OFFLINE_SALE_LIST.xlsx'
file_name_online    = '//SAPDATA01/SAPFS/Automation_Anywhere/Projects/Christies/Control_files/ONLINE_SALE_LIST.csv'
file_name_new_sales = '//SAPDATA01/SAPFS/Automation_Anywhere/Projects/Christies/Control_files/OFFLINE_NEW_SALE_LIST.csv'
file_name_tomorrow_sales = '//SAPDATA01/SAPFS/Automation_Anywhere/Projects/Christies/Control_files/OFFLINE_TOMORROW_SALE_LIST.csv'
# file_name_yesterday_sales = '//SAPDATA01/SAPFS/Automation_Anywhere/Projects/Christies/Control_files/OFFLINE_YESTERDAY_SALE_LIST.csv'
# sales = pd.read_excel(file_name, sheetname = 'SALELIST')
# sales = pd.read_csv(file_name_offline)
sales = pd.read_excel(file_name_offline)
# Read the Page
page = urllib2.urlopen(url)
soup = BeautifulSoup(page, 'html.parser')
i = 0

A=[]
B=[]
C=[]
D=[]
E=[]

cols = ['sale_no', 'sale_loc', 'url', 'start', 'end', 'sale_id']
new_sales = pd.DataFrame()
tomorrow_sales = pd.DataFrame()

for div in soup.find_all('div', attrs={'class' : 'chr-result-block-inner clearfix'}):
    div.prettify()
# URL
    URL = str((div.find('a', class_ = 'chr-sale-lot-link').get('href'))).strip()
    if URL <> 'None':
        D.append(div.find('a', class_ = 'chr-sale-lot-link').get('href'))
# Name
        A.append(div.find('h3', class_ = 'chr-result-hd').text)
# Sale Location
        loc = str(div.find('h4', class_ = 'chr-result-hd-loc').string)
        loc = loc.strip()
        if loc == 'None':
            loc = 'Online'
        B.append(loc)
# Sale Number
        no = str((div.find('li', class_ = 'chr-sale-lot-info first').text.split(" ")[1]))
        no = no.strip()
        C.append(int(no))
# Strip out internal sale ID for non-online sales

        if loc <> 'Online':
            id = str((div.find('a', class_ = 'chr-sale-lot-link').get('href')))
            id = id.strip()
#             date = id

            if id <> "None":
                id = id.split("=")[2]
                id = id[:5].strip()
            else:
                id = " "
            E.append(id)
        else:
            id = str((div.find('a', class_ = 'chr-sale-lot-link').get('href')))
            id = id.strip()
            if id <> "None":
                id = id.split("=")[2]
                id = id.split("&")[0]
            else:
                id = " "
            E.append(id)


# Create a DataFrame
out=pd.DataFrame(B,columns=['sale_loc'])
out['sale_no'] = C
out['URL'] = D
out['sale_id'] = E

tomorrow = (date.today() + timedelta(1)).strftime("%Y%m%d")

for index, row2 in sales.iterrows():
    if row2.start == tomorrow:
        df_t = pd.DataFrame(columns=cols, index=range(1))
        for a in range(1):
            df_t.loc[a].sale_no = row2.sale_no
            df_t.loc[a].sale_loc = row2.sale_loc
            df_t.loc[a].url = row2.url
            df_t.loc[a].sale_id = row2.sale_id
            df_t.loc[a].start = row2.start
            df_t.loc[a].end = row2.end
            tomorrow_sales = tomorrow_sales.append(df_t, ignore_index = True)


logs.append("Following New Sales are being Loaded")
for index, row in out.iterrows():
# Only the sale that are not online.
    if row.sale_loc <> 'Online':
# Check if the sale is already in the table
        if len(sales.loc[sales['sale_no'] == row.sale_no].index) == 0:
# if not add it.
            df2 = pd.DataFrame(columns=cols, index=range(1))
            for a in range(1):
                df2.loc[a].sale_no = row.sale_no
                df2.loc[a].sale_loc = row.sale_loc
                df2.loc[a].url = row.URL
                df2.loc[a].sale_id = row.sale_id
                sales = sales.append(df2, ignore_index = True)
                logs.append(str(row.sale_no) + "-" + row.sale_loc )
                print str(row.sale_no) + "-" + row.sale_loc
# Also create a file with the new sales seprately
                new_sales = new_sales.append(df2, ignore_index = True)


sales.to_excel(file_name_offline, header = True, index = False)
# sales.to_csv(file_name_offline, header = True, index = False)
logs_out=pd.DataFrame(logs,columns=['log'])
# new_sales.to_csv(file_name_new_sales, header = True, index = False)
logs_out.to_csv(name_n_sales_offline, header = False, index = False)
# tomorrow_sales.to_csv(file_name_tomorrow_sales, header = True, index = False)
