import requests
import json
import codecs
from bs4 import BeautifulSoup
import re

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

href_host = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/'

r = requests.get('http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html', headers=headers)
r.encoding = 'gb2312'
soup = BeautifulSoup(r.text, 'html.parser')

# print(soup.title)

# 省provincetr
# 市citytr
# 区countytr
province_list = soup.select('tr.provincetr > td > a')

data = {}
data['provinces'] = []

for p in province_list:
    # 市
    # data['provinces'].append(p.contents[0])

    city_request = requests.get(href_host + p['href'], headers=headers)
    city_soup = BeautifulSoup(city_request.text.encode(city_request.encoding).decode('gbk'), 'html.parser')
    city_list = city_soup.select('tr.citytr')
    city_data = {}
    city_data['cities'] = []
    for c in city_list:

        city_html = c.contents
        # td > a > text
        try:
            city_html_number = city_html[0].contents[0].contents[0]
        except AttributeError:
            city_html_number = city_html[0].contents[0]
        try:
            city_html_name = city_html[1].contents[0].contents[0]
            city_href = city_html[1].contents[0]['href']
        except AttributeError:
            city_html_name = city_html[1].contents[0]

        city_obj = {}
        city_obj['cityName'] = city_html_name
        city_obj['cityNumber'] = city_html_number

        city_data['provinceName'] = p.contents[0]
        city_data['cities'].append(city_obj)

    print(city_data)
    data['provinces'].append(city_data)

# D:\\SVNRepo\\JZWealth\\app\\src\\main\\assets\\provinces.json
with codecs.open('provinces.json', 'w') as f_obj:
    # 如果以utf8格式输出，ensure_ascii应该为false
    json.dump(data, f_obj, ensure_ascii=False)



