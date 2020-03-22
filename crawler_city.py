# 抓取省、市数据

import requests
import json
import codecs
from bs4 import BeautifulSoup


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

href_host = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/'

page_format = 'gb18030'

r = requests.get('http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html', headers=headers)
r.encoding = page_format
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
    city_request.encoding = page_format
    city_soup = BeautifulSoup(city_request.text.encode(city_request.encoding).decode(page_format), 'html.parser')
    city_list = city_soup.select('tr.citytr')
    city_data = {}
    city_data['cities'] = []
    for c in city_list:
        city_html = c.contents
        try:
            city_html_number = city_html[0].contents[0].contents[0]
        except AttributeError:
            city_html_number = city_html[0].contents[0]
        try:
            city_html_name = city_html[1].contents[0].contents[0]
            city_href = city_html[1].contents[0]['href']
        except AttributeError:
            city_html_name = city_html[1].contents[0]

        # 将市辖区改成直辖市名称
        city_obj = {}
        if city_html_name == '市辖区':
            city_obj['cityName'] = p.contents[0][0:-1]
        else:
            city_obj['cityName'] = city_html_name
        city_obj['cityNumber'] = city_html_number

        # 将重庆市的县对应的地区归整到重庆市市辖区
        city_data['provinceName'] = p.contents[0]
        if p.contents[0] == '重庆市' and city_obj['cityName'] == '县':
            break
        else:
            city_data['cities'].append(city_obj)

    print(city_data)
    data['provinces'].append(city_data)

# 手动添加的台湾和香港地区数据，如果不需要可以注释掉
taiwan = {}
taiwan['provinceName'] = '台湾省'
taiwan['cities'] = []
t = {"cityName": "台北市", "cityNumber": "taiwan01"}
taiwan['cities'].append(t)
t = {"cityName": "新北市", "cityNumber": "taiwan02"}
taiwan['cities'].append(t)
t = {"cityName": "桃园市", "cityNumber": "taiwan03"}
taiwan['cities'].append(t)
t = {"cityName": "台中市", "cityNumber": "taiwan04"}
taiwan['cities'].append(t)
t = {"cityName": "台南市", "cityNumber": "taiwan05"}
taiwan['cities'].append(t)
t = {"cityName": "高雄市", "cityNumber": "taiwan06"}
taiwan['cities'].append(t)
data['provinces'].append(taiwan)

hk = {}
hk['provinceName'] = '香港'
hk['cities'] = []
t = {"cityName": "香港", "cityNumber": "hk01"}
hk['cities'].append(t)
data['provinces'].append(hk)

aomen = {}
aomen['provinceName'] = '澳门'
aomen['cities'] = []
t = {"cityName": "澳门", "cityNumber": "aomen01"}
aomen['cities'].append(t)
data['provinces'].append(aomen)

# D:\\SVNRepo\\JZWealth\\app\\src\\main\\assets\\provinces.json
with codecs.open('provinces.json', 'w') as f_obj:
    # 如果以utf8格式输出，ensure_ascii应该为True
    json.dump(data, f_obj, ensure_ascii=False)



