# 抓取省、市、区数据

import requests
import json
import codecs
from bs4 import BeautifulSoup
import re


def crawler_country(c, country_list):
    country_data = {}
    country_data['countries'] = []
    for country in country_list:
        if not re.match('[\\d]+', country.contents[0]):
            country_data['cityName'] = c.contents[0]
            country_data['countries'].append(country.contents[0])
    return country_data


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
    city_request = requests.get(href_host + p['href'], headers=headers)
    # city_request.encoding = 'gb2312'
    city_soup = BeautifulSoup(city_request.text.encode(city_request.encoding).decode('gbk'), 'html.parser')
    city_list = city_soup.select('tr.citytr')
    city_data = {}
    city_data['cities'] = []
    for c in city_list:
        city_data['provinceName'] = p.contents[0]

        city_html = c.contents
        # td > a > text
        try:
            city_html_number = city_html[0].contents[0].contents[0]
        except AttributeError:
            city_html_number = city_html[0].contents[0]

        try:
            tmp_city_html_name = city_html[1].contents[0].contents[0]
            city_href = city_html[1].contents[0]['href']
        except AttributeError:
            tmp_city_html_name = city_html[1].contents[0]

        # 将市辖区改成直辖市名称
        city_html_name = ''
        if tmp_city_html_name == '市辖区':
            city_html_name = p.contents[0][0:-1]
        else:
            city_html_name = tmp_city_html_name
        country_data = {}
        country_data['countries'] = []

        country_request = requests.get(href_host + city_href, headers=headers)
        country_soup = BeautifulSoup(country_request.text.encode(country_request.encoding).decode('gbk'), 'html.parser')
        country_list = country_soup.select('tr.countytr')
        for country in country_list:
            country_data['cityName'] = city_html_name
            country_data['cityNumber'] = city_html_number

            country_obj = {}
            country_tmp = country.contents
            try:
                country_html_number = country_tmp[0].contents[0].contents[0]
            except AttributeError:
                country_html_number = country_tmp[0].contents[0]
            try:
                country_html_name = country_tmp[1].contents[0].contents[0]
            except AttributeError:
                country_html_name = country_tmp[1].contents[0]
            country_obj['countryName'] = country_html_name
            country_obj['countryNumber'] = country_html_number
            country_data['countries'].append(country_obj)
        if not country_data['countries']:
            country_list = country_soup.select('tr.towntr')
            for country in country_list:
                country_data['cityName'] = city_html_name
                country_data['cityNumber'] = city_html_number

                country_obj = {}
                country_tmp = country.contents
                try:
                    country_html_number = country_tmp[0].contents[0].contents[0]
                except AttributeError:
                    country_html_number = country_tmp[0].contents[0]
                try:
                    country_html_name = country_tmp[1].contents[0].contents[0]
                except AttributeError:
                    country_html_name = country_tmp[1].contents[0]
                country_obj['countryName'] = country_html_name
                country_obj['countryNumber'] = country_html_number
                country_data['countries'].append(country_obj)
        print(country_data)
        city_data['cities'].append(country_data)
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

with codecs.open('countries.json', 'w') as f_obj:
    # 如果以utf8格式输出，ensure_ascii应该为True
    json.dump(data, f_obj, ensure_ascii=True)




